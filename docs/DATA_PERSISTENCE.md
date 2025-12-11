# データの永続化について

## 現在の問題

Streamlit Cloudでは、ファイルシステムは一時的で、再デプロイ時にデータが消える可能性があります。

## 解決方法

### 方法1: データファイルをGitにコミットする（推奨・簡単）

データファイルをGitリポジトリにコミットすることで、再デプロイ後もデータが保持されます。

#### 設定手順

1. **`.gitignore`を確認**
   - `data/*.json`がコメントアウトされていることを確認
   - コメントアウトされていない場合は、コメントアウトする

2. **データファイルをGitに追加**
   ```bash
   git add data/*.json
   git commit -m "データファイルを追加"
   git push origin main
   ```

3. **今後の運用**
   - データが変更されたら、Gitにコミットする
   - または、自動的にコミットするスクリプトを作成

#### メリット
- ✅ 設定が簡単
- ✅ バックアップとしても機能
- ✅ データの履歴を追跡可能

#### デメリット
- ⚠️ 個人情報を含む可能性がある場合は注意が必要
- ⚠️ データが大きくなるとリポジトリが肥大化

### 方法2: 外部ストレージを使用（高度）

Google Drive、AWS S3、Supabaseなどの外部ストレージを使用する方法です。

#### Google Driveを使用する場合

1. **Google Drive APIの設定**
   - Google Cloud Consoleでプロジェクトを作成
   - Drive APIを有効化
   - サービスアカウントを作成

2. **認証情報の設定**
   - サービスアカウントのJSONキーを取得
   - Streamlit CloudのSecretsに設定

3. **コードの修正**
   - `utils/data_manager.py`を修正してGoogle Driveに保存

#### Supabaseを使用する場合

1. **Supabaseプロジェクトの作成**
   - Supabaseでプロジェクトを作成
   - データベーステーブルを作成

2. **認証情報の設定**
   - SupabaseのURLとAPIキーを取得
   - Streamlit CloudのSecretsに設定

3. **コードの修正**
   - `utils/data_manager.py`を修正してSupabaseに保存

### 方法3: Streamlit Cloudの永続ストレージ（将来対応）

Streamlit Cloudが永続ストレージ機能を提供する場合、それを使用できます。

## 推奨される実装

### 初回運用では方法1を推奨

- 設定が簡単
- データ量が少ない場合は問題なし
- バックアップとしても機能

### データ量が増えたら方法2を検討

- Google DriveやSupabaseへの移行を検討
- より安全でスケーラブル

## 実装例：Gitに自動コミットする機能

データが変更されたら自動的にGitにコミットする機能を追加することもできます。

```python
import subprocess
from pathlib import Path

def auto_commit_data():
    """データファイルを自動的にGitにコミット"""
    try:
        subprocess.run(['git', 'add', 'data/*.json'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Auto-commit: データ更新'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    except subprocess.CalledProcessError:
        # Git操作に失敗した場合は無視（ローカル環境など）
        pass
```

ただし、Streamlit CloudではGit操作が制限されている可能性があるため、この方法は推奨しません。

## 注意事項

1. **個人情報の取り扱い**
   - 参加校名などの個人情報を含む可能性がある
   - Gitにコミットする場合は、リポジトリが公開されていないことを確認

2. **データのバックアップ**
   - 定期的にデータファイルをエクスポートしてバックアップ
   - 重要なデータは複数の場所に保存

3. **データの整合性**
   - 複数人が同時に編集すると競合する可能性がある
   - 小規模利用なら問題なし

## 現在の設定確認

現在、`.gitignore`で`data/*.json`がコメントアウトされているため、データファイルはGitにコミットされる設定になっています。

データファイルをGitにコミットすることで、再デプロイ後もデータが保持されます。


