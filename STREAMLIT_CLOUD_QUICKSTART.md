# Streamlit Cloud クイックスタート

## 🚀 5分でデプロイ完了！

### ステップ1: GitHubリポジトリの準備

1. **GitHubでリポジトリを作成**
   - https://github.com/new にアクセス
   - リポジトリ名を入力（例：`pitch-contest-scoring`）
   - 「Public」または「Private」を選択
   - 「Create repository」をクリック

2. **ローカルリポジトリをGitHubに接続**

```bash
cd "/Users/makishimaryuusuke/Ryusuke Memo/SPLYZAMotion/pitch_contest_scoring"

# 変更をコミット
git add .
git commit -m "Prepare for Streamlit Cloud deployment"

# GitHubリポジトリに接続（your-usernameを実際のユーザー名に置き換え）
git remote add origin https://github.com/your-username/pitch-contest-scoring.git

# または、既にリモートが設定されている場合
git remote set-url origin https://github.com/your-username/pitch-contest-scoring.git

# プッシュ
git branch -M main
git push -u origin main
```

### ステップ2: Streamlit Cloudでデプロイ

1. **Streamlit Cloudにアクセス**
   - https://share.streamlit.io/ を開く

2. **GitHubでログイン**
   - 「Sign in with GitHub」をクリック
   - GitHubアカウントで認証

3. **新しいアプリを作成**
   - 「New app」をクリック
   - 以下の設定を入力：
     - **Repository**: `your-username/pitch-contest-scoring` を選択
     - **Branch**: `main`
     - **Main file path**: `app.py`
   - 「Deploy!」をクリック

4. **デプロイ完了を待つ**
   - 1-2分でデプロイが完了します
   - 完了すると、URLが表示されます（例：`https://pitch-contest-scoring.streamlit.app`）

### ステップ3: アプリの確認

1. **アプリにアクセス**
   - 表示されたURLをクリック
   - アプリが正常に起動するか確認

2. **APIキーを設定**
   - 「⚙️ API設定」ページでAPIキーを設定
   - OpenAI APIキーまたはGoogle Gemini APIキーを入力

3. **動作確認**
   - 参加校を登録
   - 提出資料をアップロード
   - AI採点を実行

## ✅ デプロイ前チェックリスト

- [ ] `app.py`がルートディレクトリにある
- [ ] `requirements.txt`が存在し、すべての依存パッケージが含まれている
- [ ] `utils/`フォルダが存在する
- [ ] `.streamlit/config.toml`が存在する
- [ ] `.gitignore`に`venv/`と`data/`が含まれている
- [ ] GitHubリポジトリにすべてのファイルがプッシュされている

## 🔧 トラブルシューティング

### エラー: モジュールが見つからない

`requirements.txt`を確認し、すべての依存パッケージが含まれているか確認してください。

### エラー: ファイルが見つからない

- `app.py`がリポジトリのルートにあることを確認
- `utils/`フォルダが含まれていることを確認
- GitHubリポジトリのファイル一覧を確認

### エラー: APIキーが設定できない

- アプリ内の「⚙️ API設定」ページで設定
- または、Streamlit Cloudの「Settings」→「Secrets」で環境変数として設定

## 📝 次のステップ

デプロイが完了したら：

1. **カスタムドメインの設定**（オプション）
   - Streamlit Cloudの「Settings」でカスタムドメインを設定可能

2. **環境変数の設定**（オプション）
   - APIキーを環境変数として設定すると、毎回入力する必要がなくなります

3. **自動デプロイの確認**
   - GitHubにプッシュすると、自動的に再デプロイされます

## 🎉 完了！

これで、Streamlit Cloudでアプリが公開されました！






