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

# 評価基準のプロンプトテンプレート（改善版：具体的なルーブリックとFew-shot Learningを含む）
EVALUATION_PROMPTS = {
    1: {
        "name": "着眼点の独創性",
        "prompt": """あなたは教育現場の審査員です。以下の提出資料を読み、評価基準に基づいて0-10点で採点してください。

【評価基準：着眼点の独創性】

【スコアリング基準】
- 10点: 既存の研究や手法を超えた、非常に独創的で革新的な視点がある。高校生らしい柔軟な発想が際立っており、従来のアプローチとは明確に異なる。
- 8-9点: 既存の手法を参考にしつつも、独自の視点やアプローチが明確にある。高校生らしい柔軟な発想が見られる。
- 6-7点: 既存の手法を参考にしているが、一部に独自の視点が見られる。ただし、革新的な要素は限定的。
- 4-5点: 主に既存の手法を参考にしており、独自性が少ない。模倣的な要素が強い。
- 0-3点: 既存の手法の模倣に留まり、独自性が見られない。単なる引用や再現に過ぎない。

【評価のポイント】
1. 既存の研究や手法を参考にしているか
2. 独自の視点やアプローチがあるか
3. 高校生らしい柔軟な発想があるか
4. ユニークな視点が明確に示されているか
5. 従来のアプローチとの違いが明確か

【評価例】
- 高得点例（9点）: 「SPLYZAMotionのデータを活用して、従来の練習方法とは異なる、個人の特性に合わせた練習メニューを提案した。データから見出した新しい視点が明確に示されている。」
- 中得点例（6点）: 「SPLYZAMotionのデータを分析し、一般的な練習方法を確認した。既存の研究を参考にしているが、独自の視点は限定的。」
- 低得点例（3点）: 「既存の研究をそのまま引用し、独自の視点が見られない。単なる模倣に留まっている。」

【提出資料】
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で200文字程度で説明。特に、どの点が独創的か、またはどの点が不足しているかを具体的に記述してください。"
}}"""
    },
    2: {
        "name": "背景のリアリティ",
        "prompt": """あなたは教育現場の審査員です。以下の提出資料を読み、評価基準に基づいて0-10点で採点してください。

【評価基準：背景のリアリティ】

【スコアリング基準】
- 10点: 「なぜ自分がこの課題に取り組むのか」という動機が非常に明確で、自らの実体験や現場の課題感に基づいた強い「当事者意識」が感じられる。具体的なエピソードや体験が示されている。
- 8-9点: 動機が明確で、実体験や現場の課題感に基づいた「当事者意識」が感じられる。ただし、一部の説明が抽象的。
- 6-7点: 動機は示されているが、実体験や現場の課題感との結びつきが弱い。当事者意識は感じられるが、説得力が不足している。
- 4-5点: 動機は示されているが、一般的で抽象的。実体験や現場の課題感との結びつきが弱く、当事者意識が薄い。
- 0-3点: 動機が不明確で、実体験や現場の課題感に基づいた「当事者意識」が感じられない。単なる一般的な課題提起に留まっている。

【評価のポイント】
1. 「なぜ自分がこの課題に取り組むのか」という動機が明確か
2. 自らの実体験が示されているか
3. 現場の課題感が具体的に示されているか
4. 「当事者意識」が感じられるか
5. 具体的なエピソードや体験が示されているか

【評価例】
- 高得点例（9点）: 「自分が実際に経験した試合での課題を具体的に示し、その課題を解決したいという強い動機が明確に示されている。実体験に基づいた当事者意識が感じられる。」
- 中得点例（6点）: 「一般的な課題は示されているが、自分の実体験との結びつきが弱い。動機は示されているが、説得力が不足している。」
- 低得点例（3点）: 「一般的な課題提起に留まり、自分の実体験や当事者意識が感じられない。動機が不明確。」

【提出資料】
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で200文字程度で説明。特に、動機の明確さ、実体験の有無、当事者意識の強さを具体的に記述してください。"
}}"""
    },
    3: {
        "name": "仮説検証の適切性",
        "prompt": """あなたは教育現場の審査員です。以下の提出資料を読み、評価基準に基づいて0-10点で採点してください。

【評価基準：仮説検証の適切性】

【スコアリング基準】
- 10点: 問いに対して適切な仮説を立て、SPLYZAMotion等のデータを活用して客観的かつ科学的に検証できている。仮説と検証方法の整合性が高い。
- 8-9点: 適切な仮説を立て、データを活用して検証できている。ただし、一部の検証方法に改善の余地がある。
- 6-7点: 仮説は示されているが、検証方法が不十分。データの活用が限定的で、客観性に欠ける部分がある。
- 4-5点: 仮説は示されているが、検証方法が不適切。データの活用が不十分で、科学的な検証ができていない。
- 0-3点: 仮説が不明確、または検証方法が不適切。データの活用がなく、客観的な検証ができていない。

【評価のポイント】
1. 問いに対して適切な仮説を立てているか
2. SPLYZAMotion等のデータを活用しているか
3. 客観的かつ科学的に検証できているか
4. 仮説と検証方法の整合性があるか
5. データの分析が適切か

【評価例】
- 高得点例（9点）: 「明確な仮説を立て、SPLYZAMotionのデータを統計的に分析して検証している。仮説と検証方法の整合性が高く、科学的なアプローチが取られている。」
- 中得点例（6点）: 「仮説は示されているが、データの分析が表面的。検証方法に改善の余地があり、客観性が不足している。」
- 低得点例（3点）: 「仮説が不明確で、データの活用が不十分。科学的な検証ができていない。」

【提出資料】
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で200文字程度で説明。特に、仮説の適切さ、データ活用の程度、検証方法の科学性を具体的に記述してください。"
}}"""
    },
    4: {
        "name": "分析の深さ",
        "prompt": """あなたは教育現場の審査員です。以下の提出資料を読み、評価基準に基づいて0-10点で採点してください。

【評価基準：分析の深さ】

【スコアリング基準】
- 10点: 結果を単に述べるだけでなく、「なぜそうなったのか」を深く考察し、論理的に結論を導き出せている。多角的な視点からの分析が見られる。
- 8-9点: 結果の考察が深く、論理的に結論を導き出せている。ただし、一部の分析に改善の余地がある。
- 6-7点: 結果の考察は示されているが、深さが不足している。論理的な結論は導き出せているが、分析が表面的。
- 4-5点: 結果を述べているが、考察が浅い。論理的な結論を導き出すことができていない。
- 0-3点: 結果を述べるだけで、考察がない。論理的な結論を導き出すことができていない。

【評価のポイント】
1. 結果を単に述べるだけでなく、考察があるか
2. 「なぜそうなったのか」を深く考察しているか
3. 論理的に結論を導き出せているか
4. 多角的な視点からの分析があるか
5. 分析の深さが感じられるか

【評価例】
- 高得点例（9点）: 「データの結果から、なぜそのような結果になったのかを多角的に分析し、論理的に結論を導き出している。分析の深さが感じられる。」
- 中得点例（6点）: 「結果の考察は示されているが、分析が表面的。論理的な結論は導き出せているが、深さが不足している。」
- 低得点例（3点）: 「結果を述べるだけで、考察がない。論理的な結論を導き出すことができていない。」

【提出資料】
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で200文字程度で説明。特に、考察の深さ、論理性、分析の多角性を具体的に記述してください。"
}}"""
    },
    5: {
        "name": "現場への還元",
        "prompt": """あなたは教育現場の審査員です。以下の提出資料を読み、評価基準に基づいて0-10点で採点してください。

【評価基準：現場への還元】

【スコアリング基準】
- 10点: その探究結果が、自分たちのチーム強化や競技力の向上にどう具体的に役立つかが明確に示されている。実践的な提案が具体的である。
- 8-9点: 探究結果がチーム強化や競技力の向上に役立つことが示されている。ただし、一部の提案が抽象的。
- 6-7点: 探究結果の還元は示されているが、具体的性が不足している。実践的な提案が限定的。
- 4-5点: 探究結果の還元は示されているが、抽象的で実践的でない。具体的な提案が不足している。
- 0-3点: 探究結果の還元が示されていない、または非常に抽象的で実践的でない。

【評価のポイント】
1. 探究結果がチーム強化に役立つことが示されているか
2. 競技力の向上に役立つことが示されているか
3. 具体的な提案が示されているか
4. 実践的な内容か
5. 還元方法が明確か

【評価例】
- 高得点例（9点）: 「探究結果を基に、具体的な練習メニューや戦術の改善案を提案している。実践的な内容で、チーム強化に役立つことが明確に示されている。」
- 中得点例（6点）: 「探究結果の還元は示されているが、具体的性が不足している。実践的な提案が限定的。」
- 低得点例（3点）: 「探究結果の還元が示されていない、または非常に抽象的で実践的でない。」

【提出資料】
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で200文字程度で説明。特に、還元の具体性、実践性、チーム強化への貢献度を具体的に記述してください。"
}}"""
    },
    6: {
        "name": "波及効果",
        "prompt": """あなたは教育現場の審査員です。以下の提出資料を読み、評価基準に基づいて0-10点で採点してください。

【評価基準：波及効果】

【スコアリング基準】
- 10点: 他のチームや競技、あるいはスポーツ界全体に対して、どのような新しい知見や価値を提供できるかが明確に示されている。波及効果が具体的である。
- 8-9点: 他のチームや競技への波及効果が示されている。ただし、一部の説明が抽象的。
- 6-7点: 波及効果は示されているが、具体性が不足している。新しい知見や価値の提示が限定的。
- 4-5点: 波及効果は示されているが、抽象的で説得力が不足している。新しい知見や価値の提示が不十分。
- 0-3点: 波及効果が示されていない、または非常に抽象的で説得力がない。

【評価のポイント】
1. 他のチームへの波及効果が示されているか
2. 他の競技への波及効果が示されているか
3. スポーツ界全体への波及効果が示されているか
4. 新しい知見や価値が提示されているか
5. 波及効果が具体的か

【評価例】
- 高得点例（9点）: 「探究結果が他のチームや競技にも応用可能であることが明確に示されている。新しい知見や価値が具体的に提示されている。」
- 中得点例（6点）: 「波及効果は示されているが、具体性が不足している。新しい知見や価値の提示が限定的。」
- 低得点例（3点）: 「波及効果が示されていない、または非常に抽象的で説得力がない。」

【提出資料】
{content}

採点結果は以下のJSON形式で返してください：
{{
    "score": 0-10の整数,
    "reason": "採点理由を日本語で200文字程度で説明。特に、波及効果の具体性、新しい知見や価値の提示、他への応用可能性を具体的に記述してください。"
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
                {"role": "system", "content": "あなたは教育現場の審査員です。提出資料を客観的かつ公平に評価してください。評価基準に基づいて、一貫性のある採点を行ってください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 一貫性を高めるため低く設定（0.1-0.2推奨）
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
        # 利用可能なモデルを順に試行
        # 最新のモデル名から順に試す（2024年12月時点で利用可能なモデル）
        model_names = [
            'gemini-1.5-flash',  # 最新の高速モデル
            'gemini-1.5-pro',    # 最新の高性能モデル
            'gemini-1.0-pro',    # 旧バージョン
            'gemini-pro'         # 旧バージョン（非推奨）
        ]
        
        model = None
        last_error = None
        successful_model = None
        
        # まず、モデル一覧から利用可能なモデルを確認を試みる
        try:
            available_models_list = list(genai.list_models())
            if available_models_list:
                # 利用可能なモデル名を抽出
                available_model_names = []
                for model_info in available_models_list:
                    if hasattr(model_info, 'name'):
                        model_full_name = model_info.name
                        model_short_name = model_full_name.split('/')[-1] if '/' in model_full_name else model_full_name
                        supported_methods = getattr(model_info, 'supported_generation_methods', [])
                        if 'generateContent' in supported_methods:
                            available_model_names.append(model_short_name)
                
                # 利用可能なモデルが見つかった場合、優先順位に従って選択
                if available_model_names:
                    for preferred in model_names:
                        if preferred in available_model_names:
                            successful_model = preferred
                            break
                    # 見つからない場合は、最初の利用可能なモデルを使用
                    if not successful_model and available_model_names:
                        successful_model = available_model_names[0]
        except Exception:
            # モデル一覧取得に失敗した場合は、直接試行に進む
            pass
        
        # モデル一覧から見つかった場合はそれを使用、そうでない場合は直接試行
        if successful_model:
            model = genai.GenerativeModel(successful_model)
        else:
            # 直接モデル名を試行（実際の呼び出し時にエラーをキャッチ）
            for test_model_name in model_names:
                try:
                    model = genai.GenerativeModel(test_model_name)
                    successful_model = test_model_name
                    # モデルオブジェクトの作成に成功したら、実際の呼び出しで確認
                    break
                except Exception as e:
                    last_error = e
                    continue
        
        if model is None:
            error_msg = f"利用可能なGeminiモデルが見つかりませんでした。\n"
            error_msg += f"試行したモデル: {', '.join(model_names)}\n"
            if last_error:
                error_msg += f"最後のエラー: {last_error}"
            raise Exception(error_msg)
        
        # 実際の採点を実行（温度設定で一貫性を高める）
        generation_config = {
            "temperature": 0.1,  # 一貫性を高めるため低く設定
        }
        response = model.generate_content(prompt, generation_config=generation_config)
        
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
