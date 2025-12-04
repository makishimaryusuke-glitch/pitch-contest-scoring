# ピッチコンテストAI採点システム

提出資料（PDF、PowerPoint等）をAIが自動採点するシステムです。

## 機能

- ✅ 提出資料のアップロード・管理
- ✅ AIによる自動採点（6つの評価項目、各10点、合計60点満点）
- ✅ 採点結果の一覧表示・詳細表示
- ✅ レーダーチャートによる可視化
- ✅ 採点結果のエクスポート（CSV、Excel）

## 技術スタック

- **フロントエンド・バックエンド：** Streamlit (Python)
- **データ管理：** JSONファイル（CSVエクスポート対応）
- **AI API：** OpenAI GPT-4 / Google Gemini Pro
- **ファイル処理：** PyPDF2, python-pptx
- **データ可視化：** Plotly

## セットアップ

### 1. 仮想環境の作成と依存パッケージのインストール

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. アプリの起動

**方法1: 起動スクリプトを使用（推奨）**
```bash
./start.sh
```

**方法2: 手動で仮想環境を有効化**
```bash
source venv/bin/activate
streamlit run app.py
```

ブラウザで http://localhost:8501 が開きます。

## プロジェクト構造

```
pitch_contest_scoring/
├── app.py                 # メインのStreamlitアプリ
├── requirements.txt       # 依存パッケージ
├── start.sh               # アプリ起動スクリプト
├── venv/                  # Python仮想環境（自動生成）
├── utils/
│   ├── data_manager.py   # データ管理関数（JSONファイル）
│   ├── file_processor.py # ファイル処理関数
│   ├── ai_scoring.py     # AI採点関数
│   └── visualization.py  # 可視化関数
├── data/                 # データファイル（JSON形式）
│   ├── schools.json
│   ├── submissions.json
│   ├── evaluation_results.json
│   └── evaluation_details.json
└── uploads/              # アップロードされたファイル
```

## 使用方法

1. アプリを起動
2. **「⚙️ API設定」ページでAPIキーを設定**（初回のみ）
   - OpenAI APIキーまたはGoogle Gemini APIキーを入力
3. 「📤 提出資料のアップロード」ページでファイルをアップロード
4. 「🤖 AI採点の実行」ページで採点を実行
5. 「📊 採点結果」ページで結果を確認

**注意：** APIキーはブラウザを閉じるまで有効です。次回起動時は再度設定が必要です。

## デプロイ

Streamlit Cloudにデプロイする場合：

### 基本的なデプロイ手順

1. **GitHubリポジトリにプッシュ**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/pitch-contest-scoring.git
   git push -u origin main
   ```

2. **Streamlit Cloudでデプロイ**
   - https://share.streamlit.io/ にアクセス
   - GitHubアカウントでログイン
   - 「New app」をクリック
   - Repository: 作成したリポジトリを選択
   - Branch: `main`
   - Main file path: `app.py`
   - 「Deploy!」をクリック

3. **APIキーの設定**
   - アプリ内の「⚙️ API設定」ページで設定
   - または、Streamlit Cloudの「Settings」→「Secrets」で環境変数として設定

詳細は `DEPLOY.md` を参照してください。

