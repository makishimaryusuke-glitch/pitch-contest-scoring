# Streamlit Cloudで変更が反映されない場合の対処法

## 問題

GitHubにプッシュした変更がStreamlit Cloudに反映されない場合があります。

## 解決方法

### 方法1: Streamlit Cloudダッシュボードで再デプロイ

1. **Streamlit Cloudのダッシュボードにアクセス**
   - https://share.streamlit.io/ にアクセス
   - アプリを選択

2. **「Manage app」をクリック**

3. **「Settings」タブを選択**

4. **「Reboot app」ボタンをクリック**
   - または「Always rerun」を有効にして、常に最新のコードを実行

### 方法2: 空のコミットで再デプロイを促す

GitHubに空のコミットをプッシュすることで、Streamlit Cloudに変更を検知させることができます。

```bash
git commit --allow-empty -m "再デプロイを促す"
git push origin main
```

### 方法3: ブラウザのキャッシュをクリア

1. ブラウザのキャッシュをクリア
2. 強制リロード（Ctrl+Shift+R または Cmd+Shift+R）
3. シークレットモードでアクセス

### 方法4: Streamlit Cloudのログを確認

1. Streamlit Cloudのダッシュボードで「Logs」タブを確認
2. エラーがないか確認
3. デプロイが完了しているか確認

## 確認事項

### 変更が正しくプッシュされているか確認

```bash
git log --oneline -5
git status
```

### リモートリポジトリの状態を確認

```bash
git fetch origin
git log origin/main --oneline -5
```

### Streamlit Cloudの設定を確認

- 正しいブランチ（通常は`main`）が選択されているか
- 正しいリポジトリが選択されているか
- デプロイが完了しているか

## よくある問題

### 1. ブランチが間違っている

Streamlit Cloudは通常`main`ブランチをデプロイします。他のブランチに変更をプッシュしている場合は、`main`ブランチにマージしてください。

### 2. デプロイが完了していない

Streamlit Cloudのダッシュボードで、デプロイの状態を確認してください。「Deploying...」と表示されている場合は、完了するまで待ってください。

### 3. キャッシュの問題

ブラウザのキャッシュが古い可能性があります。キャッシュをクリアして再読み込みしてください。

### 4. コードのエラー

Streamlit Cloudのログを確認して、エラーがないか確認してください。エラーがある場合は修正が必要です。

## 推奨される手順

1. **変更をコミット・プッシュ**
   ```bash
   git add .
   git commit -m "変更内容"
   git push origin main
   ```

2. **Streamlit Cloudのダッシュボードで確認**
   - デプロイが開始されているか確認
   - エラーがないか確認

3. **数分待つ**
   - デプロイには通常1-3分かかります

4. **ブラウザで確認**
   - キャッシュをクリアして再読み込み
   - 変更が反映されているか確認

