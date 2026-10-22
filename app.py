#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ピッチコンテストAI採点システム - メインアプリケーション（シンプル版）
CSV/JSONファイル管理。APP_ACCESS_PASSWORD がある環境だけ合言葉を要求する。
"""

import streamlit as st
from pathlib import Path
from utils.data_manager import *
from utils.file_processor import *
from utils.ai_scoring import *
from utils.visualization import *
from utils.award_manager import determine_awards, format_awards_display
from utils.data_persistence_helper import ensure_data_directory, show_data_persistence_info, check_data_persistence
from utils.rescoring import rescore_submission
from utils.certificate_generator import generate_certificate_for_result
from utils.backup_restore import create_backup, restore_backup, get_backup_info
from utils.access_gate import require_access
import pandas as pd

# 環境変数からAPIキーを初期化（Streamlit Cloud用）
initialize_from_env()

# データディレクトリの初期化（永続化のため）
ensure_data_directory()

# ページ設定
st.set_page_config(
    page_title="ピッチコンテストAI採点システム",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

require_access()

# APIキーの設定（セッション状態）
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = "openai"

# ページナビゲーション（セッション状態で管理）
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 ダッシュボード"  # デフォルトページ

# サイドバーにメニューバーを作成
st.sidebar.title("📋 メニュー")

# メニューオプション
pages = [
    "🏠 ダッシュボード",
    "⚙️ API設定",
    "📝 採点ワークフロー",
    "🏫 参加校管理",
    "💾 データ管理"
]

# radioボタンでページ選択（選択状態が視覚的に分かる）
selected_page = st.sidebar.radio(
    "ページを選択",
    pages,
    index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
    label_visibility="collapsed"
)

# ページが変更されたらセッション状態を更新
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    st.rerun()

# 現在のページを取得
page = st.session_state.current_page

# API設定ページ
if page == "⚙️ API設定":
    st.title("⚙️ API設定")
    
    # 環境変数からAPIキーが設定されているか確認
    env_provider = get_api_provider_from_env()
    if env_provider:
        st.success("✅ 環境変数からAPIキーが設定されています（Streamlit Cloud Secrets）")
        st.info(f"現在のプロバイダー: {env_provider}")
        st.markdown("---")
        st.markdown("### 環境変数の設定方法")
        st.markdown("""
        Streamlit Cloudのダッシュボードで：
        1. 「Manage app」→「Settings」→「Secrets」を開く
        2. 以下の形式で設定：
        
        **OpenAIの場合：**
        ```toml
        OPENAI_API_KEY = "your-api-key"
        AI_PROVIDER = "openai"
        ```
        
        **Google Geminiの場合：**
        ```toml
        GOOGLE_API_KEY = "your-api-key"
        AI_PROVIDER = "gemini"
        ```
        """)
    else:
        st.info("AI採点機能を使用するには、OpenAIまたはGoogle GeminiのAPIキーが必要です。")
        st.markdown("---")
        st.markdown("### 方法1: アプリ内で設定（一時的）")
        st.warning("⚠️ ブラウザを閉じると消えます")
        
        # APIキーを先に入力してもらう
        api_key = st.text_input("APIキーを入力", type="password", 
                               help="OpenAI APIキー（sk-...で始まる）またはGoogle Gemini APIキー（AIzaSy...で始まる）")
        
        # APIキーが入力されたら、自動検出を試みる
        detected_provider = None
        if api_key:
            try:
                from utils.ai_scoring import detect_api_provider
                detected_provider = detect_api_provider(api_key)
                if detected_provider == "openai":
                    st.info("🔍 OpenAI APIキーを検出しました")
                elif detected_provider == "gemini":
                    st.info("🔍 Google Gemini APIキーを検出しました")
            except:
                pass
        
        # プロバイダー選択（自動検出された場合はそれをデフォルトに）
        provider_options = ["openai", "gemini"]
        default_index = 0
        if detected_provider == "gemini":
            default_index = 1
        
        provider = st.selectbox(
            "AIプロバイダーを選択（自動検出された場合はそのまま）", 
            provider_options,
            index=default_index,
            help="APIキーの形式から自動検出されますが、手動で変更することもできます"
        )
        
        if st.button("APIキーを設定"):
            if api_key:
                try:
                    set_api_key(api_key, provider)
                    st.session_state.api_key_set = True
                    st.session_state.api_provider = provider
                    st.success("✅ APIキーが設定されました（ブラウザを閉じると消えます）")
                except Exception as e:
                    st.error(f"エラー: {str(e)}")
                    # より詳細なエラーメッセージを表示
                    if "形式が正しくありません" in str(e):
                        st.info("💡 ヒント: APIキーの形式を確認してください。")
                        st.markdown("- OpenAI APIキー: `sk-`で始まります")
                        st.markdown("- Google Gemini APIキー: `AIzaSy`で始まります")
            else:
                st.warning("APIキーを入力してください")
        
        st.markdown("---")
        st.markdown("### 方法2: Streamlit Cloud Secretsで設定（推奨・永続的）")
        st.markdown("""
        Streamlit Cloudのダッシュボードで：
        1. 「Manage app」→「Settings」→「Secrets」を開く
        2. 以下の形式で設定：
        
        **OpenAIの場合：**
        ```toml
        OPENAI_API_KEY = "your-api-key"
        AI_PROVIDER = "openai"
        ```
        
        **Google Geminiの場合：**
        ```toml
        GOOGLE_API_KEY = "your-api-key"
        AI_PROVIDER = "gemini"
        ```
        
        3. 「Save」をクリック
        
        **メリット：**
        - 一度設定すれば、ブラウザを閉じても保持されます
        - セキュアに暗号化されて保存されます
        """)
    
    # APIキーの状態確認
    st.markdown("---")
    if is_api_configured():
        st.success("✅ APIキーが設定されています")
    else:
        st.warning("⚠️ APIキーが設定されていません。上記で設定してください。")

# ダッシュボード
if page == "🏠 ダッシュボード":
    st.title("📊 ダッシュボード")
    
    # 統計情報
    col1, col2, col3, col4 = st.columns(4)
    
    schools = get_all_schools()
    submissions = get_all_submissions()
    results = get_all_evaluation_results()
    completed_results = [r for r in results if r["evaluation_status"] == "completed"]
    
    with col1:
        st.metric("参加校数", len(schools))
    with col2:
        st.metric("提出資料数", len(submissions))
    with col3:
        st.metric("採点完了数", len(completed_results))
    with col4:
        avg_score = sum(r["total_score"] for r in completed_results) / len(completed_results) if completed_results else 0
        st.metric("平均スコア", f"{avg_score:.1f}/60")
    
    # データ変更の通知とバックアップ推奨
    if st.session_state.get('data_changed', False):
        st.warning("""
        ⚠️ **データが変更されました**
        
        データを失わないために、バックアップをダウンロードすることをお勧めします。
        「💾 データ管理」ページからバックアップをダウンロードできます。
        """)
        if st.button("💾 データ管理ページへ移動", key="go_to_data_management"):
            st.session_state.current_page = "💾 データ管理"
            st.rerun()
    
    # データ永続化の状態を表示（折りたたみ可能）
    with st.expander("📁 データ永続化の状態", expanded=False):
        show_data_persistence_info()
    
    # ランキング表示（総合スコア順）
    st.subheader("🏆 採点結果ランキング")
    
    # デバッグ情報を表示
    with st.expander("🔍 デバッグ情報", expanded=True):
        st.write(f"completed_results数: {len(completed_results)}")
        if completed_results:
            st.write("最初のcompleted_resultの内容:")
            st.json(completed_results[0])
    
    if completed_results:
        # 総合スコアでソート（高い順）
        sorted_results = sorted(completed_results, 
                               key=lambda x: x.get('total_score', 0), 
                               reverse=True)
        
        # デバッグ情報
        with st.expander("🔍 デバッグ情報（ソート後）", expanded=True):
            st.write(f"sorted_results数: {len(sorted_results)}")
            if sorted_results:
                st.write("最初のsorted_resultの内容:")
                st.json(sorted_results[0])
        
        # 賞を判定
        awards_dict = determine_awards(completed_results)
        
        # ランキングデータを作成
        ranking_data = []
        for rank, result in enumerate(sorted_results, 1):
            result_id = result.get('id')
            school_name = result.get('school_name', '不明')
            theme_title = result.get('theme_title', '不明')
            total_score = result.get('total_score', 0)
            
            # 賞を取得
            awards = awards_dict.get(result_id, [])
            awards_text = format_awards_display(awards)
            
            # 校名と賞を結合
            school_with_award = school_name
            if awards_text:
                school_with_award = f"{school_name} {awards_text}"
            
            ranking_data.append({
                "順位": rank,
                "参加校": school_with_award,
                "テーマ": theme_title,
                "総合スコア": f"{total_score}/60",
                "result_id": result_id if result_id is not None else 0  # 削除用にIDを保持
            })
        
        # ランキングテーブルを表示（result_idは非表示）
        df_ranking = pd.DataFrame(ranking_data)
        df_display = df_ranking[["順位", "参加校", "テーマ", "総合スコア"]].copy()
        st.dataframe(df_display, width='stretch', use_container_width=True, hide_index=True)
        
        # 削除ボタンを各行に追加
        st.markdown("---")
        st.markdown("### 🗑️ 採点結果の削除")
        
        # デバッグ情報
        st.write(f"**削除ボタン表示前の確認**: sorted_results数={len(sorted_results)}")
        
        # 各行に削除ボタンを追加（sorted_resultsを直接使用）
        if len(sorted_results) == 0:
            st.info("削除対象の採点結果がありません")
        else:
            st.write(f"**削除ボタンのループ開始**: {len(sorted_results)}件の結果に対してループを実行します")
            # テーブル形式で削除ボタンを表示
            for rank_idx, result in enumerate(sorted_results, 1):
                result_id = result.get('id')
                school_name = result.get('school_name', '不明')
                theme_title = result.get('theme_title', '不明')
                total_score = result.get('total_score', 0)
                
                # result_idがNoneの場合はスキップ
                if result_id is None:
                    st.warning(f"⚠️ {rank_idx}位: result_idがNoneです（スキップします）")
                    continue
                
                # デバッグ情報
                st.write(f"**処理中**: {rank_idx}位 - {school_name} (result_id={result_id})")
                
                # 賞を取得
                awards = awards_dict.get(result_id, [])
                awards_text = format_awards_display(awards)
                school_with_award = school_name
                if awards_text:
                    school_with_award = f"{school_name} {awards_text}"
                
                # 確認状態をチェック
                if f"pending_delete_{result_id}" not in st.session_state:
                    st.session_state[f"pending_delete_{result_id}"] = False
                
                # 行を表示（より明確に表示）
                col1, col2, col3, col4 = st.columns([1, 3, 3, 3])
                with col1:
                    st.markdown(f"**{rank_idx}位**")
                with col2:
                    st.markdown(f"**{school_with_award}**")
                with col3:
                    st.markdown(theme_title)
                with col4:
                    delete_key = f"delete_ranking_{result_id}_{rank_idx}"
                    st.write(f"削除ボタンキー: {delete_key}")
                    
                    if st.session_state[f"pending_delete_{result_id}"]:
                        # 確認モード
                        st.warning(f"⚠️ 削除しますか？")
                        col_confirm1, col_confirm2 = st.columns(2)
                        with col_confirm1:
                            if st.button("✅ 確定", key=f"confirm_{delete_key}", type="primary"):
                                # 削除を実行
                                try:
                                    # 採点結果を取得してsubmission_idを取得
                                    result_obj = get_evaluation_result(result_id)
                                    submission_id = result_obj.get('submission_id') if result_obj else None
                                    
                                    # 採点結果を削除（評価詳細も自動削除される）
                                    if delete_evaluation_result(result_id):
                                        # 関連するファイルも削除（物理ファイルも削除）
                                        if submission_id:
                                            # ファイルの物理削除も実行
                                            files = get_files_by_submission(submission_id)
                                            for file_info in files:
                                                file_path = Path(file_info.get('file_path', ''))
                                                if file_path.exists():
                                                    try:
                                                        file_path.unlink()
                                                    except Exception as e:
                                                        st.warning(f"ファイル削除エラー: {e}")
                                            
                                            # ファイルメタデータを削除
                                            delete_files_by_submission(submission_id)
                                        
                                        st.success(f"✅ 「{school_name}」の採点結果を削除しました")
                                        st.session_state[f"pending_delete_{result_id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("削除に失敗しました")
                                        st.session_state[f"pending_delete_{result_id}"] = False
                                except Exception as e:
                                    st.error(f"削除中にエラーが発生しました: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
                                    st.session_state[f"pending_delete_{result_id}"] = False
                        with col_confirm2:
                            if st.button("❌ キャンセル", key=f"cancel_{delete_key}"):
                                st.session_state[f"pending_delete_{result_id}"] = False
                                st.rerun()
                    else:
                        # 通常モード - ボタンを目立たせる
                        if st.button("🗑️ 削除", key=delete_key, type="secondary", use_container_width=True):
                            st.session_state[f"pending_delete_{result_id}"] = True
                            st.rerun()
                
                st.divider()
        
        # 賞の説明
        st.markdown("---")
        st.markdown("### 賞の説明")
        st.markdown("""
        - 🏆 **最優秀賞**: 総合スコア1位
        - 🥇 **優秀賞**: 総合スコア2-3位
        - ⭐ **特別審査員賞**: 審査員が特別に選定（手動設定）
        """)
        
        # 表彰状表示セクション
        st.markdown("---")
        st.subheader("📜 表彰状")
        
        # 賞を獲得した学校の表彰状を表示
        award_winners = []
        for result_id, awards in awards_dict.items():
            if awards:
                result = next((r for r in sorted_results if r.get('id') == result_id), None)
                if result:
                    award_winners.append((result, awards))
        
        if award_winners:
            for result, awards in award_winners:
                school_name = result.get('school_name', '不明')
                theme_title = result.get('theme_title', '不明')
                
                with st.expander(f"🏆 {school_name} - {theme_title}", expanded=False):
                    certificates = generate_certificate_for_result(
                        result,
                        awards,
                        completed_results
                    )
                    
                    for award_type, certificate_text in certificates.items():
                        st.markdown(certificate_text)
                        st.markdown("---")
        else:
            st.info("まだ賞を獲得した学校がありません。")
    else:
        st.info("まだ採点結果がありません")

# 採点ワークフロー（1ページに統合）
elif page == "📝 採点ワークフロー":
    st.title("📝 採点ワークフロー")
    
    # 再採点モードの確認
    is_rescore_mode = 'rescore_school_id' in st.session_state and st.session_state.rescore_school_id is not None
    
    if is_rescore_mode:
        st.info("🔄 再採点モード: ファイルを再アップロードして採点を実行してください。")
    
    # セッション状態で前回選択した参加校を追跡
    if 'previous_school_id' not in st.session_state:
        st.session_state.previous_school_id = None
    
    # 1. 参加校の選択
    st.subheader("1. 参加校を選択")
    schools = get_all_schools()
    if not schools:
        st.warning("参加校が登録されていません。「🏫 参加校管理」ページで参加校を登録してください。")
        st.stop()
    
    school_options = {f"{s['name']} ({s.get('prefecture', '')})": s['id'] for s in schools}
    
    # 再採点モードの場合は、対象の参加校を自動選択
    if is_rescore_mode:
        rescore_school_id = st.session_state.rescore_school_id
        # 参加校名を取得
        rescore_school = next((s for s in schools if s['id'] == rescore_school_id), None)
        if rescore_school:
            default_school = f"{rescore_school['name']} ({rescore_school.get('prefecture', '')})"
            selected_school = st.selectbox(
                "参加校を選択", 
                list(school_options.keys()), 
                index=list(school_options.keys()).index(default_school) if default_school in school_options else 0,
                key="workflow_school_select"
            )
        else:
            selected_school = st.selectbox("参加校を選択", list(school_options.keys()), key="workflow_school_select")
    else:
        selected_school = st.selectbox("参加校を選択", list(school_options.keys()), key="workflow_school_select")
    
        school_id = school_options[selected_school]
    
    # 再採点モードの場合、既存の提出資料情報を取得
    existing_submission = None
    if is_rescore_mode and 'rescore_submission_id' in st.session_state:
        existing_submission = get_submission(st.session_state.rescore_submission_id)
    
    # 参加校が変更されたらフォームをクリア（再採点モードでない場合）
    if not is_rescore_mode and st.session_state.previous_school_id is not None and st.session_state.previous_school_id != school_id:
        # フォームのキーをクリアするために、セッション状態をリセット
        if 'workflow_theme_title' in st.session_state:
            del st.session_state.workflow_theme_title
        if 'workflow_theme_description' in st.session_state:
            del st.session_state.workflow_theme_description
        if 'workflow_upload_files' in st.session_state:
            del st.session_state.workflow_upload_files
    
    # 再採点モードの場合、既存のテーマ情報を事前入力
    if is_rescore_mode and existing_submission:
        if 'workflow_theme_title' not in st.session_state:
            st.session_state.workflow_theme_title = existing_submission.get('theme_title', '')
        if 'workflow_theme_description' not in st.session_state:
            st.session_state.workflow_theme_description = existing_submission.get('theme_description', '')
    
    st.session_state.previous_school_id = school_id
    
    st.divider()
    
    # 2. テーマ情報とファイルのアップロード
    st.subheader("2. テーマ情報とファイルを入力")
    theme_title = st.text_input("テーマタイトル *", key="workflow_theme_title")
    theme_description = st.text_area("テーマ説明", key="workflow_theme_description")
    
    uploaded_files = st.file_uploader(
        "ファイルを選択（PDF、PowerPoint、テキスト）",
        type=['pdf', 'pptx', 'ppt', 'txt'],
        accept_multiple_files=True,
        key="workflow_upload_files"
    )
    
    st.divider()
    
    # 3. 実行ボタン
    st.subheader("3. 採点を実行")
    
    # APIキーの確認
    if not is_api_configured():
        st.warning("⚠️ APIキーが設定されていません。「⚙️ API設定」ページでAPIキーを設定してください。")
    
    # 実行ボタン
    execute_disabled = not (theme_title and uploaded_files and is_api_configured())
    if st.button("🚀 AI採点を実行", type="primary", disabled=execute_disabled, key="workflow_execute"):
        if not theme_title:
            st.error("テーマタイトルを入力してください")
        elif not uploaded_files:
            st.error("ファイルを選択してください")
        elif not is_api_configured():
            st.error("APIキーを設定してください")
        else:
            with st.spinner("採点を実行中..."):
                try:
                    # 再採点モードの場合
                    if is_rescore_mode and 'rescore_submission_id' in st.session_state:
                        submission_id = st.session_state.rescore_submission_id
                        
                        # 提出資料を更新
                        update_submission(submission_id, theme_title, theme_description)
                        
                        # 既存のファイルを削除（物理ファイルも削除）
                        existing_files = get_files_by_submission(submission_id)
                        for file_info in existing_files:
                            file_path = Path(file_info['file_path'])
                            if file_path.exists():
                                try:
                                    file_path.unlink()
                                except Exception as e:
                                    pass  # ファイル削除に失敗しても続行
                        
                        # ファイル情報を削除
                        delete_files_by_submission(submission_id)
                        
                        # 新しいファイルを保存
                        upload_dir = Path("uploads") / str(submission_id)
                        upload_dir.mkdir(parents=True, exist_ok=True)
                    else:
                        # 新規提出資料を作成
                        submission_id = create_submission(school_id, theme_title, theme_description)
                        
                        # ファイルを保存
                        upload_dir = Path("uploads") / str(submission_id)
                        upload_dir.mkdir(parents=True, exist_ok=True)
                    
                    # ファイルをアップロードして保存
                    files = []
                    for uploaded_file in uploaded_files:
                        file_path = save_uploaded_file(uploaded_file, upload_dir)
                        file_size = get_file_size(file_path)
                        file_type = get_file_type(file_path)
                        
                        create_file(submission_id, uploaded_file.name, str(file_path),
                                   file_type, file_size)
                        files.append({
                            'file_name': uploaded_file.name,
                            'file_path': str(file_path)
                        })
                    
                    update_submission_status(submission_id, "completed")
                    
                    # ファイルからテキストを抽出
                    all_text = ""
                    for file_info in files:
                        file_path = Path(file_info['file_path'])
                        if file_path.exists():
                            try:
                                text = extract_text_from_file(file_path)
                                all_text += f"\n\n=== {file_info['file_name']} ===\n\n{text}"
                            except Exception as e:
                                st.warning(f"{file_info['file_name']}のテキスト抽出に失敗: {str(e)}")
                    
                    if not all_text.strip():
                        st.error("テキストを抽出できませんでした")
                    else:
                        # 再採点モードの場合、既存の採点結果を取得
                        result_id = None
                        if is_rescore_mode:
                            all_results = get_all_evaluation_results()
                            existing_results = [
                                r for r in all_results 
                                if r.get('submission_id') == submission_id 
                                and r.get('evaluation_status') == 'completed'
                            ]
                            
                            if existing_results:
                                # 既存の結果がある場合は上書き
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
                        else:
                            # 新規採点の場合は新規作成
                            result_id = create_evaluation_result(submission_id,
                                                                evaluated_by=None,
                                                                ai_model="gpt-4")
                        
                        # 各評価項目について採点
                        criteria = get_all_criteria()
                        total_score = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, criterion in enumerate(criteria):
                            status_text.text(f"評価項目 {idx+1}/{len(criteria)}: {criterion['criterion_name']} を採点中...")
                            progress_bar.progress((idx + 1) / len(criteria))
                            
                            try:
                                result = evaluate_criterion(all_text, criterion['id'])
                                score = result.get('score', 0)
                                reason = result.get('reason', '')
                                
                                create_evaluation_detail(result_id, criterion['id'],
                                                       score, reason)
                                total_score += score
                            except Exception as e:
                                error_msg = str(e)
                                # レート制限エラーの場合は詳細なメッセージを表示
                                if "429" in error_msg or "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                                    st.error(f"⚠️ 評価項目 {criterion['criterion_name']} の採点でレート制限エラーが発生しました")
                                    st.error(error_msg)
                                    st.warning("💡 Google Gemini APIのレート制限に達しました。無料プランの場合、1分あたり5リクエスト、1日あたり25リクエストに制限されています。")
                                    st.info("📌 対処方法：\n1. 1-2分待ってから再度お試しください\n2. 有料プランにアップグレードすると制限が緩和されます\n3. Google Cloud ConsoleでAPIの利用状況を確認してください")
                                # 403エラーの場合は詳細なメッセージを表示
                                elif "403" in error_msg or "Forbidden" in error_msg:
                                    st.error(f"❌ 評価項目 {criterion['criterion_name']} の採点でエラーが発生しました")
                                    st.error(error_msg)
                                    st.warning("💡 APIキーの設定を確認してください。「⚙️ API設定」ページで再設定できます。")
                                else:
                                    st.error(f"❌ 評価項目 {criterion['criterion_name']} の採点でエラーが発生しました")
                                    st.error(error_msg)
                                
                                create_evaluation_detail(result_id, criterion['id'], 0,
                                                       f"採点エラー: {error_msg}")
                        
                        # 採点結果を更新
                        update_evaluation_result(result_id, total_score, "completed")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        if is_rescore_mode:
                            st.success(f"再採点が完了しました！総合スコア: {total_score}/60")
                        else:
                            st.success(f"採点が完了しました！総合スコア: {total_score}/60")
                        st.info("採点結果は「🏫 参加校管理」ページのデータ一覧で確認できます。")
                        
                        # 表彰状の表示（賞を獲得した場合）
                        try:
                            st.markdown("---")
                            st.subheader("🏆 表彰状")
                            
                            # 採点結果を取得
                            final_result = get_evaluation_result(result_id)
                            if final_result:
                                # すべての採点結果を取得して賞を判定
                                all_results = get_all_evaluation_results()
                                completed_results = [r for r in all_results if r.get("evaluation_status") == "completed"]
                                awards_dict = determine_awards(completed_results)
                                
                                # この採点結果に付与された賞を取得
                                awards = awards_dict.get(result_id, [])
                                
                                if awards:
                                    # 表彰状を生成して表示
                                    certificates = generate_certificate_for_result(
                                        final_result,
                                        awards,
                                        completed_results
                                    )
                                    
                                    for award_type, certificate_text in certificates.items():
                                        st.markdown(certificate_text)
                                        st.markdown("---")
                                else:
                                    st.info("今回の採点では賞を獲得していません。")
                        except Exception as e:
                            st.warning(f"表彰状の表示でエラーが発生しました: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                        
                        # 再採点モードのセッション状態をクリア
                        if is_rescore_mode:
                            if 'rescore_school_id' in st.session_state:
                                del st.session_state.rescore_school_id
                            if 'rescore_submission_id' in st.session_state:
                                del st.session_state.rescore_submission_id
                        
                        # フォームをクリア
                        if 'workflow_theme_title' in st.session_state:
                            del st.session_state.workflow_theme_title
                        if 'workflow_theme_description' in st.session_state:
                            del st.session_state.workflow_theme_description
                        if 'workflow_upload_files' in st.session_state:
                            del st.session_state.workflow_upload_files
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# 参加校管理
elif page == "🏫 参加校管理":
    st.title("🏫 参加校管理")
    
    # 新規参加校登録
    st.subheader("新規参加校登録")
    col1, col2 = st.columns(2)
    with col1:
        new_school_name = st.text_input("学校名 *", key="new_school_name_manage")
    with col2:
        new_prefecture = st.text_input("都道府県", key="new_prefecture_manage")
    
    if st.button("参加校を登録", key="register_school_manage"):
        if new_school_name:
            school_id = create_school(new_school_name, new_prefecture)
            st.success(f"参加校を登録しました（ID: {school_id}）")
            st.rerun()
        else:
            st.warning("学校名を入力してください")
    
    st.divider()
    
    schools = get_all_schools()
    if schools:
        # データ一覧
        st.subheader("データ一覧")
        
        # 採点結果を取得して参加校に紐付ける
        submissions = get_all_submissions()
        results = get_all_evaluation_results()
        completed_results = [r for r in results if r["evaluation_status"] == "completed"]
        criteria = get_all_criteria()
        
        # 参加校ごとの最新の採点結果と提出資料IDを取得
        school_results = {}
        school_submissions = {}  # 参加校ID -> 提出資料IDのマッピング
        for result in completed_results:
            submission_id = result.get('submission_id')
            if submission_id:
                submission = next((s for s in submissions if s['id'] == submission_id), None)
                if submission:
                    school_id = submission.get('school_id')
                    if school_id:
                        # 最新の結果を保持（日付順）
                        if school_id not in school_results:
                            school_results[school_id] = result
                            school_submissions[school_id] = submission_id
                        else:
                            # より新しい結果があれば更新
                            current_date = school_results[school_id].get('evaluated_at', '')
                            new_date = result.get('evaluated_at', '')
                            if new_date > current_date:
                                school_results[school_id] = result
                                school_submissions[school_id] = submission_id
        
        # データフレームに採点結果の列を追加
        df = pd.DataFrame(schools)
        
        # 各評価項目のスコア列を追加
        for criterion in criteria:
            criterion_name = criterion['criterion_name']
            df[criterion_name] = None
        
        # 総合スコア列を追加
        df['総合スコア'] = None
        
        # 評価理由をまとめる列を追加（総合スコアの後）
        df['採点根拠'] = None
        
        # 各参加校の採点結果を設定
        for idx, school in enumerate(schools):
            school_id = school.get('id')
            if school_id in school_results:
                result = school_results[school_id]
                details = get_evaluation_details(result.get('id'))
                
                # 各評価項目のスコアを設定
                evaluation_reasons = []
                for detail in details:
                    criterion_id = detail.get('criterion_id')
                    criterion = next((c for c in criteria if c['id'] == criterion_id), None)
                    if criterion:
                        criterion_name = criterion['criterion_name']
                        score = detail.get('score', 0)
                        reason = detail.get('evaluation_reason', '')
                        df.at[idx, criterion_name] = f"{score}/10"
                        
                        # 評価理由を収集（採点根拠列用）
                        if reason:
                            evaluation_reasons.append(f"**{criterion_name}**: {reason}")
                
                # 総合スコアを設定
                df.at[idx, '総合スコア'] = f"{result.get('total_score', 0)}/60"
                
                # 採点根拠を設定（すべての評価理由をまとめる）
                if evaluation_reasons:
                    df.at[idx, '採点根拠'] = "\n\n".join(evaluation_reasons)
        
        # テーブル表示（列数が多い場合はst.dataframeを使用）
        if not df.empty:
            # 列の順序を調整（採点根拠を総合スコアの後に配置）
            base_cols = [col for col in df.columns if col not in ['総合スコア', '採点根拠', '操作']]
            df_display = df[base_cols + ['総合スコア', '採点根拠']].copy()
            df_display['操作'] = ''
            
            # データフレームを表示
            st.dataframe(df_display, width='stretch', use_container_width=True, height=400)
            
            # 操作ボタンを各行に追加
            st.markdown("### 操作")
            for row_idx, row in df.iterrows():
                school_id = row.get('id')
                school_name = row.get('name', '不明')
                if school_id is not None:
                    # 採点結果がある場合の処理
                    if school_id in school_results:
                        result = school_results[school_id]
                        result_id = result.get('id')
                        submission_id = school_submissions[school_id]
                        
                        # 特別審査員賞の設定状態を取得
                        has_special_award = get_special_judge_award(result_id)
                        
                        # 再採点ボタン、特別審査員賞設定、削除ボタンを配置
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
                        
                        with col1:
                            # 再採点ボタン
                            rescore_key = f"rescore_school_{school_id}_{row_idx}"
                            if st.button("🔄 再採点", key=rescore_key, type="primary"):
                                # 再採点対象の情報をセッション状態に保存
                                st.session_state.rescore_school_id = school_id
                                st.session_state.rescore_submission_id = submission_id
                                # 採点ワークフローのページに移動
                                st.session_state.current_page = "📝 採点ワークフロー"
                                st.rerun()
                        
                        with col2:
                            # 特別審査員賞の設定
                            special_award_key = f"special_award_{school_id}_{row_idx}"
                            if st.button("⭐ 特別審査員賞" if not has_special_award else "⭐ 特別審査員賞（設定済）", 
                                       key=special_award_key, 
                                       type="secondary" if not has_special_award else "primary"):
                                set_special_judge_award(result_id, not has_special_award)
                                st.rerun()
                        
                        with col3:
                            # 削除ボタン
                            delete_key = f"delete_school_table_{school_id}_{row_idx}"
                            if st.button("🗑️ 削除", key=delete_key, type="secondary"):
                                if delete_school(school_id):
                                    st.success(f"{school_name}を削除しました")
                                    st.rerun()
                                else:
                                    st.error("削除に失敗しました")
                        
                        with col4:
                            # 表彰状表示ボタン
                            certificate_key = f"certificate_{school_id}_{row_idx}"
                            if st.button("📜 表彰状を表示", key=certificate_key):
                                # 表彰状を表示
                                all_results = get_all_evaluation_results()
                                completed_results = [r for r in all_results if r.get("evaluation_status") == "completed"]
                                awards_dict = determine_awards(completed_results)
                                awards = awards_dict.get(result_id, [])
                                
                                if awards:
                                    certificates = generate_certificate_for_result(
                                        result,
                                        awards,
                                        completed_results
                                    )
                                    
                                    st.markdown("---")
                                    st.subheader("🏆 表彰状")
                                    for award_type, certificate_text in certificates.items():
                                        st.markdown(certificate_text)
                                        st.markdown("---")
                                else:
                                    st.info("この採点結果では賞を獲得していません。")
                    else:
                        # 採点結果がない場合
                        col1, col2, col3 = st.columns([1, 1, 8])
                        
                        with col1:
                            st.write("")  # スペーサー
                        
                        with col2:
                            delete_key = f"delete_school_table_{school_id}_{row_idx}"
                            if st.button("🗑️ 削除", key=delete_key, type="secondary"):
                                if delete_school(school_id):
                                    st.success(f"{school_name}を削除しました")
                                    st.rerun()
                                else:
                                    st.error("削除に失敗しました")
                        
                        with col3:
                            st.write(f"**{school_name}**")
                    
                    st.divider()
        else:
            st.dataframe(df, width='stretch')
    else:
        st.info("参加校が登録されていません")

# データ管理
elif page == "💾 データ管理":
    st.title("💾 データ管理")
    
    st.warning("""
    **⚠️ 重要: Streamlit Cloudでのデータ永続化について**
    
    Streamlit Cloudでは、ファイルシステムは一時的です。アプリを再起動したり再デプロイすると、データが消える可能性があります。
    
    **データを失わないために：**
    1. 定期的にバックアップをダウンロードしてください
    2. 重要なデータ変更後は必ずバックアップを取ってください
    3. バックアップファイルは安全な場所に保管してください
    """)
    
    st.divider()
    
    # データファイルの状態を表示
    st.subheader("📊 データファイルの状態")
    backup_info = get_backup_info()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("データファイル数", backup_info["total_files"])
    with col2:
        st.metric("総データサイズ", f"{backup_info['total_size']:,} bytes")
    with col3:
        total_records = sum(f["count"] for f in backup_info["files"])
        st.metric("総レコード数", total_records)
    
    st.markdown("#### 詳細情報")
    for file_info in backup_info["files"]:
        if file_info["exists"]:
            st.success(f"✅ **{file_info['name']}**: {file_info['count']}件 ({file_info['size']:,} bytes)")
        else:
            st.warning(f"⚠️ **{file_info['name']}**: ファイルが存在しません")
    
    st.divider()
    
    # バックアップと復元
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 バックアップのダウンロード")
        st.info("すべてのデータをZIPファイルとしてダウンロードします。")
        
        if st.button("バックアップを作成", key="create_backup", type="primary"):
            try:
                backup_data = create_backup()
                backup_filename = f"pitch_contest_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                
                st.download_button(
                    label="📥 バックアップをダウンロード",
                    data=backup_data,
                    file_name=backup_filename,
                    mime="application/zip",
                    key="download_backup"
                )
                st.success("✅ バックアップファイルを作成しました。上記のボタンからダウンロードしてください。")
            except Exception as e:
                st.error(f"バックアップの作成に失敗しました: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    with col2:
        st.subheader("📤 バックアップからの復元")
        st.info("以前にダウンロードしたバックアップファイルをアップロードしてデータを復元します。")
        st.warning("⚠️ **注意**: 復元を実行すると、現在のデータが上書きされます。")
        
        uploaded_file = st.file_uploader(
            "バックアップファイルを選択",
            type=["zip"],
            key="restore_backup_file"
        )
        
        if uploaded_file is not None:
            if st.button("復元を実行", key="execute_restore", type="primary"):
                try:
                    backup_bytes = uploaded_file.read()
                    result = restore_backup(backup_bytes)
                    
                    if result["success"]:
                        st.success("✅ データの復元が完了しました！")
                        st.info(f"復元されたファイル: {', '.join(result['restored_files'])}")
                        if result["backup_date"]:
                            st.info(f"バックアップ日時: {result['backup_date']}")
                        st.rerun()
                    else:
                        st.error("❌ データの復元に失敗しました。")
                        if result["errors"]:
                            for error in result["errors"]:
                                st.error(f"- {error}")
                except Exception as e:
                    st.error(f"復元処理中にエラーが発生しました: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    st.divider()
    
    # データの永続化についての説明
    st.subheader("ℹ️ データ永続化について")
    st.markdown("""
    ### Streamlit Cloudでのデータ保存について
    
    **現在の状況：**
    - データは`data/`ディレクトリのJSONファイルに保存されます
    - Streamlit Cloudでは、ファイルシステムは一時的です
    - アプリの再起動や再デプロイでデータが消える可能性があります
    
    **推奨される運用方法：**
    1. **定期的なバックアップ**: 重要なデータ入力後は必ずバックアップをダウンロード
    2. **Gitへのコミット**: データファイルをGitリポジトリにコミットすることで永続化（`.gitignore`で`data/*.json`をコメントアウト）
    3. **外部ストレージ**: Google Drive、AWS S3、Supabaseなどの外部ストレージを使用（高度）
    
    ### データが消えてしまった場合
    
    1. 以前にダウンロードしたバックアップファイルがある場合：
       - 「📤 バックアップからの復元」からファイルをアップロードして復元
    2. Gitリポジトリにコミット済みの場合：
       - GitHubからデータファイルを取得して復元
    3. バックアップがない場合：
       - 残念ながら、データの復旧はできません
       - 今後は定期的にバックアップを取ることをお勧めします
    """)
    
    # データファイルの状態を再表示
    st.markdown("---")
    st.subheader("📋 データファイルの詳細状態")
    show_data_persistence_info()
