import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional

class VisualizationHelper:
    """
    Helper class for creating consistent visualizations with custom color palette
    """
    
    def __init__(self):
        self.color_palette = {
            'primary': '#2F5249',
            'secondary': '#437057',
            'accent': '#97B067',
            'highlight': '#E3DE61'
        }
        
        self.color_sequence = [
            self.color_palette['primary'],
            self.color_palette['secondary'],
            self.color_palette['accent'],
            self.color_palette['highlight']
        ]
    
    def create_pie_chart(self, data: pd.DataFrame, values_col: str, names_col: str, title: str) -> go.Figure:
        """
        Create a pie chart with custom styling
        """
        fig = px.pie(
            data, 
            values=values_col, 
            names=names_col,
            title=title,
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            showlegend=True,
            height=400,
            font=dict(size=12),
            title_font_size=16
        )
        
        return fig
    
    def create_bar_chart(self, data: pd.DataFrame, x_col: str, y_col: str, title: str, 
                        color_col: Optional[str] = None) -> go.Figure:
        """
        Create a bar chart with custom styling
        """
        if color_col:
            fig = px.bar(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title,
                color_discrete_sequence=self.color_sequence
            )
        else:
            fig = px.bar(
                data,
                x=x_col,
                y=y_col,
                title=title,
                color_discrete_sequence=[self.color_palette['primary']]
            )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400,
            font=dict(size=12),
            title_font_size=16,
            showlegend=True if color_col else False
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
        
        return fig
    
    def create_treemap(self, data: pd.DataFrame, path_cols: List[str], values_col: str, title: str) -> go.Figure:
        """
        Create a treemap visualization
        """
        fig = px.treemap(
            data,
            path=path_cols,
            values=values_col,
            title=title,
            color=values_col,
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            height=500,
            font=dict(size=12),
            title_font_size=16
        )
        
        return fig
    
    def create_stacked_bar(self, data: pd.DataFrame, x_col: str, y_col: str, 
                          color_col: str, title: str) -> go.Figure:
        """
        Create a stacked bar chart
        """
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            color_discrete_sequence=self.color_sequence
        )
        
        fig.update_layout(
            barmode='stack',
            xaxis_tickangle=-45,
            height=400,
            font=dict(size=12),
            title_font_size=16,
            showlegend=True
        )
        
        return fig
    
    def create_dashboard_metrics(self, metrics: Dict[str, int]) -> go.Figure:
        """
        Create a dashboard-style metrics visualization
        """
        fig = make_subplots(
            rows=1, 
            cols=len(metrics),
            subplot_titles=list(metrics.keys()),
            specs=[[{"type": "indicator"}] * len(metrics)]
        )
        
        for i, (metric, value) in enumerate(metrics.items(), 1):
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=value,
                    number={'font': {'size': 30, 'color': self.color_palette['primary']}},
                    title={'text': metric, 'font': {'size': 14}}
                ),
                row=1, col=i
            )
        
        fig.update_layout(
            height=200,
            showlegend=False,
            margin=dict(t=50, b=0, l=20, r=20)
        )
        
        return fig

def create_visualizations(df: pd.DataFrame, processor) -> Dict[str, go.Figure]:
    """
    Create all visualizations for the dashboard
    """
    viz_helper = VisualizationHelper()
    charts = {}
    
    # Queue distribution pie chart
    if 'queue_type' in df.columns:
        queue_data = processor.analyze_queue_distribution(df)
        if not queue_data.empty:
            charts['queue_pie'] = viz_helper.create_pie_chart(
                queue_data, 'Count', 'Queue Type', 'Queue Type Distribution'
            )
    
    # Department bar chart
    if 'department' in df.columns:
        dept_data = processor.analyze_departments(df)
        if not dept_data.empty:
            charts['dept_bar'] = viz_helper.create_bar_chart(
                dept_data, 'Department', 'Headcount', 'Department Headcount'
            )
    
    # Role hierarchy treemap
    if 'role_category' in df.columns:
        role_data = processor.analyze_role_hierarchy(df)
        if not role_data.empty:
            charts['role_treemap'] = viz_helper.create_treemap(
                role_data, ['Role'], 'Count', 'Role Hierarchy Distribution'
            )
    
    # LOA status chart
    if 'loa_status' in df.columns:
        loa_data = processor.analyze_loa_status(df)
        if not loa_data.empty:
            charts['loa_pie'] = viz_helper.create_pie_chart(
                loa_data, 'Count', 'Status', 'LOA Status Distribution'
            )
    
    # Cross-department analysis
    if 'department' in df.columns and 'queue_type' in df.columns:
        cross_data = df.groupby(['department', 'queue_type']).size().reset_index()
        cross_data.columns = ['department', 'queue_type', 'Count']
        if not cross_data.empty:
            charts['cross_analysis'] = viz_helper.create_stacked_bar(
                cross_data, 'department', 'Count', 'queue_type', 'Queue Types by Department'
            )
    
    return charts
