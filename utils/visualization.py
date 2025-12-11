#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可視化ユーティリティ
Plotlyを使用してレーダーチャート等を作成します。
"""

import plotly.graph_objects as go
from typing import List, Dict, Any

def create_radar_chart(evaluation_details: List[Dict[str, Any]]) -> go.Figure:
    """レーダーチャートを作成"""
    criterion_names = [detail["criterion_name"] for detail in evaluation_details]
    scores = [detail["score"] for detail in evaluation_details]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=criterion_names,
        fill='toself',
        name='スコア',
        line_color='rgb(32, 201, 151)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="評価項目別スコア",
        font=dict(size=12)
    )
    
    return fig

def create_comparison_chart(results_list: List[List[Dict[str, Any]]], 
                           labels: List[str]) -> go.Figure:
    """複数の採点結果を比較するレーダーチャートを作成"""
    fig = go.Figure()
    
    colors = ['rgb(32, 201, 151)', 'rgb(250, 177, 160)', 'rgb(255, 188, 122)', 
              'rgb(186, 176, 199)', 'rgb(237, 100, 166)']
    
    if results_list:
        criterion_names = [detail["criterion_name"] for detail in results_list[0]]
        
        for idx, results in enumerate(results_list):
            scores = [detail["score"] for detail in results]
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=criterion_names,
                fill='toself',
                name=labels[idx] if idx < len(labels) else f"結果{idx+1}",
                line_color=colors[idx % len(colors)]
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="複数校の比較",
        font=dict(size=12)
    )
    
    return fig






