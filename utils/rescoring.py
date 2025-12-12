#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
再採点ユーティリティ
既存の提出資料を使って再採点を実行します。
"""

from pathlib import Path
from utils.data_manager import (
    get_submission, get_files_by_submission, create_evaluation_result,
    create_evaluation_detail, update_evaluation_result, get_all_criteria,
    get_all_evaluation_results, delete_evaluation_details
)
from utils.file_processor import extract_text_from_file
from utils.ai_scoring import evaluate_criterion, is_api_configured


def rescore_submission(submission_id: int) -> dict:
    """
    提出資料を再採点する（既存の採点結果を上書き）
    
    Args:
        submission_id: 提出資料ID
    
    Returns:
        dict: 採点結果（result_id, total_score, success, error）
    """
    if not is_api_configured():
        return {
            "success": False,
            "error": "APIキーが設定されていません"
        }
    
    # 提出資料を取得
    submission = get_submission(submission_id)
    if not submission:
        return {
            "success": False,
            "error": "提出資料が見つかりません"
        }
    
    # ファイルを取得
    files = get_files_by_submission(submission_id)
    if not files:
        return {
            "success": False,
            "error": "ファイルが見つかりません"
        }
    
    try:
        # ファイルからテキストを抽出
        all_text = ""
        for file_info in files:
            file_path = Path(file_info['file_path'])
            if file_path.exists():
                try:
                    text = extract_text_from_file(file_path)
                    all_text += f"\n\n=== {file_info['file_name']} ===\n\n{text}"
                except Exception as e:
                    # テキスト抽出に失敗しても続行
                    pass
        
        if not all_text.strip():
            return {
                "success": False,
                "error": "テキストを抽出できませんでした"
            }
        
        # 既存の採点結果を取得（最新のもの）
        all_results = get_all_evaluation_results()
        existing_results = [
            r for r in all_results 
            if r.get('submission_id') == submission_id 
            and r.get('evaluation_status') == 'completed'
        ]
        
        if existing_results:
            # 既存の結果がある場合は上書き
            # 最新の結果を取得（日付順）
            latest_result = max(
                existing_results,
                key=lambda x: x.get('evaluated_at', '') or ''
            )
            result_id = latest_result.get('id')
            
            # 既存の評価詳細を削除
            delete_evaluation_details(result_id)
        else:
            # 既存の結果がない場合は新規作成
            result_id = create_evaluation_result(submission_id,
                                                evaluated_by=None,
                                                ai_model="gpt-4")
        
        # 各評価項目について採点
        criteria = get_all_criteria()
        total_score = 0
        
        for criterion in criteria:
            try:
                result = evaluate_criterion(all_text, criterion['id'])
                score = result.get('score', 0)
                reason = result.get('reason', '')
                
                create_evaluation_detail(result_id, criterion['id'],
                                       score, reason)
                total_score += score
            except Exception as e:
                # エラーが発生した場合は0点を記録
                create_evaluation_detail(result_id, criterion['id'], 0,
                                       f"採点エラー: {str(e)}")
        
        # 採点結果を更新
        update_evaluation_result(result_id, total_score, "completed")
        
        return {
            "success": True,
            "result_id": result_id,
            "total_score": total_score,
            "overwritten": len(existing_results) > 0
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

