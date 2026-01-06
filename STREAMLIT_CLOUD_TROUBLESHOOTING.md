# Streamlit Cloud トラブルシューティング

## requirements.txt インストールエラー

### よくあるエラーと解決方法

#### エラー1: パッケージが見つからない

**エラーメッセージ例：**
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解決方法：**
- パッケージ名が正しいか確認
- バージョン指定を緩和（`>=` から `==` に変更、またはバージョン指定を削除）

#### エラー2: 依存関係の競合

**エラーメッセージ例：**
```
ERROR: Cannot install xxx because these package versions have conflicting dependencies.
```

**解決方法：**
- バージョン指定を削除して最新版を使用
- または、互換性のあるバージョンを指定

#### エラー3: Pythonバージョンの互換性

**エラーメッセージ例：**
```
ERROR: Package xxx requires Python >=3.9, but you are using Python 3.8
```

**解決方法：**
- Streamlit CloudはPython 3.11を使用
- Python 3.11と互換性のあるパッケージバージョンを指定

### 推奨されるrequirements.txtの形式

```txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
openai>=1.3.0
google-generativeai>=0.3.0
PyPDF2>=3.0.1
python-pptx>=0.6.23
python-docx>=1.1.0
openpyxl>=3.1.2
```

### デバッグ方法

1. **Streamlit Cloudのログを確認**
   - アプリの「Manage app」→「Logs」でエラーの詳細を確認

2. **ローカルでテスト**
   ```bash
   pip install -r requirements.txt
   ```
   ローカルでエラーが出る場合は、Streamlit Cloudでも同じエラーが出ます

3. **最小限のrequirements.txtでテスト**
   - 一度に1つずつパッケージを追加して、どのパッケージが問題かを特定

### 現在のrequirements.txtの確認

現在のrequirements.txtは以下の通りです：

```txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
openai>=1.3.0
google-generativeai>=0.3.0
PyPDF2>=3.0.1
python-pptx>=0.6.23
python-docx>=1.1.0
openpyxl>=3.1.2
```

### 次のステップ

1. Streamlit Cloudのログで具体的なエラーメッセージを確認
2. エラーメッセージに基づいてrequirements.txtを修正
3. GitHubにプッシュして再デプロイ

### よくある問題のパッケージ

- **python-docx**: `python-docx`が正しいパッケージ名（`docx`ではない）
- **python-pptx**: `python-pptx`が正しいパッケージ名（`pptx`ではない）
- **google-generativeai**: 最新版を使用（`>=0.3.0`）















