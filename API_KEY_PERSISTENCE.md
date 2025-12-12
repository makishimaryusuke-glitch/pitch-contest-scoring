# APIキーの永続化設定ガイド

## 現在の動作

現在、APIキーは**ブラウザのセッション状態**に保存されているため、ブラウザを閉じると消えてしまいます。そのため、毎回設定が必要です。

## 解決方法：Streamlit CloudのSecrets機能を使用

Streamlit Cloudでは、**Secrets機能**を使って環境変数としてAPIキーを設定できます。一度設定すれば、再デプロイしない限り保持されます。

### 設定手順

1. **Streamlit Cloudのダッシュボードにアクセス**
   - https://share.streamlit.io/ にアクセス
   - アプリを選択

2. **Settingsを開く**
   - 「Manage app」をクリック
   - 「Settings」タブを選択

3. **Secretsを開く**
   - 「Secrets」セクションを開く

4. **APIキーを設定**
   
   **OpenAI APIキーを使用する場合：**
   ```toml
   OPENAI_API_KEY = "your-openai-api-key-here"
   AI_PROVIDER = "openai"
   ```
   
   **Google Gemini APIキーを使用する場合：**
   ```toml
   GOOGLE_API_KEY = "your-google-api-key-here"
   AI_PROVIDER = "gemini"
   ```

5. **保存**
   - 「Save」ボタンをクリック
   - アプリが自動的に再起動します

### 設定後の動作

- 環境変数から自動的にAPIキーが読み込まれます
- アプリ内の「⚙️ API設定」ページで「✅ APIキーが設定されています」と表示されます
- ブラウザを閉じてもAPIキーは保持されます

### 注意事項

- **セキュリティ**: Secretsに設定したAPIキーは暗号化されて保存されます
- **アクセス制限**: Streamlit Cloudのダッシュボードにアクセスできる人だけが設定できます
- **再デプロイ**: アプリを削除すると、Secretsも削除されます

## ローカル環境での永続化（オプション）

ローカル環境でAPIキーを永続化したい場合は、`.streamlit/secrets.toml`ファイルを作成することもできますが、**このファイルはGitにコミットしないでください**。

```toml
# .streamlit/secrets.toml（Gitにコミットしない）
OPENAI_API_KEY = "your-api-key"
AI_PROVIDER = "openai"
```

`.gitignore`に`.streamlit/secrets.toml`が含まれていることを確認してください。







