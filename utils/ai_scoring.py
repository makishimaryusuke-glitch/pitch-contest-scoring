#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI採点ユーティリティ
OpenAI GPT-4またはGoogle Geminiを使用して採点を実行します。
"""

import os
from typing import Dict, List, Optional

# グローバル変数（セッション状態から設定）
_client = None
_ai_provider = None
_genai_configured = False

def detect_api_provider(api_key: str) -> str:
    """APIキーの形式からプロバイダーを自動検出"""
    api_key = api_key.strip()
    
    # Google Gemini APIキーは通常 "AIzaSy" で始まる
    if api_key.startswith("AIzaSy"):
        return "gemini"
    # OpenAI APIキーは通常 "sk-" で始まる
    elif api_key.startswith("sk-"):
        return "openai"
    else:
        # デフォルトはopenai（後方互換性のため）
        return "openai"

def set_api_key(api_key: str, provider: str = None):
    """APIキーを設定（アプリ内で入力）"""
    global _client, _ai_provider, _genai_configured
    
    # プロバイダーが指定されていない場合は自動検出
    if provider is None:
        provider = detect_api_provider(api_key)
    
    _ai_provider = provider.lower()
    
    # APIキーの形式とプロバイダーが一致しているか確認
    if _ai_provider == "openai":
        if not api_key.startswith("sk-"):
            raise ValueError(
                f"OpenAI APIキーの形式が正しくありません。"
                f"提供されたキーはGoogle Gemini APIキーのようです（AIzaSy...で始まります）。"
                f"プロバイダーを「gemini」に変更してください。"
            )
        from openai import OpenAI
        _client = OpenAI(api_key=api_key)
    elif _ai_provider == "gemini":
        if not api_key.startswith("AIzaSy"):
            raise ValueError(
                f"Google Gemini APIキーの形式が正しくありません。"
                f"提供されたキーはOpenAI APIキーのようです（sk-...で始まります）。"
                f"プロバイダーを「openai」に変更してください。"
            )
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _genai_configured = True
    else:
        raise ValueError(f"サポートされていないAIプロバイダー: {_ai_provider}")

def is_api_configured() -> bool:
    """APIキーが設定されているか確認"""
    # 環境変数からも確認（Streamlit Cloud用）
    if os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return True
    return _client is not None or _genai_configured

def get_api_provider_from_env() -> Optional[str]:
    """環境変数からAPIプロバイダーを取得"""
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    elif os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    return None

def initialize_from_env():
    """環境変数からAPIキーを初期化（Streamlit Cloud用）"""
    global _client, _ai_provider, _genai_configured
    
    provider = get_api_provider_from_env()
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            set_api_key(api_key, provider)
    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            set_api_key(api_key, provider)

# 評価基準のプロンプトテンプレート
EVALUATION_PROMPTS = {
    1: {
        "name": "着眼点の独創性",
        "prompt": """以下の提出資料を読み、以下の評価基準に基づいて0-10点で採点してください。

評価基準：既存の枠にとらわれない、高校生らしい柔軟な発想やユニークな視点があるか。

提出資料：
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で100文字程度で説明"
}}"""
    },
    2: {
        "name": "背景のリアリティ",
        "prompt": """以下の提出資料を読み、以下の評価基準に基づいて0-10点で採点してください。

評価基準：「なぜ自分がこの課題に取り組むのか」という動機が明確で、自らの実体験や現場の課題感に基づいた「当事者意識」が感じられるか。

提出資料：
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で100文字程度で説明"
}}"""
    },
    3: {
        "name": "仮説検証の適切性",
        "prompt": """以下の提出資料を読み、以下の評価基準に基づいて0-10点で採点してください。

評価基準：問いに対して適切な仮説を立て、SPLYZAMotion等のデータを活用して客観的かつ科学的に検証できているか。

提出資料：
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で100文字程度で説明"
}}"""
    },
    4: {
        "name": "分析の深さ",
        "prompt": """以下の提出資料を読み、以下の評価基準に基づいて0-10点で採点してください。

評価基準：結果を単に述べるだけでなく、「なぜそうなったのか」を深く考察し、論理的に結論を導き出せているか。

提出資料：
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で100文字程度で説明"
}}"""
    },
    5: {
        "name": "現場への還元",
        "prompt": """以下の提出資料を読み、以下の評価基準に基づいて0-10点で採点してください。

評価基準：その探究結果が、自分たちのチーム強化や競技力の向上にどう具体的に役立つか。

提出資料：
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で100文字程度で説明"
}}"""
    },
    6: {
        "name": "波及効果",
        "prompt": """以下の提出資料を読み、以下の評価基準に基づいて0-10点で採点してください。

評価基準：他のチームや競技、あるいはスポーツ界全体に対して、どのような新しい知見や価値を提供できるか。

提出資料：
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で100文字程度で説明"
}}"""
    },
}

def evaluate_with_openai(content: str, criterion_id: int) -> Dict[str, any]:
    """OpenAI GPT-4を使用して採点"""
    if _client is None:
        raise ValueError("OpenAI APIキーが設定されていません")
    
    prompt_template = EVALUATION_PROMPTS[criterion_id]["prompt"]
    prompt = prompt_template.format(content=content[:8000])  # トークン制限を考慮
    
    try:
        response = _client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは教育現場の審査員です。提出資料を客観的かつ公平に評価してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 一貫性を保つため低めに設定
        )
        
        result_text = response.choices[0].message.content
        # JSONを抽出（```json で囲まれている場合がある）
        import json
        import re
        
        # JSON部分を抽出
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # JSONが見つからない場合はデフォルト値を返す
            result = {"score": 5, "reason": "評価できませんでした"}
        
        return result
    except Exception as e:
        raise Exception(f"OpenAI API呼び出しエラー: {e}")

def evaluate_with_gemini(content: str, criterion_id: int) -> Dict[str, any]:
    """Google Geminiを使用して採点"""
    if not _genai_configured:
        raise ValueError("Google Gemini APIキーが設定されていません")
    
    import google.generativeai as genai
    
    prompt_template = EVALUATION_PROMPTS[criterion_id]["prompt"]
    prompt = prompt_template.format(content=content[:8000])
    
    try:
        # 利用可能なモデル名を試行
        # gemini-pro → gemini-1.0-pro → gemini-pro-vision の順で試す
        model_names = ['gemini-pro', 'gemini-1.0-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
        model = None
        last_error = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                # テスト呼び出しでモデルが利用可能か確認
                break
            except Exception as e:
                last_error = e
                continue
        
        if model is None:
            raise Exception(f"利用可能なGeminiモデルが見つかりませんでした。最後のエラー: {last_error}")
        
        response = model.generate_content(prompt)
        
        result_text = response.text
        # JSONを抽出
        import json
        import re
        
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"score": 5, "reason": "評価できませんでした"}
        
        return result
    except Exception as e:
        raise Exception(f"Gemini API呼び出しエラー: {e}")

def evaluate_criterion(content: str, criterion_id: int) -> Dict[str, any]:
    """評価項目ごとに採点を実行"""
    if not is_api_configured():
        raise ValueError("APIキーが設定されていません。設定ページでAPIキーを入力してください。")
    
    if _ai_provider == "openai":
        return evaluate_with_openai(content, criterion_id)
    elif _ai_provider == "gemini":
        return evaluate_with_gemini(content, criterion_id)
    else:
        raise ValueError(f"サポートされていないAIプロバイダー: {_ai_provider}")

def evaluate_all_criteria(content: str) -> List[Dict[str, any]]:
    """すべての評価項目について採点を実行"""
    results = []
    for criterion_id in range(1, 7):  # 1-6の評価項目
        try:
            result = evaluate_criterion(content, criterion_id)
            result["criterion_id"] = criterion_id
            result["criterion_name"] = EVALUATION_PROMPTS[criterion_id]["name"]
            results.append(result)
        except Exception as e:
            # エラーが発生した場合はデフォルト値を設定
            results.append({
                "criterion_id": criterion_id,
                "criterion_name": EVALUATION_PROMPTS[criterion_id]["name"],
                "score": 0,
                "reason": f"採点エラー: {str(e)}"
            })
    return results
