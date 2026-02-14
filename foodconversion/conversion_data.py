# foodconversion/conversion_data.py

# ------------------------
# 卵などは「個」単位に統一。サーバー側では g/ml に変換せず、そのまま返す。g表記のレシピは計量する必要もある可能性あり
# 数値換算用の辞書　unitConversion は ingredientConversion に値がない場合のフォールバックとして使う
# ------------------------

# ------------------------
# 単位換算表（日・米・英）
# ------------------------

unitConversion = {
    "jp": {
        "小さじ": 1,   # 1小さじ → 1 US tsp
        "大さじ": 1,   # 1大さじ → 1 US tbsp
        # 数値換算用として g/ml も保持
        "tsp": 5, "tbsp": 15, "cup": 200,
        "g": 1, "kg": 1000, "ml": 1, "l": 1000
    },
    "us": {
        "tsp": 4.93, "tbsp": 14.79, "cup": 240,
        "oz": 28.35, "ounce": 28.35, "ounces": 28.35,  # 重量オンス
        "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57,  # 液量オンス
        "lb": 453.6, "pint": 473, "quart": 946, "gallon": 3785,
        "g": 1, "kg": 1000, "ml": 1, "l": 1000
    },
    "uk": {
        "tsp": 5, "tbsp": 15, "cup": 250,
        "oz": 28.35, "ounce": 28.35, "ounces": 28.35,  # 重量オンス
        "fl oz": 28.41, "fluid ounce": 28.41, "fluid ounces": 28.41,  # 液量オンス
        "lb": 453.6, "pint": 568, "quart": 1136, "gallon": 4546,
        "g": 1, "kg": 1000, "ml": 1, "l": 1000
    }
      }

# 日本語→英語変換マッピング辞書
jp_to_en = {
    "牛乳": "milk",
    "薄力粉": "cake flour",
    "強力粉": "bread flour",
    "砂糖": "sugar",
    "上白糖": "sugar",
    "グラニュー糖": "granulated sugar",
    "塩": "salt",
    "卵": "egg",
    "バター": "butter",
    "水": "water",
    "オリーブオイル": "olive oil",
    "サラダ油": "vegetable oil",
    "生クリーム": "heavy cream",
    "ヨーグルト": "yogurt",
    "レモン汁": "fresh lemon juice",
    "醤油": "soy sauce",
}


# ------------------------
# 食材ごとの換算表（US/UK単位を明示）
 #すべて g/ml ベース
# ------------------------
ingredientConversion = {
    # 粉類
    "flour": {
        "us": {"cup": 120, "tbsp": 7.5, "tsp": 2.5},
        "uk": {"cup": 125, "tbsp": 7.8, "tsp": 2.6},
        "jp": {"cup": 120, "tbsp": 7.5, "tsp": 2.5},
        "form": "solid"
    },
    "all-purpose flour": {"us": {"cup": 120}, "form": "solid"},
    "bread flour": {"us": {"cup": 120, "tbsp": 7.5}, "form": "solid"},
    "cake flour": {"us": {"cup": 120, "tbsp": 7.5}, "form": "solid"},
    "cornstarch": { # コーンスターチ (US標準: 1 tsp ≈ 3g, 1 cup ≈ 128g)
        "us": {"cup": 128, "tbsp": 8, "tsp": 3},
        "uk": {"cup": 128, "tbsp": 8, "tsp": 3},
        "jp": {"cup": 110, "tbsp": 8, "tsp": 3}, # 日本の200mlカップ基準に調整
        "form": "solid"
    },

    # 砂糖
    "sugar": {"us": {"cup": 200, "tbsp": 12.5, "tsp": 4.2},
              "uk": {"cup": 225, "tbsp": 14, "tsp": 4.7},
              "form": "solid"},
    "granulated sugar": {"us": {"cup": 200, "tbsp": 12.5},
                         "uk": {"cup": 225, "tbsp": 14},
                         "form": "solid"},
    "brown sugar": {"us": {"cup": 213, "tbsp": 13.3, "tsp": 4.4}, "form": "solid"},
    "caster sugar": {"alias": "sugar"},
    "powdered sugar": {"us": {"cup": 120, "tbsp": 7.5}, "form": "solid"},

    # ベーキング
    "baking powder": {"us": {"tsp": 4.0, "tbsp": 12.0}, "uk": {"tsp": 5}, "form": "solid"},
    # baking sodaの密度を物理的に正しい値（1tsp=4.5g）
    "baking soda": {"us": {"tsp": 4.5, "tbsp": 13.5}, "uk": {"tsp": 5}, "form": "solid"},

    # 塩
    "salt": {"us": {"tsp": 5}, "uk": {"tsp": 5.8}, "form": "solid"},
    "kosher salt": {"us": {"tsp": 2.8, "tbsp": 8.4}, "form": "solid"}, # USの標準的な密度

    # バター・乳製品
    "butter": {"us": {"tbsp": 14.2,"tsp": 4.7, "cup": 225, "stick": 113}, "form": "solid"},
    "milk": {"us": {"cup": 240, "tbsp": 15, "tsp": 5}, "form": "liquid"},
    "heavy cream": {"us": {"cup": 240, "tbsp": 15}, "form": "liquid"},# ml換算
    "yogurt": {"us": {"cup": 245}, "form": "liquid"},
    "cream cheese": {"us": {"cup": 240}, "form": "solid"},

    # 油
    "olive oil": {"us": {"tbsp": 14.79, "tsp": 4.93}, "form": "liquid"},
    "vegetable oil": {"us": {"tbsp": 14.79, "tsp": 4.93}, "form": "liquid"},

    # 調味料
    "vanilla extract": {"us": {"tsp": 5, "fl oz": 29.57}, "form": "liquid"}, # tspの値をmlではなくg換算として扱う場合は5g。ここでは一旦体積mlとして扱う。
    "soy sauce": {"us": {"tbsp": 15}, "jp": {"tbsp": 15}, "form": "liquid"},
    "fresh lemon juice": {"us": {"tbsp": 15}, "form": "liquid"},

    # 卵
    "egg": {"form": "unit",
            "unit_weight": 50,
            "weight_by_size": {"medium": 50, "large": 60}},

    # 果物・野菜
    "banana": {"form": "unit",
               "unit_weight": 120,
               "cup": 200,
               "weight_by_size": {"small": 100, "large": 150}},
    
    "mashed bananas": {
        "us": {"cup": 200},
        "form": "solid"
    },
    "elbow macaroni": {
        "us": {"oz": 28.35}, # 容積単位ではないが、oz->g換算で定義
        "form": "solid"
    },
    "shredded cheddar cheese": {
        "us": {"cup": 113}, # 細切りチーズ1cupはおよそ113g（レシピ要求は200gなので、ここでは100gに調整）
        "us_adjust": {"cup": 100}, # USの換算値とは別に、日本のニーズに合わせて1cup=100gと定義するならこちら
        "form": "solid"
    },
    "blueberries": {
        "us": {"cup": 150}, # 1 cupのブルーベリーはおよそ150g
        "form": "solid"
    },
    "tomato purée": {
        "uk": {"tbsp": 15}, # 1 tbspのトマトペースト/ピュレはおよそ15g
        "form": "solid"
    },
    "golden syrup": {
        "uk": {"tbsp": 15}, # 1 tbspのゴールデンシロップはおよそ20g (水より密度が高い)
        "form": "solid"
    },
    "apple": {"form": "unit", "unit_weight": 125},
    "onion": {"form": "unit", "unit_weight": 150},
    "carrot": {"form": "unit", "unit_weight": 70},
    "potato": {"form": "unit", "unit_weight": 150},
    "tomato": {"form": "unit", "unit_weight": 125},

    # チョコ
   "chocolate chunks": {"us": {"cup": 170}, "form": "solid"},
}

# 日本語→英語変換マッピング辞書
jp_to_en = {
    "牛乳": "milk",
    "薄力粉": "flour",
    "強力粉": "bread flour",
    "砂糖": "sugar",
    "上白糖": "sugar",
    "グラニュー糖": "granulated sugar",
    "塩": "salt",
    "卵": "egg", # 元々存在
    "バター": "butter",
    "水": "water",
    "オリーブオイル": "olive oil",
    "サラダ油": "vegetable oil",
    "生クリーム": "heavy cream",
    "ヨーグルト": "yogurt",
    "レモン汁": "fresh lemon juice",
    "醤油": "soy sauce",
    "ベーキングソーダ": "baking soda",
    "ブラウンシュガー": "brown sugar",
    "チョコチップ": "chocolate chips",
    # "卵" -> "egg" があるため、複数形 "eggs" は synonyms で処理するのが一般的
    # ただし、確実性を高めるためにここでは "卵" で両方対応
    "たまご": "egg",
    "タマゴ": "egg",
    "玉子": "egg",
    "elbow macaroni": "エルボーマカロニ",
    "cheddar cheese": "チェダーチーズ (シュレッド)",
    "ベーキングパウダー": "baking powder", 
}

# 逆引き辞書を自動生成
en_to_jp = {v: k for k, v in jp_to_en.items()}

# ------------------------
# 同義語・別名マッピング（synonyms）
# ------------------------
# 別名 → 基本食材名 に正規化するための辞書
# convert_to_g_ml() 内で ingredientConversion 検索前に適用される

synonyms = {
    # チョコ系
    "chocolate chips": "chocolate chunks",
    "dark chocolate chips": "chocolate chunks",
    "milk chocolate chips": "chocolate chunks",
    "semi-sweet chocolate chips": "chocolate chunks",
    "choc chips": "chocolate chunks",

    # 砂糖系（UK表記・和訳含む）
    "caster sugar": "sugar",
    "white sugar": "sugar",
    "granulated white sugar": "sugar",
    "powdered sugar": "sugar",
    "icing sugar": "powdered sugar",

    # 小麦粉系
    "plain flour": "flour",
    "self-raising flour": "flour",
    "self raising flour": "flour",
    "all purpose flour": "all-purpose flour",

    # 油系
    "veg oil": "vegetable oil",
    "sunflower oil": "vegetable oil",

    # 卵表現
    "free-range eggs": "egg",
    "eggs": "egg",

    # バター系
    "unsalted butter": "butter",
    "salted butter": "butter",

    # 液体系
    "vanilla essence": "vanilla extract",
    "pure vanilla extract or paste": "vanilla extract",
    "lemon juice": "fresh lemon juice",
}


# ------------------------
# パーサー用補助メモ
# ------------------------
# 複雑文字列例: "1/4 tsp baking soda (bi0carb) or 3/4 tsp extra baking powder"
# 処理方針:
# 1. 括弧内コメントを除去
# 2. "or"/","で分割して複数材料として扱う
# 3. 各材料を ingredientConversion で換算
