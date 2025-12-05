# Vercelデプロイガイド

## ⚠️ 重要な注意事項

**VercelはStreamlitアプリの直接デプロイには対応していません。**

Vercelは主に以下のプラットフォーム向けに最適化されています：
- Next.js（React）
- Vue.js
- Nuxt.js
- 静的サイト
- サーバーレス関数（Node.js、Python、Goなど）

StreamlitアプリをVercelで動かすには、以下の選択肢があります：

## 選択肢1: FastAPIに変換してVercelでデプロイ（推奨）

StreamlitアプリをFastAPIベースのAPIサーバーに変換し、Vercelのサーバーレス関数としてデプロイします。

### メリット
- ✅ Vercelでデプロイ可能
- ✅ サーバーレス関数として動作（コスト効率が良い）
- ✅ 既存のロジックを再利用可能

### デメリット
- ❌ UIをNext.jsで再構築する必要がある
- ❌ 開発工数が増える

### 実装方法
1. バックエンドAPIをFastAPIで構築
2. フロントエンドをNext.jsで構築
3. Vercelでデプロイ

## 選択肢2: 他のプラットフォームを使用（最も簡単）

Streamlitアプリをそのまま動かせるプラットフォームを使用します。

### 推奨プラットフォーム

#### 1. **Streamlit Cloud**（最も簡単）
- ✅ 無料
- ✅ GitHubと連携して自動デプロイ
- ✅ Streamlit専用に最適化
- 📍 https://share.streamlit.io/

#### 2. **Railway**
- ✅ 無料枠あり（$5/月のクレジット）
- ✅ 簡単なデプロイ
- ✅ データベースも利用可能
- 📍 https://railway.app/

#### 3. **Render**
- ✅ 無料枠あり（スリープあり）
- ✅ GitHubと連携
- ✅ 簡単なデプロイ
- 📍 https://render.com/

#### 4. **Fly.io**
- ✅ 無料枠あり
- ✅ グローバルCDN
- ✅ Dockerサポート
- 📍 https://fly.io/

#### 5. **Google Cloud Run**
- ✅ 従量課金（無料枠あり）
- ✅ スケーラブル
- ✅ Dockerサポート
- 📍 https://cloud.google.com/run

## 選択肢3: StreamlitアプリをNext.jsに完全変換

StreamlitのUIをNext.jsで再構築します。

### メリット
- ✅ Vercelで最適化されたデプロイ
- ✅ モダンなUI/UX
- ✅ パフォーマンス向上

### デメリット
- ❌ 大規模な開発工数が必要
- ❌ 既存のStreamlitコードを大幅に変更

## 推奨：Streamlit Cloudを使用

現在のStreamlitアプリをそのまま動かすなら、**Streamlit Cloud**が最も簡単で最適です。

### Streamlit Cloudのデプロイ手順

1. GitHubリポジトリにプッシュ
2. https://share.streamlit.io/ にアクセス
3. GitHubアカウントでログイン
4. 「New app」をクリック
5. リポジトリを選択してデプロイ

詳細は `DEPLOY.md` を参照してください。

## Vercelでどうしても動かしたい場合

FastAPI + Next.jsへの変換が必要です。以下のファイルを作成します：

1. `api/` - FastAPIバックエンド
2. `frontend/` - Next.jsフロントエンド
3. `vercel.json` - Vercel設定

この場合、開発工数は2-3週間程度かかります。

## 結論

**Streamlitアプリをそのまま動かすなら：Streamlit Cloudを推奨**
**Vercelで動かすなら：FastAPI + Next.jsへの変換が必要**

どちらの方向で進めますか？



