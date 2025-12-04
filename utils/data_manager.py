#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ管理ユーティリティ（CSV/JSONファイルベース）
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# データディレクトリ
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ファイルパス
SCHOOLS_FILE = DATA_DIR / "schools.json"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
EVALUATION_RESULTS_FILE = DATA_DIR / "evaluation_results.json"
EVALUATION_DETAILS_FILE = DATA_DIR / "evaluation_details.json"
FILES_FILE = DATA_DIR / "files.json"

def load_json(file_path: Path, default: List = None) -> List[Dict[str, Any]]:
    """JSONファイルを読み込む"""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else []

def save_json(file_path: Path, data: List[Dict[str, Any]]):
    """JSONファイルに保存"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_id(data_list: List[Dict[str, Any]]) -> int:
    """次のIDを取得"""
    if not data_list:
        return 1
    return max(item.get('id', 0) for item in data_list) + 1

# ==================== Schools ====================

def create_school(name: str, prefecture: Optional[str] = None,
                  contact_email: Optional[str] = None,
                  contact_name: Optional[str] = None) -> int:
    """参加校を作成"""
    schools = load_json(SCHOOLS_FILE)
    school_id = get_next_id(schools)
    school = {
        "id": school_id,
        "name": name,
        "prefecture": prefecture,
        "contact_email": contact_email,
        "contact_name": contact_name,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    schools.append(school)
    save_json(SCHOOLS_FILE, schools)
    return school_id

def get_school(school_id: int) -> Optional[Dict[str, Any]]:
    """参加校を取得"""
    schools = load_json(SCHOOLS_FILE)
    return next((s for s in schools if s['id'] == school_id), None)

def get_all_schools() -> List[Dict[str, Any]]:
    """すべての参加校を取得"""
    return load_json(SCHOOLS_FILE)

# ==================== Submissions ====================

def create_submission(school_id: int, theme_title: str,
                     theme_description: Optional[str] = None) -> int:
    """提出資料を作成"""
    submissions = load_json(SUBMISSIONS_FILE)
    submission_id = get_next_id(submissions)
    submission = {
        "id": submission_id,
        "school_id": school_id,
        "theme_title": theme_title,
        "theme_description": theme_description,
        "submission_status": "pending",
        "submitted_at": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    submissions.append(submission)
    save_json(SUBMISSIONS_FILE, submissions)
    return submission_id

def get_submission(submission_id: int) -> Optional[Dict[str, Any]]:
    """提出資料を取得"""
    submissions = load_json(SUBMISSIONS_FILE)
    submission = next((s for s in submissions if s['id'] == submission_id), None)
    if submission:
        school = get_school(submission['school_id'])
        if school:
            submission['school_name'] = school['name']
    return submission

def get_all_submissions() -> List[Dict[str, Any]]:
    """すべての提出資料を取得"""
    submissions = load_json(SUBMISSIONS_FILE)
    schools = {s['id']: s['name'] for s in get_all_schools()}
    for submission in submissions:
        submission['school_name'] = schools.get(submission['school_id'], '不明')
    return submissions

def update_submission_status(submission_id: int, status: str):
    """提出資料のステータスを更新"""
    submissions = load_json(SUBMISSIONS_FILE)
    for submission in submissions:
        if submission['id'] == submission_id:
            submission['submission_status'] = status
            submission['updated_at'] = datetime.now().isoformat()
            break
    save_json(SUBMISSIONS_FILE, submissions)

# ==================== Files ====================

def create_file(submission_id: int, file_name: str, file_path: str,
                file_type: str, file_size: int) -> int:
    """ファイル情報を作成"""
    files = load_json(FILES_FILE)
    file_id = get_next_id(files)
    file_data = {
        "id": file_id,
        "submission_id": submission_id,
        "file_name": file_name,
        "file_path": file_path,
        "file_type": file_type,
        "file_size": file_size,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    files.append(file_data)
    save_json(FILES_FILE, files)
    return file_id

def get_files_by_submission(submission_id: int) -> List[Dict[str, Any]]:
    """提出資料に紐づくファイルを取得"""
    files = load_json(FILES_FILE)
    return [f for f in files if f['submission_id'] == submission_id]

# ==================== Evaluation Results ====================

def create_evaluation_result(submission_id: int, evaluated_by: Optional[int] = None,
                            ai_model: Optional[str] = None) -> int:
    """採点結果を作成"""
    results = load_json(EVALUATION_RESULTS_FILE)
    result_id = get_next_id(results)
    result = {
        "id": result_id,
        "submission_id": submission_id,
        "total_score": 0,
        "max_score": 60,
        "evaluation_status": "processing",
        "evaluated_by": evaluated_by,
        "evaluated_at": None,
        "ai_model": ai_model,
        "evaluation_notes": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    results.append(result)
    save_json(EVALUATION_RESULTS_FILE, results)
    return result_id

def update_evaluation_result(result_id: int, total_score: int, status: str,
                             evaluation_notes: Optional[str] = None):
    """採点結果を更新"""
    results = load_json(EVALUATION_RESULTS_FILE)
    for result in results:
        if result['id'] == result_id:
            result['total_score'] = total_score
            result['evaluation_status'] = status
            result['evaluation_notes'] = evaluation_notes
            result['evaluated_at'] = datetime.now().isoformat()
            result['updated_at'] = datetime.now().isoformat()
            break
    save_json(EVALUATION_RESULTS_FILE, results)

def create_evaluation_detail(result_id: int, criterion_id: int,
                             score: int, evaluation_reason: str) -> int:
    """採点結果詳細を作成"""
    details = load_json(EVALUATION_DETAILS_FILE)
    detail_id = get_next_id(details)
    detail = {
        "id": detail_id,
        "evaluation_result_id": result_id,
        "criterion_id": criterion_id,
        "score": score,
        "evaluation_reason": evaluation_reason,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    details.append(detail)
    save_json(EVALUATION_DETAILS_FILE, details)
    return detail_id

def get_evaluation_result(result_id: int) -> Optional[Dict[str, Any]]:
    """採点結果を取得"""
    results = load_json(EVALUATION_RESULTS_FILE)
    result = next((r for r in results if r['id'] == result_id), None)
    if result:
        submission = get_submission(result['submission_id'])
        if submission:
            result['theme_title'] = submission['theme_title']
            result['school_name'] = submission.get('school_name', '不明')
    return result

def get_evaluation_details(result_id: int) -> List[Dict[str, Any]]:
    """採点結果詳細を取得"""
    details = load_json(EVALUATION_DETAILS_FILE)
    result_details = [d for d in details if d['evaluation_result_id'] == result_id]
    
    # 評価基準情報を追加
    criteria = get_all_criteria()
    criteria_dict = {c['id']: c for c in criteria}
    
    for detail in result_details:
        criterion = criteria_dict.get(detail['criterion_id'])
        if criterion:
            detail['criterion_name'] = criterion['criterion_name']
            detail['criterion_description'] = criterion['description']
    
    # display_orderでソート
    result_details.sort(key=lambda x: criteria_dict.get(x['criterion_id'], {}).get('display_order', 0))
    return result_details

def get_all_evaluation_results() -> List[Dict[str, Any]]:
    """すべての採点結果を取得"""
    results = load_json(EVALUATION_RESULTS_FILE)
    submissions = {s['id']: s for s in get_all_submissions()}
    
    for result in results:
        submission = submissions.get(result['submission_id'])
        if submission:
            result['theme_title'] = submission['theme_title']
            result['school_name'] = submission.get('school_name', '不明')
    
    return results

# ==================== Evaluation Criteria ====================

def get_all_criteria() -> List[Dict[str, Any]]:
    """すべての評価基準を取得"""
    # 評価基準は固定データとして定義
    return [
        {"id": 1, "category": "事前審査", "criterion_name": "着眼点の独創性",
         "description": "既存の枠にとらわれない、高校生らしい柔軟な発想やユニークな視点があるか",
         "max_score": 10, "display_order": 1},
        {"id": 2, "category": "事前審査", "criterion_name": "背景のリアリティ",
         "description": "「なぜ自分がこの課題に取り組むのか」という動機が明確で、自らの実体験や現場の課題感に基づいた「当事者意識」が感じられるか",
         "max_score": 10, "display_order": 2},
        {"id": 3, "category": "事前審査", "criterion_name": "仮説検証の適切性",
         "description": "問いに対して適切な仮説を立て、SPLYZAMotion等のデータを活用して客観的かつ科学的に検証できているか",
         "max_score": 10, "display_order": 3},
        {"id": 4, "category": "事前審査", "criterion_name": "分析の深さ",
         "description": "結果を単に述べるだけでなく、「なぜそうなったのか」を深く考察し、論理的に結論を導き出せているか",
         "max_score": 10, "display_order": 4},
        {"id": 5, "category": "事前審査", "criterion_name": "現場への還元",
         "description": "その探究結果が、自分たちのチーム強化や競技力の向上にどう具体的に役立つか",
         "max_score": 10, "display_order": 5},
        {"id": 6, "category": "事前審査", "criterion_name": "波及効果",
         "description": "他のチームや競技、あるいはスポーツ界全体に対して、どのような新しい知見や価値を提供できるか",
         "max_score": 10, "display_order": 6},
    ]

