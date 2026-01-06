#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表彰状文章生成ユーティリティ
各賞に適した表彰状の文章を生成します。
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from utils.data_manager import get_evaluation_details, get_all_criteria


def _get_high_score_criteria(result_id: Optional[int], threshold: int = 8) -> List[Dict[str, Any]]:
    """
    高いスコアを獲得した評価項目を取得
    
    Args:
        result_id: 採点結果ID（Noneの場合は空リストを返す）
        threshold: 閾値（このスコア以上を「高い」とみなす）
    
    Returns:
        high_score_criteria: 高いスコアを獲得した評価項目のリスト
    """
    if result_id is None:
        return []
    
    try:
        details = get_evaluation_details(result_id)
        criteria = get_all_criteria()
        criteria_dict = {c['id']: c for c in criteria}
        
        high_score_items = []
        for detail in details:
            score = detail.get('score', 0)
            if score >= threshold:
                criterion_id = detail.get('criterion_id')
                criterion = criteria_dict.get(criterion_id)
                if criterion:
                    high_score_items.append({
                        'criterion_name': criterion.get('criterion_name', ''),
                        'score': score,
                        'max_score': criterion.get('max_score', 10)
                    })
        
        # スコア順にソート（高い順）
        high_score_items.sort(key=lambda x: x['score'], reverse=True)
        return high_score_items
    except Exception:
        # エラーが発生した場合は空リストを返す
        return []


def _generate_highlight_text(high_score_items: List[Dict[str, Any]], award_type: str) -> str:
    """
    高いスコアの評価項目に基づいて、表彰状に組み込む文章を生成
    
    Args:
        high_score_items: 高いスコアを獲得した評価項目のリスト
        award_type: 賞の種類
    
    Returns:
        highlight_text: 特徴的な数値を組み込んだ文章
    """
    if not high_score_items:
        return ""
    
    # 評価項目名とスコアのマッピング
    criterion_descriptions = {
        "着眼点の独創性": "独創的な視点",
        "背景のリアリティ": "実体験に基づく背景",
        "データ活用の適切性": "データの適切な活用",
        "分析の論理性": "論理的な分析",
        "実践可能性": "実践的な提案",
        "発表の明確性": "明確な発表"
    }
    
    # 最優秀賞の場合
    if award_type == "最優秀賞":
        if len(high_score_items) >= 2:
            top_items = high_score_items[:2]
            descriptions = []
            for item in top_items:
                criterion_name = item['criterion_name']
                score = item['score']
                desc = criterion_descriptions.get(criterion_name, criterion_name)
                descriptions.append(f"{desc}（{score}点）")
            
            if len(descriptions) == 2:
                return f"{descriptions[0]}と{descriptions[1]}において、"
        elif len(high_score_items) == 1:
            item = high_score_items[0]
            criterion_name = item['criterion_name']
            score = item['score']
            desc = criterion_descriptions.get(criterion_name, criterion_name)
            return f"{desc}（{score}点）において、"
        return "各評価項目において、"
    
    # 優秀賞の場合
    elif award_type == "優秀賞":
        if high_score_items:
            top_item = high_score_items[0]
            criterion_name = top_item['criterion_name']
            score = top_item['score']
            desc = criterion_descriptions.get(criterion_name, criterion_name)
            return f"{desc}（{score}点）をはじめ、"
        return ""
    
    # 特別審査員賞の場合
    elif award_type == "特別審査員賞":
        if high_score_items:
            # 独創性や創造性に関連する項目を優先
            creativity_items = [item for item in high_score_items 
                              if "独創" in item['criterion_name'] or "創造" in item['criterion_name']]
            if creativity_items:
                item = creativity_items[0]
                criterion_name = item['criterion_name']
                score = item['score']
                desc = criterion_descriptions.get(criterion_name, criterion_name)
                return f"{desc}（{score}点）をはじめ、"
            else:
                top_item = high_score_items[0]
                criterion_name = top_item['criterion_name']
                score = top_item['score']
                desc = criterion_descriptions.get(criterion_name, criterion_name)
                return f"{desc}（{score}点）をはじめ、"
        return ""
    
    return ""


def generate_certificate_text(
    school_name: str,
    theme_title: str,
    award_type: str,
    result_id: Optional[int] = None,
    total_score: Optional[int] = None,
    contest_name: str = "ピッチコンテスト"
) -> str:
    """
    表彰状の文章を生成
    
    Args:
        school_name: 学校名
        theme_title: テーマタイトル
        award_type: 賞の種類（"最優秀賞", "優秀賞", "特別審査員賞"）
        total_score: 総合スコア（オプション）
        contest_name: コンテスト名（デフォルト: "ピッチコンテスト"）
    
    Returns:
        certificate_text: 表彰状の文章
    """
    # 日付を取得（日本語形式）
    today = datetime.now()
    date_str = f"{today.year}年{today.month}月{today.day}日"
    
    # 高いスコアを獲得した評価項目を取得
    highlight_text = ""
    if result_id:
        high_score_items = _get_high_score_criteria(result_id, threshold=8)
        highlight_text = _generate_highlight_text(high_score_items, award_type)
    
    # 賞の種類に応じた文章を生成
    if award_type == "最優秀賞":
        if highlight_text:
            main_text = f"貴殿は本コンテストにおいて、{highlight_text}緻密な分析と独自の洞察を示し、極めて優れた成果を収められました。"
        else:
            main_text = "貴殿は本コンテストにおいて、緻密な分析と独自の洞察を示し、極めて優れた成果を収められました。"
        
        certificate_text = f"""
# 🏆 表彰状

**{school_name}** 様

{main_text}その卓越した探究心を讃え、ここに最優秀賞を贈り表彰します。

{date_str}

ピッチコンテスト実行委員会
"""
    
    elif award_type == "優秀賞":
        if highlight_text:
            main_text = f"貴殿は本コンテストにおいて、{highlight_text}論理的で説得力のある発表を行い、優秀な成績を収められました。"
        else:
            main_text = "貴殿は本コンテストにおいて、論理的で説得力のある発表を行い、優秀な成績を収められました。"
        
        certificate_text = f"""
# 🥇 表彰状

**{school_name}** 様

{main_text}その努力と成果を讃え、ここに優秀賞を贈り、これを表彰します。

{date_str}

ピッチコンテスト実行委員会
"""
    
    elif award_type == "特別審査員賞":
        if highlight_text:
            main_text = f"貴殿は本コンテストにおいて、{highlight_text}独自の視点と熱意溢れる探究姿勢を示し、強い印象を残す発表を行いました。"
        else:
            main_text = "貴殿は本コンテストにおいて、独自の視点と熱意溢れる探究姿勢を示し、強い印象を残す発表を行いました。"
        
        certificate_text = f"""
# ⭐ 表彰状

**{school_name}** 様

{main_text}その創造性を高く評価し、ここに特別審査員賞を贈ります。

{date_str}

ピッチコンテスト実行委員会
"""
    
    else:
        # デフォルトの表彰状
        certificate_text = f"""
# 🏅 表彰状

**{school_name}** 様

この度、{contest_name}において、貴校の取り組み「**{theme_title}**」が、優れた成果を収められたことを認め、ここに**{award_type}**を授与いたします。

貴校の探究活動は、SPLYZAMotionのデータを活用した分析と、その結果に基づく実践的な提案が高く評価されました。

今後とも、スポーツ探究活動を通じて、さらなる成長と発展を期待しております。

{date_str}

ピッチコンテスト実行委員会
"""
    
    return certificate_text.strip()


def generate_certificate_for_result(
    result: Dict[str, Any],
    award_types: List[str],
    all_results: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    採点結果に基づいて表彰状の文章を生成
    
    Args:
        result: 採点結果の辞書
        award_types: 授与された賞の種類のリスト（例: ["最優秀賞", "優秀賞"]）
        all_results: すべての採点結果のリスト（ランキング判定用）
    
    Returns:
        certificates: {賞の種類: 表彰状の文章} の辞書
    """
    school_name = result.get('school_name', '不明')
    theme_title = result.get('theme_title', '不明')
    total_score = result.get('total_score')
    result_id = result.get('id')
    
    certificates = {}
    
    for award_type in award_types:
        # 賞の種類から絵文字を除去（表示用）
        clean_award_type = award_type.replace('🏆 ', '').replace('🥇 ', '').replace('⭐ ', '')
        
        certificate_text = generate_certificate_text(
            school_name=school_name,
            theme_title=theme_title,
            award_type=clean_award_type,
            result_id=result_id,
            total_score=total_score
        )
        
        certificates[award_type] = certificate_text
    
    return certificates

