#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
賞判定ユーティリティ
採点結果に基づいて賞を自動判定します。
"""

from typing import Dict, List, Any
from utils.data_manager import get_all_evaluation_results, get_evaluation_details, get_all_criteria


def determine_awards(results: List[Dict[str, Any]]) -> Dict[int, List[str]]:
    """
    採点結果に基づいて賞を自動判定
    
    Args:
        results: 採点結果のリスト（evaluation_status='completed'のもの）
    
    Returns:
        awards: {result_id: [賞のリスト]} の辞書
    """
    if not results:
        return {}
    
    # 完了した採点結果のみを対象
    completed_results = [r for r in results if r.get("evaluation_status") == "completed"]
    if not completed_results:
        return {}
    
    awards = {}
    
    # 総合スコアでソート（高い順）
    sorted_results = sorted(completed_results, 
                           key=lambda x: x.get('total_score', 0), 
                           reverse=True)
    
    # 基本賞の判定
    for idx, result in enumerate(sorted_results):
        result_id = result.get('id')
        if result_id is None:
            continue
        
        award_list = []
        
        # 最優秀賞（1位）
        if idx == 0:
            award_list.append("🏆 最優秀賞")
        
        # 優秀賞（2-3位）
        elif idx in [1, 2]:
            award_list.append("🥇 優秀賞")
        
        # 特別審査員賞（手動設定）
        if result.get('special_judge_award', False):
            award_list.append("⭐ 特別審査員賞")
        
        if award_list:
            awards[result_id] = award_list
    
    return awards


def get_awards_for_result(result_id: int, all_results: List[Dict[str, Any]]) -> List[str]:
    """
    特定の採点結果に付与された賞を取得
    
    Args:
        result_id: 採点結果ID
        all_results: すべての採点結果のリスト
    
    Returns:
        awards: 賞のリスト
    """
    awards_dict = determine_awards(all_results)
    return awards_dict.get(result_id, [])


def format_awards_display(awards: List[str]) -> str:
    """
    賞のリストを表示用の文字列に変換
    
    Args:
        awards: 賞のリスト
    
    Returns:
        display_text: 表示用の文字列
    """
    if not awards:
        return ""
    return " / ".join(awards)


