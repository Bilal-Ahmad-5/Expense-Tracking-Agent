import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import base64
from PIL import Image
import io

from utils.ocr_processor import OCRProcessor
from agent_orchestrator import AIAgentOrchestrator
from utils.data_manager import DataManager
from utils.visualizations import create_spending_chart, create_category_pie_chart, create_budget_gauge
from utils.styles import apply_custom_styles

# Initialize AI Agent System
@st.cache_resource
def initialize_components():
    ocr = OCRProcessor()
    ai_orchestrator = AIAgentOrchestrator()
    data_manager = DataManager()
    return ocr, ai_orchestrator, data_manager

def main():
    st.set_page_config(
        page_title="AI Expense Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize AI Agent System
    ocr, ai_orchestrator, data_manager = initialize_components()
    
    # Load existing data
    expenses_df = data_manager.load_expenses()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Expense Tracker</h1>
        <p>Multi-Agent AI System: Receipt Scanner • Categorization Expert • Budget Advisor • Financial Analyst</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Quick Stats")
        
        if not expenses_df.empty:
            total_spent = expenses_df['amount'].sum()
            avg_transaction = expenses_df['amount'].mean()
            transaction_count = len(expenses_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Spent", f"${total_spent:.2f}")
                st.metric("Transactions", transaction_count)
            with col2:
                st.metric("Avg Transaction", f"${avg_transaction:.2f}")
                if len(expenses_df) >= 2:
                    recent_change = expenses_df.iloc[-1]['amount'] - expenses_df.iloc[-2]['amount']
                    st.metric("Last Change", f"${recent_change:.2f}")
        else:
            st.info("Upload your first receipt to see stats!")
        
        st.markdown("---")
        
        # Budget setting
        st.markdown("### 🎯 Monthly Budget")
        monthly_budget = st.number_input("Set your budget", min_value=0.0, value=1000.0, step=50.0)
        
        if not expenses_df.empty:
            current_month_spending = expenses_df[
                pd.to_datetime(expenses_df['date']).dt.month == datetime.now().month
            ]['amount'].sum()
            
            budget_percentage = (current_month_spending / monthly_budget) * 100
            st.plotly_chart(create_budget_gauge(budget_percentage), use_container_width=True)
    
    # AI-Powered Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📷 AI Receipt Scanner", "📊 Dashboard", "📈 AI Analytics", "💰 AI Budget Advisor", "⚙️ Settings"])
    
    with tab1:
        st.markdown("### Upload Receipt")
        
        uploaded_file = st.file_uploader(
            "Choose a receipt image", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear image of your receipt for automatic processing"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image, caption="Uploaded Receipt", use_container_width=True)
            
            with col2:
                with st.spinner("🔍 Processing receipt..."):
                    # OCR processing
                    try:
                        # First extract OCR text
                        ocr_result = ocr.extract_text_with_ocr(image)
                        
                        if ocr_result:
                            # Use AI agent to enhance data extraction
                            with st.spinner("🤖 AI analyzing receipt data..."):
                                ai_extracted_data = ai_orchestrator.ai_enhanced_extraction(ocr_result)
                            
                            st.success("✅ Receipt processed with AI enhancement!")
                            
                            # Display extracted data with edit options
                            st.markdown("#### AI-Enhanced Extraction")
                            
                            # Use AI-extracted data as primary source with OCR as fallback
                            extracted_amount = ai_extracted_data["amount"]
                            amount = st.number_input("Amount ($)", value=float(extracted_amount), min_value=0.0)
                            
                            extracted_date = ai_extracted_data["date"]
                            try:
                                date = st.date_input("Date", value=pd.to_datetime(extracted_date).date())
                            except:
                                date = st.date_input("Date", value=datetime.now().date())
                            
                            extracted_merchant = ai_extracted_data["merchant"]
                            merchant = st.text_input("Merchant", value=extracted_merchant)
                            
                            # Show extracted items if available
                            extracted_items = ai_extracted_data["items"]
                            st.markdown("**Items Found:**")
                            st.write(", ".join(extracted_items[:5]))
                            
                            _category = ai_extracted_data["category"]
                            category = st.text_input("category", value=_category)
                            
                            _description = ai_extracted_data["description"]
                            description = st.text_input("Description", value=_description)
                            

                        else:
                            st.error("❌ Could not extract data from receipt. Please try again with a clearer image.")
                    except Exception as e:
                        st.error(f"❌ Error processing receipt: {str(e)}")
                if st.button("💾 Save Expense", type="primary"):
                                expense_data = ai_extracted_data
                                
                                # Update AI agent memory
                                ai_orchestrator.update_agent_memory(expense_data)
                                
                                data_manager.add_expense(expense_data)
                                st.success("💰 Expense saved and learned by AI!")
                                st.rerun()
    
    with tab2:
        st.markdown("### 📊 Expense Dashboard")
        
        if expenses_df.empty:
            st.info("📷 Upload your first receipt to see your dashboard!")
        else:
            # Recent transactions
            st.markdown("#### Recent Transactions")
            recent_df = expenses_df.tail(5).sort_values('date', ascending=False)
            
            for _, expense in recent_df.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        st.write(f"**{expense['merchant']}**")
                    with col2:
                        st.write(expense['category'])
                    with col3:
                        st.write(f"${expense['amount']:.2f}")
                    with col4:
                        st.write(expense['date'])
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Spending by Category")
                fig_pie = create_category_pie_chart(expenses_df)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("#### Daily Spending Trend")
                fig_line = create_spending_chart(expenses_df)
                st.plotly_chart(fig_line, use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Advanced Analytics")
        
        if expenses_df.empty:
            st.info("📊 No data available yet. Start by uploading receipts!")
        else:
            # Time range selector
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now())
            
            # Filter data
            filtered_df = expenses_df[
                (pd.to_datetime(expenses_df['date']) >= pd.to_datetime(start_date)) &
                (pd.to_datetime(expenses_df['date']) <= pd.to_datetime(end_date))
            ]
            
            if not filtered_df.empty:
                # Analytics metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total = filtered_df['amount'].sum()
                    st.metric("Total Spent", f"${total:.2f}")
                
                with col2:
                    avg_daily = filtered_df.groupby('date')['amount'].sum().mean()
                    st.metric("Avg Daily", f"${avg_daily:.2f}")
                
                with col3:
                    max_expense = filtered_df['amount'].max()
                    st.metric("Largest Expense", f"${max_expense:.2f}")
                
                with col4:
                    top_category = filtered_df.groupby('category')['amount'].sum().idxmax()
                    st.metric("Top Category", top_category)
                
                # Detailed breakdown
                st.markdown("#### Category Breakdown")
                category_summary = filtered_df.groupby('category').agg({
                    'amount': ['sum', 'mean', 'count']
                }).round(2)
                category_summary.columns = ['Total', 'Average', 'Count']
                st.dataframe(category_summary, use_container_width=True)
                
                # AI Agent Insights
                st.markdown("#### 🤖 AI Agent Insights")
                with st.spinner("AI analyzing your spending patterns..."):
                    ai_insights = ai_orchestrator.generate_insights_with_ai(filtered_df.to_dict('records'))
                
                if ai_insights.get('insights'):
                    for insight in ai_insights['insights']:
                        st.info(f"💡 {insight}")
                
                if ai_insights.get('recommendations'):
                    st.markdown("#### 📋 AI Recommendations")
                    for i, rec in enumerate(ai_insights['recommendations'], 1):
                        st.success(f"{i}. {rec}")
                
                # Health Score
                health_score = ai_insights.get('health_score', 70)
                st.markdown(f"#### 🏥 Spending Health Score: {health_score}/100")
                
                if health_score >= 80:
                    st.success("Excellent financial health!")
                elif health_score >= 60:
                    st.warning("Good, but room for improvement")
                else:
                    st.error("Needs attention - consider budget adjustments")
            else:
                st.warning("No expenses found in the selected date range.")
    
    with tab4:
        st.markdown("### 💰 AI Budget Advisor")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Create Personalized Budget")
            
            # Budget creation form
            monthly_income = st.number_input("Monthly Income ($)", min_value=0.0, value=3000.0, step=100.0)
            
            financial_goals = st.text_area(
                "Financial Goals (optional)", 
                placeholder="e.g., Save for vacation, pay off debt, build emergency fund"
            )
            
            risk_tolerance = st.selectbox(
                "Spending Style",
                options=["conservative", "moderate", "flexible"],
                index=1,
                help="Conservative: Focus on savings. Moderate: Balanced approach. Flexible: More discretionary spending."
            )
            
            if st.button("🧠 Generate AI Budget", type="primary"):
                if monthly_income > 0:
                    with st.spinner("AI creating your personalized budget..."):
                        expense_history = expenses_df.to_dict('records') if not expenses_df.empty else []
                        ai_budget = ai_orchestrator.generate_budget_with_ai(
                            monthly_income, expense_history, financial_goals, risk_tolerance
                        )
                    
                    st.session_state.ai_budget = ai_budget
                    st.success("✨ AI Budget created successfully!")
                else:
                    st.error("Please enter a valid monthly income")
        
        with col2:
            if 'ai_budget' in st.session_state:
                budget = st.session_state.ai_budget
                
                st.markdown("#### 📊 Your AI-Generated Budget")
                
                # Budget summary
                summary = budget.get('budget_summary', {})
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Monthly Income", f"${summary.get('total_income', 0):.0f}")
                    st.metric("Total Allocated", f"${summary.get('total_allocated', 0):.0f}")
                
                with col_b:
                    st.metric("Savings Target", f"${summary.get('savings_target', 0):.0f}")
                    st.metric("Health Score", f"{budget.get('budget_health_score', 75)}/100")
                
                # Category breakdown
                st.markdown("#### Category Allocations")
                budget_data = budget.get('monthly_budget', {})
                
                for category, details in budget_data.items():
                    recommended = details.get('recommended', 0)
                    current = details.get('current', 0)
                    percentage = details.get('percentage', 0)
                    
                    col_x, col_y, col_z = st.columns([2, 1, 1])
                    
                    with col_x:
                        st.write(f"**{category}**")
                    with col_y:
                        st.write(f"${recommended:.0f} ({percentage:.0%})")
                    with col_z:
                        variance = recommended - current
                        if variance > 0:
                            st.success(f"+${variance:.0f}")
                        elif variance < 0:
                            st.error(f"${variance:.0f}")
                
                # AI Recommendations
                if budget.get('recommendations'):
                    st.markdown("#### 🎯 AI Recommendations")
                    for i, rec in enumerate(budget['recommendations'], 1):
                        st.info(f"{i}. {rec}")
            else:
                st.info("👆 Create a personalized budget to see AI recommendations")
        
        # Financial Advice Chat
        st.markdown("---")
        st.markdown("#### 🤖 Ask Your AI Financial Advisor")
        
        user_question = st.text_input(
            "Ask a financial question:",
            placeholder="e.g., How can I save more money? Should I invest in stocks?"
        )
        
        if st.button("💬 Get AI Advice") and user_question:
            with st.spinner("AI advisor analyzing your question..."):
                context = {
                    "total_expenses": expenses_df['amount'].sum() if not expenses_df.empty else 0,
                    "expense_count": len(expenses_df) if not expenses_df.empty else 0,
                    "top_category": expenses_df.groupby('category')['amount'].sum().idxmax() if not expenses_df.empty else "None"
                }
                
                advice = ai_orchestrator.get_personalized_advice(user_question, context)
                st.success(f"🧠 **AI Advisor:** {advice}")

    with tab5:
        st.markdown("### ⚙️ Settings & Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Export Data")
            if not expenses_df.empty:
                if st.button("📊 Export to CSV"):
                    csv = expenses_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                if st.button("📋 Export to JSON"):
                    json_data = expenses_df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_data,
                        file_name=f"expenses_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
            else:
                st.info("No data to export yet.")
        
        with col2:
            st.markdown("#### Data Management")
            if not expenses_df.empty:
                st.warning("⚠️ Danger Zone")
                if st.button("🗑️ Clear All Data", type="secondary"):
                    if st.checkbox("I understand this will delete all my expense data"):
                        data_manager.clear_all_data()
                        st.success("All data cleared!")
                        st.rerun()
            
            st.markdown("#### App Info")
            st.info("""
            **AI Expense Tracker v1.0**
            
            Features:
            - OCR Receipt Scanning
            - AI-Powered Categorization  
            - Beautiful Visualizations
            - Export Capabilities
            - Budget Tracking
            """)

if __name__ == "__main__":
    main()
