#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ピッチコンテストAI採点システム - メインアプリケーション（シンプル版）
認証機能なし、CSV/JSONファイル管理
"""

import streamlit as st
from pathlib import Path
from utils.data_manager import *
from utils.file_processor import *
from utils.ai_scoring import *
from utils.visualization import *
from utils.award_manager import determine_awards, format_awards_display
from utils.data_persistence_helper import ensure_data_directory, show_data_persistence_info, check_data_persistence
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
    "🏫 参加校管理"
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
    
    # データ永続化の状態を表示（折りたたみ可能）
    with st.expander("📁 データ永続化の状態", expanded=False):
        show_data_persistence_info()
    
    # ランキング表示（総合スコア順）
    st.subheader("🏆 採点結果ランキング")
    if completed_results:
        # 総合スコアでソート（高い順）
        sorted_results = sorted(completed_results, 
                               key=lambda x: x.get('total_score', 0), 
                               reverse=True)
        
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
                "総合スコア": f"{total_score}/60"
            })
        
        # ランキングテーブルを表示
        df_ranking = pd.DataFrame(ranking_data)
        st.dataframe(df_ranking, width='stretch', use_container_width=True, hide_index=True)
        
        # 賞の説明
        st.markdown("---")
        st.markdown("### 賞の説明")
        st.markdown("""
        - 🏆 **最優秀賞**: 総合スコア1位
        - 🥇 **優秀賞**: 総合スコア2-3位
        - 🥈 **敢闘賞**: 総合スコア4-5位
        - 🥉 **奨励賞**: 総合スコア6位以下
        - 💡 **独創性賞**: 着眼点の独創性で最高得点を獲得
        """)
    else:
        st.info("まだ採点結果がありません")

# 採点ワークフロー（1ページに統合）
elif page == "📝 採点ワークフロー":
    st.title("📝 採点ワークフロー")
    
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
    selected_school = st.selectbox("参加校を選択", list(school_options.keys()), key="workflow_school_select")
    school_id = school_options[selected_school]
    
    # 参加校が変更されたらフォームをクリア
    if st.session_state.previous_school_id is not None and st.session_state.previous_school_id != school_id:
        # フォームのキーをクリアするために、セッション状態をリセット
        if 'workflow_theme_title' in st.session_state:
            del st.session_state.workflow_theme_title
        if 'workflow_theme_description' in st.session_state:
            del st.session_state.workflow_theme_description
        if 'workflow_upload_files' in st.session_state:
            del st.session_state.workflow_upload_files
    
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
                    # 提出資料を作成
                    submission_id = create_submission(school_id, theme_title, theme_description)
                    
                    # ファイルを保存
                    upload_dir = Path("uploads") / str(submission_id)
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    
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
                        # 採点結果を作成
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
                                st.error(f"評価項目 {criterion['criterion_name']} の採点でエラー: {str(e)}")
                                create_evaluation_detail(result_id, criterion['id'], 0,
                                                       f"採点エラー: {str(e)}")
                        
                        # 採点結果を更新
                        update_evaluation_result(result_id, total_score, "completed")
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                        st.success(f"採点が完了しました！総合スコア: {total_score}/60")
                        st.info("採点結果は「🏫 参加校管理」ページのデータ一覧で確認できます。")
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
        
        # 参加校ごとの最新の採点結果を取得
        school_results = {}
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
                        else:
                            # より新しい結果があれば更新
                            current_date = school_results[school_id].get('evaluated_at', '')
                            new_date = result.get('evaluated_at', '')
                            if new_date > current_date:
                                school_results[school_id] = result
        
        # データフレームに採点結果の列を追加
        df = pd.DataFrame(schools)
        
        # 各評価項目のスコア列を追加
        for criterion in criteria:
            criterion_name = criterion['criterion_name']
            df[criterion_name] = None
        
        # 総合スコア列を追加
        df['総合スコア'] = None
        
        # 各参加校の採点結果を設定
        for idx, school in enumerate(schools):
            school_id = school.get('id')
            if school_id in school_results:
                result = school_results[school_id]
                details = get_evaluation_details(result.get('id'))
                
                # 各評価項目のスコアを設定
                for detail in details:
                    criterion_id = detail.get('criterion_id')
                    criterion = next((c for c in criteria if c['id'] == criterion_id), None)
                    if criterion:
                        criterion_name = criterion['criterion_name']
                        score = detail.get('score', 0)
                        df.at[idx, criterion_name] = f"{score}/10"
                
                # 総合スコアを設定
                df.at[idx, '総合スコア'] = f"{result.get('total_score', 0)}/60"
        
        # テーブル表示（列数が多い場合はst.dataframeを使用）
        if not df.empty:
            # 操作列を追加
            df_display = df.copy()
            df_display['操作'] = ''
            
            # データフレームを表示
            st.dataframe(df_display, width='stretch', use_container_width=True)
            
            # 削除ボタンを各行に追加
            st.markdown("### 操作")
            for row_idx, row in df.iterrows():
                school_id = row.get('id')
                school_name = row.get('name', '不明')
                if school_id is not None:
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        delete_key = f"delete_school_table_{school_id}_{row_idx}"
                        if st.button("🗑️ 削除", key=delete_key, type="secondary"):
                            if delete_school(school_id):
                                st.success(f"{school_name}を削除しました")
                                st.rerun()
                            else:
                                st.error("削除に失敗しました")
                    with col2:
                        st.write(f"**{school_name}**")
                    st.divider()
        else:
            st.dataframe(df, width='stretch')
    else:
        st.info("参加校が登録されていません")
