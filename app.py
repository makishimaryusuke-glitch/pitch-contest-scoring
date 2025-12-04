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
import pandas as pd

# 環境変数からAPIキーを初期化（Streamlit Cloud用）
initialize_from_env()

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

# ナビゲーション
page = st.sidebar.selectbox(
    "ページを選択",
    ["⚙️ API設定", "🏠 ダッシュボード", "📤 提出資料のアップロード", "🤖 AI採点の実行", "📊 採点結果", "🏫 参加校管理"]
)

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
    
    # 最近の採点結果
    st.subheader("最近の採点結果")
    if completed_results:
        # 日付順にソート（新しい順）
        sorted_results = sorted(completed_results, 
                               key=lambda x: x.get('evaluated_at', '') or '', 
                               reverse=True)[:10]
        df = pd.DataFrame(sorted_results)
        display_cols = ["school_name", "theme_title", "total_score", "evaluated_at"]
        available_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(df[available_cols], width='stretch')
    else:
        st.info("まだ採点結果がありません")

# 提出資料のアップロード
elif page == "📤 提出資料のアップロード":
    st.title("📤 提出資料のアップロード")
    
    # 参加校の選択または新規作成
    schools = get_all_schools()
    school_options = {f"{s['name']} ({s.get('prefecture', '')})": s['id'] for s in schools}
    
    col1, col2 = st.columns(2)
    with col1:
        selected_school = st.selectbox("参加校を選択", ["新規作成"] + list(school_options.keys()))
    
    if selected_school == "新規作成":
        with col2:
            st.subheader("新規参加校を登録")
            new_school_name = st.text_input("学校名 *")
            new_prefecture = st.text_input("都道府県")
            
            if st.button("参加校を登録"):
                if new_school_name:
                    school_id = create_school(new_school_name, new_prefecture)
                    st.success(f"参加校を登録しました（ID: {school_id}）")
                    st.rerun()
    else:
        school_id = school_options[selected_school]
    
    # ファイルアップロード
    if selected_school != "新規作成":
        st.subheader("提出資料をアップロード")
        theme_title = st.text_input("テーマタイトル *", key="theme_title")
        theme_description = st.text_area("テーマ説明", key="theme_description")
        
        uploaded_files = st.file_uploader(
            "ファイルを選択（PDF、PowerPoint、テキスト）",
            type=['pdf', 'pptx', 'ppt', 'txt'],
            accept_multiple_files=True
        )
        
        if st.button("提出資料を登録", disabled=not (theme_title and uploaded_files)):
            if theme_title and uploaded_files:
                # 提出資料を作成
                submission_id = create_submission(school_id, theme_title, theme_description)
                
                # ファイルを保存
                upload_dir = Path("uploads") / str(submission_id)
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                for uploaded_file in uploaded_files:
                    file_path = save_uploaded_file(uploaded_file, upload_dir)
                    file_size = get_file_size(file_path)
                    file_type = get_file_type(file_path)
                    
                    create_file(submission_id, uploaded_file.name, str(file_path),
                               file_type, file_size)
                
                update_submission_status(submission_id, "completed")
                st.success(f"提出資料を登録しました（ID: {submission_id}）")
                st.rerun()

# AI採点の実行
elif page == "🤖 AI採点の実行":
    st.title("🤖 AI採点の実行")
    
    submissions = get_all_submissions()
    if not submissions:
        st.info("提出資料がありません")
    else:
        submission_options = {f"{s.get('school_name', '不明')} - {s['theme_title']}": s['id']
                             for s in submissions}
        selected_submission = st.selectbox("採点する提出資料を選択", list(submission_options.keys()))
        
        if selected_submission:
            submission_id = submission_options[selected_submission]
            submission = get_submission(submission_id)
            
            if submission:
                st.subheader("提出資料情報")
                st.write(f"**学校名:** {submission.get('school_name', '不明')}")
                st.write(f"**テーマ:** {submission['theme_title']}")
                st.write(f"**説明:** {submission.get('theme_description') or 'なし'}")
                
                # ファイル一覧
                files = get_files_by_submission(submission_id)
                if files:
                    st.subheader("提出ファイル")
                    for file in files:
                        st.write(f"- {file['file_name']} ({file['file_type']}, {file['file_size']} bytes)")
                
                # APIキーの確認
                if not is_api_configured():
                    st.warning("⚠️ APIキーが設定されていません。「⚙️ API設定」ページでAPIキーを設定してください。")
                
                # 採点実行
                if st.button("AI採点を実行", type="primary", disabled=not is_api_configured()):
                    with st.spinner("採点を実行中..."):
                        try:
                            # ファイルからテキストを抽出
                            all_text = ""
                            for file in files:
                                file_path = Path(file['file_path'])
                                if file_path.exists():
                                    try:
                                        text = extract_text_from_file(file_path)
                                        all_text += f"\n\n=== {file['file_name']} ===\n\n{text}"
                                    except Exception as e:
                                        st.warning(f"{file['file_name']}のテキスト抽出に失敗: {str(e)}")
                            
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
                                st.rerun()
                        except Exception as e:
                            st.error(f"エラーが発生しました: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

# 採点結果
elif page == "📊 採点結果":
    st.title("📊 採点結果")
    
    results = get_all_evaluation_results()
    completed_results = [r for r in results if r["evaluation_status"] == "completed"]
    
    if not completed_results:
        st.info("まだ採点結果がありません")
    else:
        # フィルタリング
        col1, col2 = st.columns(2)
        with col1:
            school_names = list(set(r.get("school_name", "不明") for r in completed_results))
            school_filter = st.selectbox("学校でフィルタ", ["すべて"] + school_names)
        with col2:
            sort_option = st.selectbox("並び替え", ["スコア順（高い順）", "スコア順（低い順）", "日付順（新しい順）"])
        
        # フィルタリングとソート
        filtered_results = completed_results
        if school_filter != "すべて":
            filtered_results = [r for r in filtered_results if r.get("school_name") == school_filter]
        
        if sort_option == "スコア順（高い順）":
            filtered_results = sorted(filtered_results, key=lambda x: x.get("total_score", 0), reverse=True)
        elif sort_option == "スコア順（低い順）":
            filtered_results = sorted(filtered_results, key=lambda x: x.get("total_score", 0))
        else:
            filtered_results = sorted(filtered_results, 
                                    key=lambda x: x.get("evaluated_at") or "", 
                                    reverse=True)
        
        # 結果一覧
        for idx, result in enumerate(filtered_results):
            result_id = result.get('id')
            if result_id is None:
                result_id = f'result_{idx}'
            else:
                result_id = str(result_id)
            
            # st.expanderはkeyパラメータをサポートしていないため、削除
            with st.expander(f"{result.get('school_name', '不明')} - {result.get('theme_title', '不明')} (スコア: {result.get('total_score', 0)}/60)"):
                # 詳細情報
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**評価日時:** {result.get('evaluated_at', '未設定')}")
                    st.write(f"**AIモデル:** {result.get('ai_model', '未設定')}")
                with col2:
                    st.write(f"**総合スコア:** {result.get('total_score', 0)}/60")
                    st.write(f"**ステータス:** {result.get('evaluation_status', '不明')}")
                
                # 削除ボタン
                delete_key = f"delete_result_{result.get('id')}_{idx}"
                if st.button("🗑️ 削除", key=delete_key, type="secondary"):
                    if delete_evaluation_result(result.get('id')):
                        st.success("採点結果を削除しました")
                        st.rerun()
                    else:
                        st.error("削除に失敗しました")
                
                # 評価詳細
                details = get_evaluation_details(result.get('id'))
                if details:
                    st.subheader("評価項目別スコア")
                    
                    # レーダーチャート
                    fig = create_radar_chart(details)
                    chart_key = f"radar_chart_{result_id}_{idx}"
                    st.plotly_chart(fig, width='stretch', key=chart_key)
                    
                    # 詳細テーブル
                    detail_data = []
                    for detail in details:
                        detail_data.append({
                            "評価項目": detail.get("criterion_name", "不明"),
                            "スコア": f"{detail.get('score', 0)}/10",
                            "評価理由": detail.get("evaluation_reason", "")
                        })
                    st.dataframe(pd.DataFrame(detail_data), width='stretch')
        
        # エクスポート
        st.subheader("エクスポート")
        if st.button("CSV形式でエクスポート"):
            df = pd.DataFrame(filtered_results)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="CSVをダウンロード",
                data=csv,
                file_name="evaluation_results.csv",
                mime="text/csv"
            )

# 参加校管理
elif page == "🏫 参加校管理":
    st.title("🏫 参加校管理")
    
    schools = get_all_schools()
    if schools:
        # 参加校一覧を表示
        for idx, school in enumerate(schools):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{school.get('name', '不明')}**")
                if school.get('prefecture'):
                    st.caption(f"都道府県: {school.get('prefecture')}")
            with col2:
                st.write(f"ID: {school.get('id')}")
            with col3:
                delete_key = f"delete_school_{school.get('id')}_{idx}"
                if st.button("🗑️ 削除", key=delete_key, type="secondary"):
                    if delete_school(school.get('id')):
                        st.success("参加校を削除しました")
                        st.rerun()
                    else:
                        st.error("削除に失敗しました")
            st.divider()
        
        # データフレーム表示（参考用）
        st.subheader("データ一覧")
        df = pd.DataFrame(schools)
        st.dataframe(df, width='stretch')
    else:
        st.info("参加校が登録されていません")
