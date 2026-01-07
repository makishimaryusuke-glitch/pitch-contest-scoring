#!/bin/bash
# アプリ起動スクリプト

cd "$(dirname "$0")"
source venv/bin/activate
streamlit run app.py

















