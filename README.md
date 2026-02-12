ClipCook
🍲 外国レシピの「計量の壁」を技術で解決する、日・英・米対応レシピSNS
🌟 プロジェクト概要
ClipCookは、海外レシピ特有の単位（cup, oz, lb等）や、地域による容量差（US/UK/JP）を自動吸収し、誰でも正確に調理できるようにサポートするレシピ管理・SNSプラットフォームです。

単なる計算ツールではなく、「物質の密度」まで考慮した独自の換算エンジンを搭載しています。

🛠 技術スタック
Frontend: Vue.js 3 (Composition API), Pinia, PWA

Backend: Django, Django Rest Framework (DRF)

Database: PostgreSQL / SQLite

Authentication: django-allauth

Logic: 自作食材密度換算エンジン (Python)

🚀 主要機能
1. Quantify（レシピ・カスタマイザー）
フロントエンドとバックエンドのハイブリッド処理による高精度なレシピ変換。

双方向・三地域単位変換:

日・英・米の単位系（cup, oz, lb, fl oz, tbsp, tsp）を相互変換。

「物質変換」ロジック: 水、小麦粉、砂糖など、食材ごとの密度を考慮した重量（g）換算。

材料連動型・自動倍率計算:

特定の材料を「基準」にして分量を変更すると、レシピ全体の比率をリアルタイムに再計算。

2. Timeline（TikTok風レシピSNS）
スワイプUI: 直感的な操作で新しいレシピを発見。

Quantify連携: タイムラインで見つけたレシピを、ワンタップで自分の必要分量へ調整。

ソーシャル機能: フォロー、いいね、ブックマーク、リアルタイムチャット。

🧠 技術的なこだわり（課題解決）
① 浮動小数点誤差の蓄積防止
倍率計算において、計算後の値を元に再計算を繰り返すと、端数処理により数値が劣化します。

解決: 常に最初の入力値をマスター（Source of Truth）として保持する originalQuantities 方式を採用。何度倍率を変更しても、常に正確な数値を維持します。

② 非定型テキストの構造化
レシピ全文をAPIへ送信し、以下のプロセスで正規化しています。

テキスト解析: Unicode分数（½）や混合数（1 1/2）、範囲（1-2g）を数値化。

正規化: 語彙揺れ（synonyms統合）を自作辞書でマッピング。

フォールバック戦略: 食材固有の密度データがない場合、汎用単位換算へ安全にフォールバック。

③ 信頼性の高いデータソース
計算の根拠となる数値は、以下の公的機関のデータを参照し、辞書（conversion_data.py）を自作しました。

米国 NIST (National Institute of Standards and Technology)

英国 NPL (National Physical Laboratory)

文部科学省 「日本食品標準成分表」

📈 今後の展望（Roadmap）
[ ] AI加熱調理アドバイザー: 食材の総重量から、オーブンの最適な温度・焼き時間をAIが算出。

[ ] ビジュアル・パントリー: 海外食材の「外箱写真」を紐付け、コストコ等の店舗レコメンドを実装。

[ ] AIレシピジェネレーター: クリエイター向けに、ターゲット（高タンパク等）に合わせたレシピ構成案を自動生成。

🔧 開発者向けセットアップ（抜粋）
Bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate

# Frontend
cd frontend
npm install
npm run dev
