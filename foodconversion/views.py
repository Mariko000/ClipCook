# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .conversion_data import unitConversion, ingredientConversion
import re
from fractions import Fraction

# ------------------------
# 定数 / マップ
# ------------------------

# Unicode分数マップ（表示→ASCII分数）
UNICODE_FRACTIONS = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4",
    "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5",
    "⅙": "1/6", "⅚": "5/6", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}

# 非換算（量を数値化できない）ユニットセット（小文字）
NON_MEASURE_UNITS = {"pinch", "dash", "handful", "stick", "clove", "slice", "sprig", "to taste"}

# 単位別エイリアス（略語・複数形含む）
UNIT_ALIASES = {
    "c": "cup", "cup": "cup", "cups": "cup",
    "tbsp": "tbsp", "tbs": "tbsp", "T": "tbsp", "Tbs": "tbsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp",
    "tsp": "tsp", "t": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "g": "g", "kg": "kg", "ml": "ml", "l": "l",
    "pinch": "pinch", "dash": "dash", "clove": "clove", "slice": "slice",
    "個": "個", "medium": "medium", "large": "large", "small": "small",
    "stick": "stick", "handful": "handful", "sprig": "sprig"
}

# unit regex (長いキーを先に評価するためソート)
_UNIT_PATTERN = re.compile(r"\b(" + "|".join(sorted(map(re.escape, UNIT_ALIASES.keys()), key=lambda x: -len(x))) + r")\b", flags=re.I)

# ------------------------
# ユーティリティ関数
# ------------------------

def _preprocess_unicode_fractions(s: str) -> str:
    """Unicode分数を標準の 1/2 形式に変換"""
    unicode_map = {
        "½": "1/2", "⅓": "1/3", "⅔": "2/3",
        "¼": "1/4", "¾": "3/4",
        "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5",
        "⅙": "1/6", "⅚": "5/6",
        "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
    }
    for k, v in unicode_map.items():
        s = s.replace(k, v)
    return s


# --- replace existing parse_amount and tokenize_line with this code ---

def parse_amount(text: str):
    """
    レシピ量テキストを float に変換。
    - Unicode分数（½等）は事前に 1/2 に置換
    - "1 1/2" -> 1.5
    - "1/2-1" / "1–2" のような範囲 -> 各端を解析して平均値を返す
    """
    if not text:
        return None

    s = str(text).strip()

    # Unicode分数を ASCII 表現に
    for uni, frac in UNICODE_FRACTIONS.items():
        # 例: "2½" -> "2 1/2"
        s = re.sub(r"(\d)"+re.escape(uni), r"\1 " + frac, s)
    for uni, frac in UNICODE_FRACTIONS.items():
        s = s.replace(uni, frac)

    # 範囲表記対応（ハイフン '-' とエンダッシュ '–' を考慮）
    if re.search(r'[-–]', s):
        parts = [p.strip() for p in re.split(r'[-–]', s) if p.strip()]
        values = []
        for p in parts:
            v = parse_amount(p)  # 再帰的に端を解析
            if v is not None:
                values.append(v)
        if values:
            return sum(values) / len(values)
        return None

    # "整数 分数" の形 (例: "1 2/3")
    m = re.match(r'^\s*(\d+)\s+(\d+/\d+)\s*$', s)
    if m:
        integer = int(m.group(1))
        frac = float(Fraction(m.group(2)))
        return integer + frac

    # 単独分数 "2/3"
    m = re.match(r'^\s*(\d+/\d+)\s*$', s)
    if m:
        return float(Fraction(m.group(1)))

    # 小数または整数 "2.5" / "3"
    m = re.match(r'^\s*(\d+(?:\.\d+)?)\s*$', s)
    if m:
        try:
            return float(m.group(1))
        except:
            return None

    # 混合トークン（例: "1 1/2" を split して合算できる汎用処理）
    try:
        parts = s.split()
        total = 0.0
        for p in parts:
            total += float(Fraction(p))
        return total if total != 0 else None
    except Exception:
        # 最後の手段: 数字部分だけ抽出して parse
        m_num = re.search(r'(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+)', s)
        if m_num:
            return parse_amount(m_num.group(0))
        return None


def tokenize_line(line: str):
    """
    1 行のレシピテキストをトークン化して返す。
    - Unicode分数対応
    - 数量・範囲対応
    - 単位正規化
    - ingredientConversion の form に応じて oz → oz/fl oz 自動マッピング
    """
    if not line:
        return {"raw": line, "amount": None, "unit": None, "ingredient": "", "comment": ""}

    original = line.strip()

    # 括弧内はコメントへ移す（複数ある場合は連結）
    comments = []
    def _paren_repl(m):
        comments.append(m.group(1).strip())
        return " "
    without_paren = re.sub(r"\((.*?)\)", _paren_repl, original)

    pre = _preprocess_unicode_fractions(without_paren)

    # 数量検出（範囲対応）
    amount_pattern = re.compile(
        r"(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+)"   # 単一数値または分数
        r"(?:\s*[-–]\s*(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+))?"  # 範囲
    )
    m_amount = amount_pattern.search(pre)
    amount = None
    amount_token = None
    if m_amount:
        if m_amount.group(2):
            # 範囲表記あり
            amount_token = m_amount.group(0)
        else:
            amount_token = m_amount.group(1)
        amount = parse_amount(amount_token)

    # 単位検出
    unit = None
    if m_amount:
        start = m_amount.end()
        window = pre[start:start+30]  # 直後窓
        u = _find_unit_in_text(window)
        if not u:
            u = _find_unit_in_text(pre)
        unit = u
    else:
        unit = _find_unit_in_text(pre)

    # 材料名候補抽出
    cleaned = pre
    if amount_token:
        cleaned = re.sub(re.escape(amount_token), " ", cleaned, count=1)
    if unit:
        cleaned = re.sub(r"\b" + re.escape(unit) + r"\b", " ", cleaned, flags=re.I, count=1)

    cleaned = re.sub(
        r"\b(of|approximately|approx|about|to serve|for frying|for dusting|plus|plus extra|or to taste)\b",
        " ", cleaned, flags=re.I
    )

    parts = re.split(r",|\s-\s|\s—\s", cleaned, maxsplit=1)
    ingredient_name = parts[0].strip()
    if not ingredient_name:
        ingredient_name = original
    if len(parts) > 1:
        comments.append(parts[1].strip())
    comment = "; ".join([c for c in comments if c])

    ingredient_name = re.sub(r"\s+", " ", ingredient_name).strip()
    comment = re.sub(r"\s+", " ", comment).strip()

    # --- oz/fl oz 自動マッピング ---
    ingredient_key = normalize_ingredient(ingredient_name)
    if unit == "oz" and ingredient_key:
        ing_form = ingredientConversion.get(ingredient_key, {}).get("form")
        if ing_form == "liquid":
            unit = "fl oz"  # 液体なら fl oz
        else:
            unit = "oz"     # 固体なら oz

    return {
        "raw": original,
        "amount": amount,
        "amount_token": amount_token,  # デバッグ用
        "unit": unit,
        "ingredient": ingredient_name,
        "comment": comment
    }


def _find_unit_in_text(text: str):
    """テキスト中から unit を見つけ canonical unit を返す（なければ None）。"""
    if not text:
        return None
    m = _UNIT_PATTERN.search(text)
    if not m:
        return None
    raw = m.group(0).lower()
    return UNIT_ALIASES.get(raw, raw)

def tokenize_line(line: str):
    """
    1 行のレシピテキストをトークン化して返す。
    戻り値: { 'raw':line, 'amount': float|None, 'unit': 'cup'|'g'|...|None,
            'ingredient': 'milk', 'comment': '2% reduced-fat' }
    """
    if not line:
        return {"raw": line, "amount": None, "unit": None, "ingredient": "", "comment": ""}

    original = line.strip()

    # 括弧内はコメントへ移す（複数ある場合は連結）
    comments = []
    def _paren_repl(m):
        comments.append(m.group(1).strip())
        return " "
    without_paren = re.sub(r"\((.*?)\)", _paren_repl, original)

    pre = _preprocess_unicode_fractions(without_paren)

    # 数量検出（範囲対応）
    amount_pattern = re.compile(
        r"(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+)"   # 単一数値または分数
        r"(?:\s*[-–]\s*(\d+\s+\d+/\d+|\d+/\d+|\d+\.\d+|\d+))?"  # 範囲
    )
    m_amount = amount_pattern.search(pre)
    amount = None
    amount_token = None
    if m_amount:
        if m_amount.group(2):
            # 範囲表記あり
            amount_token = m_amount.group(0)
        else:
            amount_token = m_amount.group(1)
        amount = parse_amount(amount_token)

    # 単位検出（数量の近傍を優先）
    unit = None
    if m_amount:
        start = m_amount.end()
        window = pre[start:start+30]  # 直後窓（少し広め）
        u = _find_unit_in_text(window)
        if not u:
            u = _find_unit_in_text(pre)
        unit = u
    else:
        unit = _find_unit_in_text(pre)

    # 材料名候補抽出：数量と単位トークンを取り除く
    cleaned = pre
    if amount_token:
        cleaned = re.sub(re.escape(amount_token), " ", cleaned, count=1)
    if unit:
        cleaned = re.sub(r"\b" + re.escape(unit) + r"\b", " ", cleaned, flags=re.I, count=1)

    # 副詞的フレーズを取り除く（plus系・for〜系などを一部除去）
    cleaned = re.sub(r"\b(of|approximately|approx|about|to serve|for frying|for dusting|plus|plus extra|or to taste)\b", " ", cleaned, flags=re.I)

    # コメント候補（カンマ、空白で囲まれたハイフン、エムダッシュで分割）
    parts = re.split(r",|\s-\s|\s—\s", cleaned, maxsplit=1)
    ingredient_name = parts[0].strip()
    if not ingredient_name:
        ingredient_name = original

    if len(parts) > 1:
        comments.append(parts[1].strip())

    comment = "; ".join([c for c in comments if c])

    # 最終トリム
    ingredient_name = re.sub(r"\s+", " ", ingredient_name).strip()
    comment = re.sub(r"\s+", " ", comment).strip()

    return {
        "raw": original,
        "amount": amount,
        "unit": unit,
        "ingredient": ingredient_name,
        "comment": comment
    }


def normalize_unit(unit: str):
    if not unit:
        return None
    unit = unit.lower().rstrip(".")
    plurals = {
        "cups": "cup",
        "tablespoons": "tbsp",
        "teaspoons": "tsp",
        "tbsps": "tbsp",
        "tsps": "tsp"
    }
    return plurals.get(unit, unit)

def is_countable_ingredient(ingredient: str):
    if not ingredient:
        return False
    return any(x in ingredient.lower() for x in ["egg", "eggs", "卵"])

def normalize_ingredient(name: str):
    """
    最長一致で ingredientConversion のキーとマッチングする。
    長いキー（例: 'all-purpose flour'）を優先してマッチする。
    """
    name_l = (name or "").lower()
    for key in sorted(ingredientConversion.keys(), key=lambda x: -len(x)):
        if key in name_l:
            return key
    return name_l.strip()

# ------------------------
# API エンドポイント（簡易）
# ------------------------

def unit_conversion_api(request):
    return JsonResponse(unitConversion)

def ingredient_conversion_api(request):
    return JsonResponse(ingredientConversion)

# ------------------------
# レシピ変換エンドポイント
# ------------------------

@csrf_exempt
def convert_recipe(request):
    """
    JP ↔ US/UK 両方向対応レシピ変換
    - direction はフロントから from_unit_system / to_unit_system で受け取る
    - ingredientConversion / unitConversion を活用
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        recipe_text = data.get("recipe_text", "")
        from_unit_system = data.get("from_unit_system", "jp") or "jp"
        to_unit_system = data.get("to_unit_system", "jp") or "jp"

        lines = [line.strip() for line in recipe_text.splitlines() if line.strip()]
        result = []

        # small/medium/large 対応表（g/個）
        medium_units = {
            "egg": {"small": 40, "medium": 50, "large": 60},
            "onion": {"small": 110, "medium": 150, "large": 200},
            "tomato": {"small": 100, "medium": 125, "large": 150},
            "carrot": {"small": 50, "medium": 70, "large": 100},
            "potato": {"small": 100, "medium": 150, "large": 200},
            "apple": {"small": 100, "medium": 125, "large": 150},
            "banana": {"small": 100, "medium": 120, "large": 140},
        }

        # --- 行ごとの処理 ---
        for line in lines:
            tokens = tokenize_line(line)
            amount = tokens.get("amount")
            unit = tokens.get("unit")
            ingredient_name = tokens.get("ingredient")
            comment = tokens.get("comment")

            ingredient_key = normalize_ingredient(ingredient_name)
            ing_conf = ingredientConversion.get(ingredient_key, {}) or {}
            form = ing_conf.get("form")  # "solid" / "liquid" / "unit" / None

            converted_amount = None
            converted_unit = None

            # 非換算ユニット
            if unit and unit.lower() in NON_MEASURE_UNITS:
                converted_amount = None
                converted_unit = unit.lower()
                result.append({
                    "ingredient": ingredient_name,
                    "comment": comment,
                    "amount": converted_amount,
                    "unit": converted_unit
                })
                continue

            # ---------- JP → US/UK ----------
            if from_unit_system == "jp" and to_unit_system in ("us", "uk"):
                if form == "unit":
                    # 個数系はそのまま個数表示
                    converted_amount = amount if amount is not None else 1
                    converted_unit = "個"

                elif form in ("solid", "liquid") and amount is not None:
                    # 逆算テーブル（例: 1 cup = 120g の場合 g → cup = g/120）
                    system_table = ing_conf.get(to_unit_system, {}) if ing_conf else {}
                    if unit in ("g", "ml") and system_table:
                        # 近い単位で換算（cup/tbsp/tsp/oz/fl oz）
                        for u, factor in system_table.items():
                            # factor: 1 cup = 120g のような係数
                            converted_amount = amount / factor
                            converted_unit = u
                            break
                        else:
                            converted_amount = amount
                            converted_unit = unit
                    else:
                        converted_amount = amount
                        converted_unit = unit
                else:
                    converted_amount = amount
                    converted_unit = unit

            # ---------- 外国 → JP ----------
            elif to_unit_system == "jp":
                if form == "unit":
                    if unit in ("small", "medium", "large"):
                        base_weight = medium_units.get(ingredient_key, {}).get(unit)
                        if amount is not None and base_weight:
                            converted_amount = amount * base_weight
                            converted_unit = "g"
                        else:
                            converted_amount = amount
                            converted_unit = unit
                    else:
                        converted_amount = amount if amount is not None else 1
                        converted_unit = "個"

                elif form in ("solid", "liquid") and amount is not None and unit:
                    system_table = ing_conf.get(from_unit_system, {}) if ing_conf else {}
                    unit_value = system_table.get(unit) if system_table else None
                    if unit_value:
                        converted_amount = amount * unit_value
                        converted_unit = "ml" if form=="liquid" else "g"
                    else:
                        fallback = unitConversion.get(from_unit_system, {})
                        converted_amount = amount * fallback.get(unit, 1)
                        converted_unit = "ml" if form=="liquid" else "g"
                else:
                    converted_amount = amount
                    converted_unit = unit

            else:
                converted_amount = amount
                converted_unit = unit

            # 丸め処理（humanize）
            def humanize(a, u, f):
                if a is None:
                    return None
                if u=="個":
                    return int(round(a))
                if u=="g":
                    return int(round(a)) if a>=5 else round(a,1)
                if u=="ml":
                    return int(round(a)) if a>=5 else round(a,1)
                return round(a,1) if f in ("solid","liquid") else a

            converted_amount = humanize(converted_amount, converted_unit, form)

            result.append({
                "ingredient": ingredient_name,
                "comment": comment,
                "amount": converted_amount,
                "unit": converted_unit
            })

        return JsonResponse({"converted_recipe": result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=400)
