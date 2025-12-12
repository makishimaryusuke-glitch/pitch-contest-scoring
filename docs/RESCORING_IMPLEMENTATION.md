# 再採点の上書き実装について

## 現在の実装

現在の再採点機能は、**新しい採点結果を作成**する方式です。

### メリット
- 採点履歴が残る
- 過去の採点結果と比較可能

### デメリット
- データが増える
- 最新の結果を取得する必要がある

## 上書き実装の方法

既存の採点結果を上書きする実装は**可能**です。

### 実装方法

1. **既存の採点結果を取得**
   - 提出資料IDから既存の採点結果を取得（最新のもの）

2. **既存の評価詳細を削除**
   - 既存の採点結果に紐づく評価詳細を削除

3. **新しい評価詳細を作成**
   - 再採点の結果で新しい評価詳細を作成

4. **既存の採点結果を更新**
   - `update_evaluation_result`関数で総合スコアとステータスを更新

### 必要な関数

評価詳細を削除する関数を追加する必要があります：

```python
def delete_evaluation_details(result_id: int):
    """採点結果詳細を削除"""
    details = load_json(EVALUATION_DETAILS_FILE)
    details = [d for d in details if d['evaluation_result_id'] != result_id]
    save_json(EVALUATION_DETAILS_FILE, details)
```

### 実装の流れ

```python
def rescore_submission_overwrite(submission_id: int) -> dict:
    # 1. 既存の採点結果を取得
    existing_results = [r for r in get_all_evaluation_results() 
                       if r['submission_id'] == submission_id 
                       and r['evaluation_status'] == 'completed']
    
    if not existing_results:
        # 既存の結果がない場合は新規作成
        return rescore_submission(submission_id)
    
    # 最新の結果を取得
    latest_result = max(existing_results, 
                       key=lambda x: x.get('evaluated_at', '') or '')
    result_id = latest_result['id']
    
    # 2. 既存の評価詳細を削除
    delete_evaluation_details(result_id)
    
    # 3. 再採点を実行
    # （ファイルからテキストを抽出して採点）
    
    # 4. 新しい評価詳細を作成
    # （各評価項目のスコアと理由）
    
    # 5. 既存の採点結果を更新
    update_evaluation_result(result_id, total_score, "completed")
    
    return {"success": True, "result_id": result_id, ...}
```

## どちらを選ぶべきか

### 上書き方式（推奨）
- ✅ データが増えない
- ✅ 常に最新の結果が表示される
- ✅ シンプル
- ❌ 採点履歴が残らない

### 新規作成方式（現在）
- ✅ 採点履歴が残る
- ✅ 過去の結果と比較可能
- ❌ データが増える
- ❌ 最新の結果を取得する必要がある

## 推奨

**上書き方式を推奨**します。理由：
- データが増えない
- 最新の結果が常に表示される
- シンプルで分かりやすい

採点履歴が必要な場合は、別途履歴機能を追加することも可能です。

