# tests_convert.py
# foodconversion/views.py の関数を絶対インポート
from foodconversion.views import tokenize_line, convert_to_g_ml, convert_recipe_items

# 入力例
lines = [
    "1 cup sugar",
    "2 tbsp butter",
    "½ tsp salt",
    "1 large egg"
]

# 1. tokenize_line で解析
tokens_list = [tokenize_line(line) for line in lines]
print("=== Tokenize ===")
for t in tokens_list:
    print(t)

# 2. convert_to_g_ml で単位換算（US -> JP）
converted = [convert_to_g_ml(t["ingredient"], t["amount"], t["unit"], from_system="us") for t in tokens_list]
print("\n=== Convert to g/ml ===")
for original, (amount, unit) in zip(lines, converted):
    print(f"{original} -> {amount}{unit}")

# 3. convert_recipe_items を使ってまとめて変換
final = convert_recipe_items(tokens_list, from_system="us")
print("\n=== convert_recipe_items ===")
for f in final:
    print(f)
