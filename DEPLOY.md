# デプロイガイド

## デプロイプラットフォームの選択

このアプリはStreamlitで構築されているため、以下のプラットフォームでデプロイできます：

### 推奨：Streamlit Cloud（最も簡単）
- ✅ 無料
- ✅ GitHubと連携して自動デプロイ
- ✅ Streamlit専用に最適化
- 📍 https://share.streamlit.io/

### その他の選択肢
- **Railway**: https://railway.app/（無料枠あり）
- **Render**: https://render.com/（無料枠あり）
- **Fly.io**: https://fly.io/（無料枠あり）
- **Google Cloud Run**: https://cloud.google.com/run（従量課金）

**注意：** VercelはStreamlitアプリの直接デプロイには対応していません。Vercelで動かすには、FastAPI + Next.jsへの変換が必要です。詳細は `VERCEL_DEPLOY.md` を参照してください。

---

# Streamlit Cloud デプロイガイド

## デプロイ手順

### 1. GitHubリポジトリの準備

1. GitHubアカウントでログイン
2. 新しいリポジトリを作成（例：`pitch-contest-scoring`）
3. リポジトリをローカルにクローンまたは初期化

### 2. ファイルのプッシュ

```bash
cd pitch_contest_scoring

# Gitリポジトリを初期化（まだの場合）
git init

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit: Pitch Contest Scoring System"

# GitHubリポジトリに接続
git remote add origin https://github.com/your-username/pitch-contest-scoring.git

# プッシュ
git push -u origin main
```

### 3. Streamlit Cloudでデプロイ

1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. 「Sign in with GitHub」でGitHubアカウントでログイン
3. 「New app」をクリック
4. 設定：
   - **Repository**: 作成したGitHubリポジトリを選択
   - **Branch**: `main`（または`master`）
   - **Main file path**: `app.py`
5. 「Deploy!」をクリック

### 4. デプロイ後の確認

- デプロイが完了すると、URLが生成されます（例：`https://your-app-name.streamlit.app`）
- アプリが正常に起動するか確認
- 「⚙️ API設定」ページでAPIキーを設定

## トラブルシューティング

### デプロイエラー：モジュールが見つからない

`requirements.txt`にすべての依存パッケージが含まれているか確認してください。

### デプロイエラー：ファイルが見つからない

- `app.py`がリポジトリのルートにあることを確認
- `utils/`フォルダが含まれていることを確認
- `.gitignore`で必要なファイルが除外されていないか確認

### データファイルのエラー

- `data/`フォルダは自動的に作成されます
- 初回起動時にJSONファイルが自動生成されます

### APIキーの設定

Streamlit Cloudでは、アプリ内でAPIキーを設定するか、環境変数として設定することもできます：

1. Streamlit Cloudのダッシュボードでアプリを選択
2. 「Settings」→「Secrets」を開く
3. 以下の形式でシークレットを追加：

```toml
OPENAI_API_KEY = "your-api-key-here"
AI_PROVIDER = "openai"
```

または

```toml
GOOGLE_API_KEY = "your-api-key-here"
AI_PROVIDER = "gemini"
```

環境変数を設定した場合、`utils/ai_scoring.py`を環境変数からも読み取れるように修正が必要です。

## 注意事項

- Streamlit Cloudは無料プランで利用可能
- アプリは自動的にスリープします（一定時間アクセスがない場合）
- ファイルアップロードは一時的なストレージに保存されます
- データファイル（JSON）は永続化されますが、アプリを削除すると失われます

