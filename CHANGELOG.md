# 変更履歴

## シンプル構成への変更（2025-12-02）

### 削除した機能
- ❌ **認証機能（Streamlit-Authenticator）**
  - 理由：個人利用・小規模利用では不要、設定が複雑
  - 影響：ログイン不要で即座に使用可能

- ❌ **SQLiteデータベース**
  - 理由：設定が複雑、初期化が必要
  - 代替：JSONファイルによるデータ管理

### 追加・変更した機能
- ✅ **JSONファイルによるデータ管理**
  - `data/schools.json` - 参加校情報
  - `data/submissions.json` - 提出資料情報
  - `data/evaluation_results.json` - 採点結果
  - `data/evaluation_details.json` - 採点結果詳細
  - `data/files.json` - ファイル情報
  - メリット：設定不要、ファイルを直接確認可能、バックアップが簡単

### 削除したファイル
- `init_database.py` - データベース初期化スクリプト
- `schema.sql` - データベーススキーマ
- `config.yaml` - 認証設定
- `generate_password_hash.py` - パスワードハッシュ生成ツール
- `utils/database.py` - SQLiteデータベースアクセス関数

### 追加したファイル
- `utils/data_manager.py` - JSONファイルによるデータ管理関数

### 変更したファイル
- `app.py` - 認証機能を削除、データ管理をJSONファイルに変更
- `requirements.txt` - streamlit-authenticator、bcrypt、PyYAMLを削除
- `README.md` - セットアップ手順を更新
- `SETUP.md` - データベース初期化手順を削除
- `QUICKSTART.md` - 認証手順を削除

### メリット
1. **セットアップが簡単** - データベース初期化不要
2. **設定ファイルが少ない** - config.yaml不要
3. **データの確認が容易** - JSONファイルを直接確認可能
4. **バックアップが簡単** - ファイルをコピーするだけ
5. **即座に使用可能** - 認証不要で起動直後から使用可能

### デメリット（注意点）
1. **同時アクセス** - 複数人が同時に編集するとデータが競合する可能性（小規模利用なら問題なし）
2. **大量データ** - 100校以上になるとJSONファイルが重くなる可能性（10-20校程度なら問題なし）

