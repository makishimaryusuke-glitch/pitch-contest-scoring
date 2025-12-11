#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ永続化ヘルパー
Streamlit Cloudでのデータ永続化をサポートします。
"""

import streamlit as st
from pathlib import Path
from utils.data_manager import DATA_DIR, SCHOOLS_FILE, SUBMISSIONS_FILE, EVALUATION_RESULTS_FILE, EVALUATION_DETAILS_FILE, FILES_FILE


def check_data_persistence():
    """
    データファイルが永続化されているか確認
    
    Returns:
        dict: 各データファイルの状態
    """
    data_files = {
        "参加校": SCHOOLS_FILE,
        "提出資料": SUBMISSIONS_FILE,
        "採点結果": EVALUATION_RESULTS_FILE,
        "採点詳細": EVALUATION_DETAILS_FILE,
        "ファイル情報": FILES_FILE,
    }
    
    status = {}
    for name, file_path in data_files.items():
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        status[name] = {
            "exists": exists,
            "size": size,
            "path": str(file_path)
        }
    
    return status


def show_data_persistence_info():
    """データ永続化に関する情報を表示"""
    st.info("""
    **データの永続化について**
    
    データは`data/`ディレクトリのJSONファイルに保存されます。
    
    **Streamlit Cloudでの注意事項：**
    - データファイルはGitリポジトリにコミットすることで永続化されます
    - データが変更された場合は、Gitにコミットしてください
    - 再デプロイ後もデータが保持されます
    
    **ローカル環境での注意事項：**
    - データファイルは`data/`ディレクトリに保存されます
    - ブラウザを閉じてもデータは保持されます
    """)
    
    # データファイルの状態を表示
    status = check_data_persistence()
    
    st.markdown("### データファイルの状態")
    for name, info in status.items():
        if info["exists"]:
            st.success(f"✅ {name}: {info['size']} bytes ({info['path']})")
        else:
            st.warning(f"⚠️ {name}: ファイルが存在しません")


def ensure_data_directory():
    """データディレクトリが存在することを確認"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 各データファイルが存在しない場合は空のリストで初期化
    from utils.data_manager import save_json
    
    if not SCHOOLS_FILE.exists():
        save_json(SCHOOLS_FILE, [])
    if not SUBMISSIONS_FILE.exists():
        save_json(SUBMISSIONS_FILE, [])
    if not EVALUATION_RESULTS_FILE.exists():
        save_json(EVALUATION_RESULTS_FILE, [])
    if not EVALUATION_DETAILS_FILE.exists():
        save_json(EVALUATION_DETAILS_FILE, [])
    if not FILES_FILE.exists():
        save_json(FILES_FILE, [])


