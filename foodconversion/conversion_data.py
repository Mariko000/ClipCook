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


# ------------------------
# 食材ごとの換算表（US/UK単位を明示）
# ------------------------
ingredientConversion = {
    # --- 粉類 ---
    "flour": {
        "us": {"cup": 120, "tbsp": 7.5, "tsp": 2.5},
        "uk": {"cup": 125, "tbsp": 7.8, "tsp": 2.6},
        "jp": {"cup": 120, "tbsp": 7.5, "tsp": 2.5},
        "form": "solid"
    },
    "bread flour": {"us": {"cup": 120, "tbsp": 7.5}, "form": "solid"},
    "cake flour": {"us": {"cup": 120, "tbsp": 7.5}, "form": "solid"},

    # --- 砂糖 ---
    "sugar": {"us": {"cup": 200, "tbsp": 12.5, "tsp": 4.2},
              "uk": {"cup": 225, "tbsp": 14, "tsp": 4.7},
              "form": "solid"},
    "caster sugar": {"us": {"cup": 200, "tbsp": 12.5, "tsp": 4.2},
                     "uk": {"cup": 225, "tbsp": 14, "tsp": 4.7},
                     "form": "solid"},
    "granulated sugar": {"us": {"cup": 200, "tbsp": 12.5},
                         "uk": {"cup": 225, "tbsp": 14},
                         "form": "solid"},
    "brown sugar": {"us": {"cup": 213, "tbsp": 13.3, "tsp": 4.4},
                    "uk": {"cup": 220},
                    "form": "solid"},
    "powdered sugar": {"us": {"cup": 120, "tbsp": 7.5}, "form": "solid"},

    # --- ベーキング類 ---
    "baking powder": {"us": {"tsp": 4.0, "tbsp": 12.0}, "uk": {"tsp": 5}, "form": "solid"},
    "baking soda": {"us": {"tsp": 1.5, "tbsp": 4.5}, "uk": {"tsp": 5}, "form": "solid"},

    # --- 塩 ---
    "salt": {"us": {"tsp": 5}, "uk": {"tsp": 5.8}, "form": "solid"},

    # --- バター・乳製品 ---
    "butter": {"us": {"tbsp": 14.2, "cup": 227, "stick": 113}, "form": "solid"},
    "ricotta cheese": {"us": {"cup": 246, "tbsp": 15.4},
                       "uk": {"cup": 250},
                       "form": "solid"},
    "cream cheese": {"us": {"cup": 240}, "form": "solid"},
    "yogurt": {"us": {"cup": 245}, "form": "liquid"},
    "milk": {
        "us": {
            "cup": 240, "tbsp": 15, "tsp": 5,
            "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57,
            "oz": 29.57, "ounce": 29.57, "ounces": 29.57  # 追加
        },
        "uk": {
            "cup": 284,
            "fl oz": 28.41, "fluid ounce": 28.41, "fluid ounces": 28.41,
            "oz": 28.41, "ounce": 28.41, "ounces": 28.41  # 追加
        },
        "jp": {"cup": 200},
        "form": "liquid"
    },
    "heavy cream": {"us": {"cup": 240,
                           "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57},
                    "form": "liquid"},

    # --- 油類 ---
     "olive oil": {
        "us": {
            "tbsp": 14.79, "tsp": 4.93,
            "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57,
            "oz": 29.57, "ounce": 29.57, "ounces": 29.57  # 追加
        },
        "uk": {
            "tbsp": 15, "tsp": 5,
            "fl oz": 28.41, "fluid ounce": 28.41, "fluid ounces": 28.41,
            "oz": 28.41, "ounce": 28.41, "ounces": 28.41  # 追加
        },
        "jp": {"tbsp": 15, "tsp": 5},
        "form": "liquid"
    },
    "vegetable oil": {
        "us": {"fl oz": 29.57, "oz": 29.57, "ounce": 29.57, "ounces": 29.57, "tbsp": 14.79, "tsp": 4.93},
        "uk": {"fl oz": 28.41, "oz": 28.41, "ounce": 28.41, "ounces": 28.41, "tbsp": 15, "tsp": 5},
        "jp": {"tbsp": 15, "tsp": 5},
        "form": "liquid"
    },

    # --- シロップ類 ---
    "maple syrup": {"us": {"cup": 322, "tbsp": 20,
                           "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57},
                    "form": "liquid"},
    "honey": {"us": {"cup": 340, "tbsp": 21.3,
                     "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57},
              "form": "liquid"},

    # --- 調味料 ---
    "fresh lemon juice": {"us": {"tbsp": 15, "tsp": 5,
                                 "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57},
                         "form": "liquid"},
    "vanilla extract": {"us": {"tsp": 5,
                               "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57},
                        "form": "liquid"},
    "soy sauce": {"us": {"cup": 240, "tbsp": 15, "tsp": 5,
                         "fl oz": 29.57, "fluid ounce": 29.57, "fluid ounces": 29.57},
                  "jp": {"cup": 200}, "form": "liquid"},
    "pepper": {"us": {"tsp": 2.3}, "form": "solid"},

    # --- 卵 ---
    "egg": {"form": "unit",
            "unit_weight": 60,
            "weight_by_size": {"medium": 50, "large": 60}},

    # --- 野菜・果物 ---
    "onion": {"form": "unit", "unit_weight": 150},
    "carrot": {"form": "unit", "unit_weight": 70},
    "potato": {"form": "unit", "unit_weight": 150},
    "tomato": {"form": "unit", "unit_weight": 125},
    "apple": {"form": "unit", "unit_weight": 125},
    "banana": {"form": "unit", "unit_weight": 120},
}


# ------------------------
# パーサー用補助メモ
# ------------------------
# 複雑文字列例: "1/4 tsp baking soda (bi0carb) or 3/4 tsp extra baking powder"
# 処理方針:
# 1. 括弧内コメントを除去
# 2. "or"/","で分割して複数材料として扱う
# 3. 各材料を ingredientConversion で換算
