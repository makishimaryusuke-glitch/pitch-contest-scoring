#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データのバックアップと復元機能
Streamlit Cloudでのデータ永続化をサポートします。
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from utils.data_manager import (
    DATA_DIR, SCHOOLS_FILE, SUBMISSIONS_FILE, 
    EVALUATION_RESULTS_FILE, EVALUATION_DETAILS_FILE, FILES_FILE,
    save_json, load_json
)


def create_backup() -> bytes:
    """
    すべてのデータファイルをZIP形式でバックアップ
    
    Returns:
        bytes: ZIPファイルのバイトデータ
    """
    backup_data = {
        "backup_date": datetime.now().isoformat(),
        "version": "1.0",
        "data": {}
    }
    
    # 各データファイルを読み込んでバックアップデータに追加
    data_files = {
        "schools": SCHOOLS_FILE,
        "submissions": SUBMISSIONS_FILE,
        "evaluation_results": EVALUATION_RESULTS_FILE,
        "evaluation_details": EVALUATION_DETAILS_FILE,
        "files": FILES_FILE,
    }
    
    for key, file_path in data_files.items():
        if file_path.exists():
            backup_data["data"][key] = load_json(file_path)
        else:
            backup_data["data"][key] = []
    
    # ZIPファイルとして作成
    import io
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # メタデータファイル
        zip_file.writestr(
            "backup_metadata.json",
            json.dumps(backup_data, ensure_ascii=False, indent=2)
        )
        
        # 各データファイル
        for key, file_path in data_files.items():
            if file_path.exists():
                zip_file.write(file_path, f"{key}.json")
            else:
                # ファイルが存在しない場合は空のリストを保存
                zip_file.writestr(
                    f"{key}.json",
                    json.dumps([], ensure_ascii=False, indent=2)
                )
    
    zip_buffer.seek(0)
    return zip_buffer.read()


def restore_backup(backup_file: bytes) -> Dict[str, Any]:
    """
    バックアップファイルからデータを復元
    
    Args:
        backup_file: ZIPファイルのバイトデータ
        
    Returns:
        dict: 復元結果の情報
    """
    import io
    
    result = {
        "success": False,
        "restored_files": [],
        "errors": [],
        "backup_date": None
    }
    
    try:
        zip_buffer = io.BytesIO(backup_file)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
            # メタデータを読み込む
            if "backup_metadata.json" in zip_file.namelist():
                metadata_str = zip_file.read("backup_metadata.json").decode('utf-8')
                metadata = json.loads(metadata_str)
                result["backup_date"] = metadata.get("backup_date")
            
            # 各データファイルを復元
            data_files = {
                "schools": SCHOOLS_FILE,
                "submissions": SUBMISSIONS_FILE,
                "evaluation_results": EVALUATION_RESULTS_FILE,
                "evaluation_details": EVALUATION_DETAILS_FILE,
                "files": FILES_FILE,
            }
            
            for key, file_path in data_files.items():
                json_filename = f"{key}.json"
                if json_filename in zip_file.namelist():
                    try:
                        data_str = zip_file.read(json_filename).decode('utf-8')
                        data = json.loads(data_str)
                        save_json(file_path, data)
                        result["restored_files"].append(key)
                    except Exception as e:
                        result["errors"].append(f"{key}: {str(e)}")
            
            result["success"] = len(result["restored_files"]) > 0
            
    except Exception as e:
        result["errors"].append(f"バックアップファイルの読み込みエラー: {str(e)}")
    
    return result


def get_backup_info() -> Dict[str, Any]:
    """
    現在のデータファイルの情報を取得
    
    Returns:
        dict: データファイルの情報
    """
    data_files = {
        "schools": ("参加校", SCHOOLS_FILE),
        "submissions": ("提出資料", SUBMISSIONS_FILE),
        "evaluation_results": ("採点結果", EVALUATION_RESULTS_FILE),
        "evaluation_details": ("採点詳細", EVALUATION_DETAILS_FILE),
        "files": ("ファイル情報", FILES_FILE),
    }
    
    info = {
        "total_files": 0,
        "total_size": 0,
        "files": []
    }
    
    for key, (name, file_path) in data_files.items():
        if file_path.exists():
            data = load_json(file_path)
            file_size = file_path.stat().st_size
            info["total_files"] += 1
            info["total_size"] += file_size
            info["files"].append({
                "key": key,
                "name": name,
                "path": str(file_path),
                "size": file_size,
                "count": len(data),
                "exists": True
            })
        else:
            info["files"].append({
                "key": key,
                "name": name,
                "path": str(file_path),
                "size": 0,
                "count": 0,
                "exists": False
            })
    
    return info
