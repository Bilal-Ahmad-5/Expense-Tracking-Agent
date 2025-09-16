import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def create_spending_chart(expenses_df):
    """Create a line chart showing spending over time"""
    if expenses_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Group by date and sum amounts
    daily_spending = expenses_df.groupby('date')['amount'].sum().reset_index()
    daily_spending['date'] = pd.to_datetime(daily_spending['date'])
    
    fig = px.line(
        daily_spending, 
        x='date', 
        y='amount',
        title='Daily Spending Trend',
        labels={'amount': 'Amount ($)', 'date': 'Date'}
    )
    
    fig.update_traces(
        line_color='#1f77b4',
        line_width=3,
        mode='lines+markers'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def create_category_pie_chart(expenses_df):
    """Create a pie chart showing spending by category"""
    if expenses_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    category_spending = expenses_df.groupby('category')['amount'].sum().reset_index()
    
    # Custom colors for categories
    colors = {
        'Food & Dining': '#FF6B6B',
        'Shopping': '#4ECDC4', 
        'Transportation': '#45B7D1',
        'Entertainment': '#96CEB4',
        'Healthcare': '#FFEAA7',
        'Utilities': '#DDA0DD',
        'Other': '#98D8C8'
    }
    
    fig = px.pie(
        category_spending,
        values='amount',
        names='category',
        title='Spending by Category',
        color='category',
        color_discrete_map=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
    )
    
    return fig

def create_budget_gauge(percentage):
    """Create a gauge chart for budget tracking"""
    color = "green" if percentage <= 75 else "yellow" if percentage <= 90 else "red"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Budget Usage"},
        delta = {'reference': 100},
        gauge = {
            'axis': {'range': [None, 150]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 75], 'color': "lightgray"},
                {'range': [75, 90], 'color': "gray"},
                {'range': [90, 150], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_merchant_bar_chart(expenses_df, top_n=10):
    """Create a bar chart showing top merchants by spending"""
    if expenses_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    merchant_spending = expenses_df.groupby('merchant')['amount'].sum().sort_values(ascending=False).head(top_n)
    
    fig = px.bar(
        x=merchant_spending.values,
        y=merchant_spending.index,
        orientation='h',
        title=f'Top {top_n} Merchants by Spending',
        labels={'x': 'Amount ($)', 'y': 'Merchant'}
    )
    
    fig.update_traces(marker_color='#1f77b4')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_weekly_comparison(expenses_df):
    """Create a chart comparing weekly spending"""
    if expenses_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig
    
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_df['week'] = expenses_df['date'].dt.to_period('W').astype(str)
    
    weekly_spending = expenses_df.groupby(['week', 'category'])['amount'].sum().reset_index()
    
    fig = px.bar(
        weekly_spending,
        x='week',
        y='amount',
        color='category',
        title='Weekly Spending by Category',
        labels={'amount': 'Amount ($)', 'week': 'Week'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig

def create_spending_heatmap(expenses_df):
    """Create a heatmap showing spending patterns by day of week and hour"""
    if expenses_df.empty:
        return go.Figure()
    
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_df['day_of_week'] = expenses_df['date'].dt.day_name()
    expenses_df['hour'] = expenses_df['date'].dt.hour
    
    # Create a pivot table
    heatmap_data = expenses_df.pivot_table(
        values='amount', 
        index='day_of_week', 
        columns='hour', 
        aggfunc='sum', 
        fill_value=0
    )
    
    fig = px.imshow(
        heatmap_data,
        title='Spending Patterns by Day and Time',
        labels=dict(x="Hour of Day", y="Day of Week", color="Amount ($)")
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig
