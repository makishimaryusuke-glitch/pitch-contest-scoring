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
        
        # 敢闘賞（4-5位）
        elif idx in [3, 4]:
            award_list.append("🥈 敢闘賞")
        
        # 奨励賞（6位以下）
        elif idx >= 5:
            award_list.append("🥉 奨励賞")
        
        if award_list:
            awards[result_id] = award_list
    
    # 評価項目ベースの賞の判定
    criteria = get_all_criteria()
    
    # 着眼点の独創性（評価項目ID: 1）で最高得点を獲得した作品
    creativity_scores = []
    for result in completed_results:
        details = get_evaluation_details(result.get('id'))
        for detail in details:
            if detail.get('criterion_id') == 1:  # 着眼点の独創性
                creativity_scores.append({
                    'result_id': result.get('id'),
                    'score': detail.get('score', 0)
                })
                break
    
    if creativity_scores:
        max_creativity_score = max(s['score'] for s in creativity_scores)
        creativity_winners = [s['result_id'] for s in creativity_scores 
                            if s['score'] == max_creativity_score]
        
        for result_id in creativity_winners:
            if result_id not in awards:
                awards[result_id] = []
            awards[result_id].append("💡 独創性賞")
    
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

