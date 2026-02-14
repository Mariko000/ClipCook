from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# .conversion_data は仮のインポート
from .conversion_data import unitConversion, ingredientConversion, synonyms, jp_to_en, en_to_jp
import re
from fractions import Fraction
import traceback 

# ------------------------
# 定数 / マップ (Constants / Maps)
# ------------------------

# Unicode分数マップ（表示→ASCII分数）
UNICODE_FRACTIONS = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4",
    "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5",
    "⅙": "1/6", "⅚": "5/6", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}
# Unicode分数文字セット (混合数対応のために正規表現で使用)
_UNICODE_FRACTIONS_SET = "".join(UNICODE_FRACTIONS.keys())

# 非換算（量を数値化できない）ユニットセット（小文字）
NON_MEASURE_UNITS = {"pinch", "dash", "handful", "stick", "clove", "slice", "sprig", "to taste", "適量"} 

# 単位別エイリアス（略語・複数形含む）
UNIT_ALIASES = {
    "c": "cup", "cup": "cup", "cups": "cup",
    "tbsp": "tbsp", "tbs": "tbsp", "T": "tbsp", "Tbs": "tbsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp",
    "tsp": "tsp", "t": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    # 日本の単位を US の単位系にマッピング
    "大さじ": "tbsp", 
    "小さじ": "tsp",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "fl oz": "fl oz", "fluid ounce": "fl oz", "fluid ounces": "fl oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "g": "g", "gram": "g", "grams": "g", 
    "kg": "kg", "kilogram": "kg", "kilograms": "kg", 
    "ml": "ml", "milliliter": "ml", "milliliters": "ml",
    "l": "l", "liter": "l", "liters": "l",
    # 日本語の数量単位を追加
    "個": "個", "piece": "個", "pieces": "個", 
    "丁": "個", # 豆腐などの単位を '個' に統一
    "本": "個", # 野菜などの単位を '個' に統一
    "medium": "medium", "large": "large", "small": "small",
    "stick": "stick", "handful": "handful", "sprig": "sprig",
}

# unit regex (長いキーを先に評価するためソート)
# re.escape は正規表現の特殊文字をエスケープするために必須
_UNIT_PATTERN = re.compile(r"\b(" + "|".join(sorted(map(re.escape, UNIT_ALIASES.keys()), key=lambda x: -len(x))) + r")\b", flags=re.I)

# コメント内の重量・体積パターン (例: (352 grams))
GRAMS_OR_ML_IN_COMMENT_PATTERN = re.compile(
    r'\(\s*(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+)\s*(grams?|g|milliliters?|ml)\s*\)', re.IGNORECASE
)

# ingredientConversionのキーを長さ降順でソートしたリスト (汎用名抽出用)
_SORTED_ING_KEYS = sorted(ingredientConversion.keys(), key=lambda x: -len(x))


# ------------------------
# ユーティリティ関数 (Utility Functions)
# ------------------------

def _preprocess_unicode_fractions(s: str) -> str:
    """
    Unicode分数を標準の 1/2 形式に変換し、混合数に対応するスペースを挿入
    例: "2¼" -> "2 1/4"
    """
    # 1. 数字の直後にUnicode分数がある場合、間にスペースを挿入 (混合数対応)
    s = re.sub(r'(\d)([' + re.escape(_UNICODE_FRACTIONS_SET) + r'])', r'\1 \2', s)

    # 2. Unicode分数をASCII分数に変換
    for k, v in UNICODE_FRACTIONS.items():
        s = s.replace(k, v)
    return s


def parse_amount(amount_str):
    """ '1 3/4' → 1.75, '3/4' -> 0.75, '2.5' -> 2.5 """
    try:
        amount_str = amount_str.strip()
        if not amount_str:
            return None
        
        # 混合数 (例: "1 3/4" または "1 と 1/2") の処理
        amount_str = amount_str.replace('と', ' ')
        
        if ' ' in amount_str:
            parts = amount_str.split(' ', 1)
            # parts[0] が整数であることを確認
            if parts[0].isdigit() or (parts[0].startswith('-') and parts[0][1:].isdigit()):
                whole_str = parts[0]
                frac_str = parts[1]
                
                # 分数が有効な形式であるかチェック（例: '1/2'）
                if '/' in frac_str and frac_str.replace('/', '', 1).isdigit():
                    whole = float(Fraction(whole_str)) 
                    frac = float(Fraction(frac_str))
                    
                    return whole + frac
            
        # 単一の数値または分数 (例: "1.75" または "3/4")
        return float(Fraction(amount_str))
        
    except (ValueError, ZeroDivisionError):
        return None

def _find_unit_in_text(text: str):
    """テキスト中から unit を見つけ canonical unit を返す（なければ None）。"""
    if not text:
        return None
    
    m = _UNIT_PATTERN.search(text)
    if not m:
        return None
    raw_token = m.group(0)
    canonical = UNIT_ALIASES.get(raw_token.lower(), raw_token.lower())
    return raw_token, canonical 


def tokenize_line(line: str):
    """
    1 行のレシピテキストをトークン化して返す。
    日本語・英語混在の単位対応（ml, g, l, cc, 個, 大さじ, 小さじ, cup, tbsp, tspなど）
    Unicode分数・混合数・範囲・コメントにも対応。
    """
    if not line:
        return {"raw": line, "amount": None, "unit": None, "ingredient": "", "comment": ""}

    original = line.strip()

    # --- 括弧内コメント抽出 ---
    comments = []
    def _paren_repl(m):
        comments.append(m.group(1).strip())
        return " "
    without_paren = re.sub(r"\((.*?)\)", _paren_repl, original)

    # ★修正1: 日本語混合数対応のための前処理
    # 例: "大さじ 1と1/2" -> "大さじ 1 1/2"
    pre = re.sub(
        r"(\d+)\s*と\s*(\d+/\d+|[" + re.escape(_UNICODE_FRACTIONS_SET) + r"])",
        r"\1 \2", without_paren
    )

    # --- Unicode分数・混合数対応 ---
    pre = _preprocess_unicode_fractions(pre)


    # --- 数量検出（範囲対応）---
    amount_pattern = re.compile(
        r"(\d+\s+\d+/\d+|\d+\/\d+|\d+\.\d+|\d+)"
        r"(?:\s*[-–]\s*(\d+\s+\d+/\d+|\d+\/\d+|\d+\.\d+|\d+))?"
    )
    m_amount = amount_pattern.search(pre)
    amount = None
    amount_token = None
    if m_amount:
        amount_token = m_amount.group(0)
        if m_amount.group(2):
            start_amount = parse_amount(m_amount.group(1))
            end_amount = parse_amount(m_amount.group(2))
            if start_amount is not None and end_amount is not None:
                amount = (start_amount + end_amount) / 2
        else:
            amount = parse_amount(m_amount.group(1))

    # --- 単位検出 ---
    unit = None
    raw_unit_token = None

    # 数値の直後からまず探す
    if m_amount:
        unit_search_text = pre[m_amount.end():]
        unit_result = _find_unit_in_text(unit_search_text)
    else:
        unit_result = _find_unit_in_text(pre)

    # 見つからない場合は全体から再検索
    if not unit_result:
        unit_result = _find_unit_in_text(pre)

    # 結果が得られたら canonical に正規化
    if unit_result:
        raw_unit_token, unit = unit_result
        unit = UNIT_ALIASES.get(unit.lower(), unit.lower())

    # --- 材料名の抽出 ---
    cleaned = pre
    
    # 数量と単位が検出された場合は、そのトークンを削除
    if amount_token or raw_unit_token:
        # 量と単位を結合したトークンがあればそれを削除
        full_token_parts = [amount_token, raw_unit_token]
        # 空でないトークンをスペースで結合
        full_token = " ".join(part.strip() for part in full_token_parts if part)

        if full_token:
            # 正規表現を使って、量+単位のパターンを検索し削除（厳密な文字列一致よりも安全）
            pattern_to_remove = re.escape(amount_token) + r'\s*' + (re.escape(raw_unit_token) if raw_unit_token else '')
            cleaned = re.sub(pattern_to_remove, ' ', cleaned, count=1, flags=re.I)
        elif amount_token:
             cleaned = cleaned.replace(amount_token, " ", 1)
        elif raw_unit_token:
             cleaned = cleaned.replace(raw_unit_token, " ", 1)


    # 不要語句除去
    cleaned = re.sub(
        r"\b(of|approximately|approx|about|to serve|for frying|for dusting|plus|plus extra|or to taste|extra|free-range|ripe)\b",
        " ", cleaned, flags=re.I
    )
    
    # ★修正2: 単位として処理された '丁' '本' などの日本語単位を食材名から確実に削除
    if unit in ("個", "tbsp", "tsp", "cup", "oz", "g", "ml"):
        for jp_unit in ["丁", "本"]:
            cleaned = cleaned.replace(jp_unit, " ")


    # コメント（カンマなどで分割）
    parts = re.split(r",|\s-\s|\s—\s", cleaned, maxsplit=1)
    ingredient_name = parts[0].strip()
    if not ingredient_name:
        ingredient_name = cleaned.strip()
    if len(parts) > 1:
        comments.append(parts[1].strip())

    comment = "; ".join([c for c in comments if c])

    # --- 最後のフォールバック ---
    # 数量あり・単位なしの場合 → 単位を ingredient_name から再抽出
    if amount is not None and unit is None:
        unit_result_fallback = _find_unit_in_text(ingredient_name)
        if unit_result_fallback:
            raw_unit_token_fallback, unit_fallback = unit_result_fallback
            unit = UNIT_ALIASES.get(unit_fallback.lower(), unit_fallback.lower())
            ingredient_name = ingredient_name.replace(raw_unit_token_fallback, " ", 1).strip()
        else:
            # 単位なしで数量が検出された場合、デフォルトで '個' に設定 (例: りんご 1)
            unit = "個" 

    # 特定の単語が単位扱いされた場合、個に正規化 (ただし、既に '個' に正規化されているため不要だが残す)
    if unit in ("lemon", "lime", "onion", "apple", "pie crust", "egg"):
        unit = "個"

    # --- 出力 ---
    return {
        "raw": original,
        "amount": amount,
        "unit": unit,
        # 連続するスペースを除去
        "ingredient": re.sub(r"\s+", " ", ingredient_name).strip(),
        "comment": re.sub(r"\s+", " ", comment).strip(),
    }


def normalize_ingredient(name: str) -> str:
    """食材名を正規化（前回のロジックを維持）"""
    n = name.strip().lower()

    if n in ingredientConversion:
        return n

    if n in synonyms:
        canonical = synonyms[n]
        if canonical in ingredientConversion:
            return canonical
        return canonical 

    for key in ingredientConversion.keys():
        if re.search(r"\b" + re.escape(key) + r"\b", n):
            return key
            
    return n


# ------------------------
# 換算ロジック (Conversion Logic)
# ------------------------


# --- 1. 外国単位 → g/ml への順変換 ---
def convert_to_g_ml(ingredient, amount, unit, from_system="us", skip_us_round=False):
    """
    US/UK単位 → g/ml または個数に換算
    ★修正: 固形物であっても容積単位からの換算を優先的に行う
    """
    if amount is None or unit is None:
        return amount, unit
        
    ing_name = normalize_ingredient(ingredient)
    data = ingredientConversion.get(ing_name, {})

    form = data.get("form", "solid")  # solid/liquid/unit
    conv = data.get(from_system, {})  # ingredientConversion 内の単位換算値

    current_unit = unit
    if current_unit == "oz":
        current_unit = "fl oz" if form == "liquid" else "oz"

    # 1. 個数単位 (unit フォーム)
    if form == "unit":
        # 個数単位は換算しない
        return amount, "個"

    # ★修正3: 容積単位 (cup/tbsp/tsp) から重量 (g/ml) への変換
    # 固形物(form=="solid")であっても、ingredientConversion に換算データがあればそれを使う（最も正確）
    if current_unit in conv: 
        factor = conv[current_unit]
        target_unit = "g" if form == "solid" else "ml"
        return round(amount * factor, 1), target_unit
    
    # 2. 汎用液体・容積単位のフォールバック (unitConversion の体積換算値を使用)
    # ingredientConversion にデータがないが、液量として扱える場合
    if form == "liquid" and current_unit in ("cup", "tbsp", "tsp", "fl oz", "l"):
        factor = unitConversion.get(from_system, {}).get(current_unit)
        if factor:
            return round(amount * factor, 1), "ml"

    # 3. 換算データがない場合、元の値と単位をそのまま返す
    return amount, unit


# ------------------------
# --- 2. g/ml → US単位 への逆変換  ---
# ------------------------

def convert_to_us_units(ingredient, amount, unit, form="solid"):
    """
    g/ml を US単位 (cup, fl oz, oz, tbsp, tsp) に換算する。
    材料分類と分数丸め入り。
    """
    if unit not in ("g", "ml"):
        return amount, unit

    ing_name = normalize_ingredient(ingredient)
    data = ingredientConversion.get(ing_name, {})
    form = data.get("form", "solid")  # solid/liquid/unit

    us_factors = unitConversion.get("us", {})
    
    # 液体 (ml → cup/fl oz/tbsp/tsp)
    if unit == "ml" or form == "liquid":
        ml_amount = amount 
        
        # us_factors から値を取得
        fl_oz_val = us_factors.get("fl oz", 29.57) 
        cup_val = us_factors.get("cup", 236.59) 
        tbsp_val = us_factors.get("tbsp", 14.79) 
        tsp_val = us_factors.get("tsp", 4.93)   

        # 1. cup (1/2 cup = 118ml 以上)
        cups = ml_amount / cup_val
        if cups >= 0.5:
            return round_fraction(cups, 8), "cup"

        # 2. fl oz (1 fl oz = 29.57ml 以上)
        fl_oz = ml_amount / fl_oz_val
        if fl_oz >= 1:
            return round(fl_oz, 1), "fl oz"

        # 3. tbsp → tsp
        tbsp = ml_amount / tbsp_val
        if tbsp >= 1:
            return round_fraction(tbsp, 2), "tbsp"

        tsp = ml_amount / tsp_val
        if tsp >= 0.5:
            return round_fraction(tsp, 2), "tsp"

        return ml_amount, "ml" 

    # 固体 (g → oz/tbsp/tsp)
    if form == "solid" and unit == "g":
        # 少量の固形物 (15g以下) は g のまま維持
        if amount <= 15:
            # 例外的な食材リストがあればここで処理するが、今回は g を維持
            # わかめ 5g はここで g のまま維持される
            return round(amount, 1), "g" 

        # 15gを超える固形物は oz に変換
        oz_val = us_factors.get("oz", 28.35)
        return round(amount / oz_val, 1), "oz"


    # 卵・果物・野菜 (unit フォーム)
    if form == "unit" and unit == "g":
        unit_weight = data.get("unit_weight", 60)
        units = amount / unit_weight
        return round(units, 1), "個"

    # その他固形物
    if form == "solid" and unit == "g":
        oz_factor = us_factors.get("oz")
        return round(amount / oz_factor, 1), "oz"

    return amount, unit


# ----------------------- ------------------------
#  US単位→ g/ml  への変換のときの丸めるロジック
# ------------------------ ------------------------


def humanize(a, u, f):
    """換算後の量を整形する"""
    if a is None:
        return None
    # g/ml は100以上なら整数、それ以外は小数点第1位
    if u=="g" or u=="ml":
        if a >= 100 and a % 1 == 0:
             return int(a) 
        if a >= 100:
            return int(round(a, 1))
        return round(a, 1)
    
    # 個数は端数を残す
    if u=="個" or u in ("small", "medium", "large"):
        if isinstance(a, str) and '/' in a:
            a = float(Fraction(a))
        return round(a, 2)
    
    # その他の単位は文字列（分数表現）の場合はそのまま返す
    if isinstance(a, str):
        return a

    # その他の単位は小数点第1位
    return round(a, 1)


def round_fraction(value, max_denominator=8):
    """
    cup/tbsp/tsp 用の分数丸め
    """
    if value is None:
        return None
        
    frac = Fraction(round(value, 4)).limit_denominator(max_denominator)
    
    if frac.denominator == 1:
        return frac.numerator
    
    whole = int(frac)
    remainder = frac - whole
    
    if whole == 0:
        if remainder.numerator == 0:
            return 0
        return f"{remainder.numerator}/{remainder.denominator}"
    else:
        if remainder.numerator == 0:
            return whole
        # 混合数として返す (例: "2 1/2")
        return f"{whole} {remainder.numerator}/{remainder.denominator}"

# ------------------------
# レシピ変換エンドポイント (Recipe Conversion Endpoint)
# ------------------------

@csrf_exempt
def convert_recipe(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        recipe_text = data.get("recipe_text", "")
        from_unit_system = data.get("from_unit_system", "us") 
        to_unit_system = data.get("to_unit_system", "jp")

        lines = [line.strip() for line in recipe_text.splitlines() if line.strip()]
        result = []

        for line in lines:
            tokens = tokenize_line(line)
            amount = tokens.get("amount")
            unit = tokens.get("unit")
            ingredient_name = tokens.get("ingredient")
            comment = tokens.get("comment")

            if ingredient_name.lower() in NON_MEASURE_UNITS:
                result.append({
                    "ingredient": ingredient_name,
                    "comment": comment,
                    "amount": None,
                    "unit": None
                })
                continue
            
            # 1. 換算に使用するキー (英語キーに正規化) を決定
            # ingredient_name は元の言語 (JP/EN) の名前
            ingredient_key_for_conversion = normalize_ingredient(ingredient_name)
            ing_conf = ingredientConversion.get(ingredient_key_for_conversion, {}) or {}
            form = ing_conf.get("form", "solid")

            # 最終的な表示名用の変数を初期化
            ingredient_display_name = ingredient_name 
            
            converted_amount = amount
            converted_unit = unit

            # --- US → JP 変換ロジック（食材名の日本語化を含む） ---
            if to_unit_system == "jp" and amount is not None:
                
                # ★修正4a: US -> JP 変換時、食材名を日本語に変換（最優先は正規化後の英語キーで検索）
                ingredient_display_name = en_to_jp.get(ingredient_key_for_conversion, ingredient_name)
                
                # 特殊な表現のフォールバック処理
                if "mashed banana" in ingredient_key_for_conversion:
                    ingredient_display_name = "バナナ (マッシュ)" 
                
                # US/UKの単位から g/ml に変換
                if unit not in ("g", "ml", "small", "medium", "large", "個"):
                    # チョコチップのような固形物で容積換算が必要な場合も、この関数内で処理される
                    converted_amount, converted_unit = convert_to_g_ml(
                        ingredient_key_for_conversion, 
                        amount, 
                        unit, 
                        from_system=from_unit_system, 
                        skip_us_round=False
                    )

            # --- JP → US/UK 変換ロジック ---
            elif to_unit_system != "jp":
                
                # ★修正4b: JP -> US/UK の場合は、食材名も英語に変換（元の日本語名で検索）
                # 例: "玉ねぎ" -> "onion"
                ingredient_display_name = jp_to_en.get(ingredient_name, ingredient_name)
                # 変換に使用するキーは、日本語名の翻訳後の英語名で再度正規化
                ingredient_en = normalize_ingredient(ingredient_display_name)
                
                if converted_unit in ("g", "ml"):
                    form = ingredientConversion.get(ingredient_en, {}).get("form", "solid")
                    
                    if to_unit_system == "us":
                        converted_amount, converted_unit = convert_to_us_units(
                            ingredient_en, converted_amount, converted_unit, form=form
                        )
                # 個数単位処理
                elif converted_unit == "個":
                    converted_unit = ""
                    # 英語で個数を示す場合、複数形にしたい場合はここでの調整が必要
                    if converted_amount > 1 and not ingredient_display_name.endswith("s"):
                        pass # 現状では複数形化はしない

            final_amount = humanize(converted_amount, converted_unit, form)
            
            # 個数単位処理 (unit の最終的な表示名調整)
            if unit in UNIT_ALIASES and UNIT_ALIASES[unit] == "個":
                # 日本語レシピの個数単位は、変換先単位系に関わらず '個' と表示
                converted_unit = "個" if to_unit_system == "jp" else ""


            # 最終結果の格納: amount, unit が None の場合はコメントを優先して表示
            result.append({
                "ingredient": ingredient_display_name,
                "comment": comment,
                "amount": final_amount,
                "unit": converted_unit
            })

        return JsonResponse({"converted_recipe": result})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=400)
# ------------------------
# API エンドポイント（簡易）
# ------------------------
def unit_conversion_api(request):
    """単位換算データを出力"""
    return JsonResponse(unitConversion)

def ingredient_conversion_api(request):
    """食材別換算データを出力"""
    return JsonResponse(ingredientConversion)
