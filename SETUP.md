# セットアップ手順

## 1. 依存パッケージのインストール

```bash
cd pitch_contest_scoring
pip install -r requirements.txt
```

## 2. アプリの起動

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

## 3. APIキーの設定（初回のみ）

アプリ起動後、「⚙️ API設定」ページで：
- OpenAI APIキーまたはGoogle Gemini APIキーを入力
- 「APIキーを設定」ボタンをクリック

**注意：** 
- APIキーはブラウザを閉じるまで有効です
- 次回起動時は再度設定が必要です
- Streamlit Cloudにデプロイする場合は、環境変数として設定することもできます

## トラブルシューティング

### データファイルエラー

データファイル（`data/*.json`）が存在しない場合は、自動的に作成されます。

### AI APIエラー

- 「⚙️ API設定」ページでAPIキーが正しく設定されているか確認
- APIキーの有効期限を確認
- APIキーの使用量制限に達していないか確認
- レート制限に達していないか確認

### ファイルアップロードエラー

- `uploads/`フォルダの書き込み権限を確認
- ファイルサイズが大きすぎないか確認（推奨: 10MB以下）

