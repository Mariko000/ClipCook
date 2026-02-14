# foodconversion/tests_recipes_convert.py
# 統合テスト用スクリプト
# コマンド: python -m foodconversion.tests_recipes_convert

from foodconversion.test_recipes import UK_RECIPES, US_RECIPES
from foodconversion.views import tokenize_line, normalize_ingredient, convert_to_g_ml, humanize

def process_recipe(recipe_items, from_system="us"):
    """
    1レシピを行ごとに処理して換算結果を返す
    """
    results = []

    for ingredient_name, raw_amount_unit in recipe_items.items():
        # 例: "225 g" → tokenize_line で amount/unit/ingredient/comment 抽出
        token = tokenize_line(f"{raw_amount_unit} {ingredient_name}")
        norm_name = normalize_ingredient(token["ingredient"])
        amount = token["amount"]
        unit = token["unit"]

        # g/ml に換算
        if amount is not None and unit is not None:
            conv_amount, conv_unit = convert_to_g_ml(norm_name, amount, unit, from_system)
            conv_amount = humanize(conv_amount, conv_unit, "solid")  # solid/liquid/unit の推測可
        else:
            conv_amount, conv_unit = None, unit

        results.append({
            "ingredient": ingredient_name,
            "normalized": norm_name,
            "raw_amount": amount,
            "raw_unit": unit,
            "converted_amount": conv_amount,
            "converted_unit": conv_unit,
            "comment": token.get("comment", "")
        })
    return results


def test_recipe_conversions():
    print("=== 🇬🇧 UK Recipes (to g/ml) ===")
    for name, items in UK_RECIPES.items():
        print(f"\n{name}")
        results = process_recipe(items, from_system="uk")
        for r in results:
            print(f"  {r['ingredient']} ({r['normalized']}): {r['converted_amount']} {r['converted_unit']} {r['comment']}")

    print("\n=== 🇺🇸 US Recipes (to g/ml) ===")
    for name, items in US_RECIPES.items():
        print(f"\n{name}")
        results = process_recipe(items, from_system="us")
        for r in results:
            print(f"  {r['ingredient']} ({r['normalized']}): {r['converted_amount']} {r['converted_unit']} {r['comment']}")


if __name__ == "__main__":
    test_recipe_conversions()
