"""
AI Agent Orchestrator - Coordinates multiple AI agents for expense tracking
"""
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel , Field
import os
from dotenv import load_dotenv
load_dotenv()

api = os.getenv("API_KEY")

class RecieptObject(BaseModel):
    merchant: str = Field(description="Extracted merchant from reciept text")
    amount: float = Field(description="Extracted amount on reciept")
    date: str = Field(description="Extracted date of transaction from reciept text")
    items: str = Field(description="Extracted items from reciept text")
    category: str = Field(description="Extracted categery from reciept text like Shoping, Groceries, Entertainment, etc.")
    description: str = Field(description="Description of reciept text")
    

llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api,
            temperature=0.1
        )

class AIAgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive expense management"""
    
    def __init__(self):
        # Agent memory for context
        self.agent_memory = {
            "recent_expenses": [],
            "user_preferences": {},
            "spending_patterns": {},
            "budget_data": {}
        }
    
    def ai_enhanced_extraction(self, raw_text):

        """Use AI to enhance and structure the extracted data"""

        prompt = f"""
            Analyze this OCR text from a receipt and extract structured information:
            
            Raw OCR Text:
            {raw_text}
            
            Extract these fields:
            - merchant: Store/business name
            - amount: Total amount (as float)
            - date: Date in YYYY-MM-DD format
            - items: List of purchased items
            - category: Likely expense category based on merchant/items
            - description: Description of reciept text
            
            if any feild is missing in raw text, fill with 'Unknown'. 
            
            Focus on accuracy.Return only valid JSON."""
           
        model = llm.bind_tools([RecieptObject])
        response = model.invoke(prompt)
        result = response.additional_kwargs["function_call"]["arguments"]
        result = json.loads(result)
        print(result)
        return {
            "merchant": result["merchant"],
            "amount": result["amount"],
            "date": result["date"],
            "items": result["items"],
            "category": result["category"],
            "description": result["description"]
        }
            
    def generate_budget_with_ai(self, income: float, expense_history: List[Dict], 
                               goals: str = "", risk_tolerance: str = "moderate") -> Dict[str, Any]:
        """Generate personalized budget using actual expense data"""
        
        # Analyze current spending patterns in detail
        total_spent = sum(exp.get('amount', 0) for exp in expense_history)
        categories = {}
        monthly_spending = {}
        recurring_expenses = []
        
        for exp in expense_history:
            cat = exp.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + exp.get('amount', 0)
            
            # Track monthly patterns
            month = exp.get('date', '')[:7]
            if month not in monthly_spending:
                monthly_spending[month] = 0
            monthly_spending[month] += exp.get('amount', 0)
            
        
        months_count = len(monthly_spending) if monthly_spending else 1
        avg_monthly = total_spent / months_count
        
        prompt = f"""Create a personalized budget based on actual spending data. Return only valid JSON.

Financial Profile:
- Monthly Income: ${income:.2f}
- Current Monthly Average: ${avg_monthly:.2f}
- Risk Tolerance: {risk_tolerance}
- Goals: {goals or "Financial stability and growth"}
- Months of Data: {months_count}

Actual Spending by Category:
{json.dumps(categories)}

Monthly Spending History:
{json.dumps(monthly_spending)}

Create realistic budget using 50/30/20 principles but adjusted for actual spending patterns.

Return ONLY JSON, For example (note: Remember that it is just an example, you can change the values based on
the actual spending patterns):
{{
    "monthly_budget": {{
        "Food & Dining": {{"recommended": 300.00, "current": 350.00, "percentage": 0.15}},
        "Groceries": {{"recommended": 250.00, "current": 200.00, "percentage": 0.125}},
        "Transportation & Gas": {{"recommended": 200.00, "current": 180.00, "percentage": 0.10}},
        "Shopping & Retail": {{"recommended": 150.00, "current": 120.00, "percentage": 0.075}},
        "Entertainment & Recreation": {{"recommended": 100.00, "current": 80.00, "percentage": 0.05}},
        "Healthcare & Medical": {{"recommended": 100.00, "current": 90.00, "percentage": 0.05}},
        "Utilities & Bills": {{"recommended": 200.00, "current": 190.00, "percentage": 0.10}},
        "Other": {{"recommended": 100.00, "current": 85.00, "percentage": 0.05}}
    }},
    "budget_summary": {{
        "total_income": {income:.2f},
        "total_allocated": 1400.00,
        "savings_target": 600.00,
        "emergency_fund_target": 6000.00
    }},
    "recommendations": [
        "Based on your {avg_monthly:.0f} average, consider specific improvement",
        "Your top category needs attention",
        "Opportunity for savings identified"
    ],
    "budget_health_score": 80,
    "personalization_notes": [
        "Budget adjusted based on {months_count} months of actual data",
        "Accounts for your spending patterns"
    ]
}}

Use actual spending data to make realistic recommendations."""
        
        try:
            response = llm.invoke(prompt)
            result = response.content
            print(result)
            
            # Clean up response
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            elif result.startswith('```'):
                result = result.replace('```', '').strip()
            
            # Extract JSON
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                result = result[start_idx:end_idx]
            
            budget_data = json.loads(result)
            budget_data["created_date"] = datetime.now().strftime("%Y-%m-%d")
            budget_data["data_months"] = months_count
            
            # Store in agent memory
            self.agent_memory["budget_data"] = budget_data
            
            return budget_data
            
        except Exception as e:
            print(f"Budget AI generation error: {e}")
            
    
    def generate_insights_with_ai(self, expense_data: List[Dict]) -> Dict[str, Any]:
        """Generate financial insights using AI agent"""
        
        if not expense_data:
            return {
                "insights": ["Start tracking expenses to build spending patterns"],
                "recommendations": ["Add your first expense to get personalized insights"],
                "health_score": 50,
                "spending_health": "unknown",
                "trends": [],
                "next_month_forecast": {"predicted_total": 0, "risk_areas": []}
            }
        
        # Prepare data summary
        total_amount = sum(exp.get('amount', 0) for exp in expense_data)
        categories = {}
        merchants = {}
        
        for exp in expense_data:
            cat = exp.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + exp.get('amount', 0)
            
            merchant = exp.get('merchant', 'Unknown')  
            merchants[merchant] = merchants.get(merchant, 0) + exp.get('amount', 0)
        
        # Get top categories and merchants
        top_categories = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        top_merchants = dict(sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5])
        
        prompt = f"""Analyze spending patterns and provide insights. Return only valid JSON.

Data Summary:
- Total Spending: ${total_amount:.2f}
- Number of Transactions: {len(expense_data)}
- Top Categories: {json.dumps(top_categories)}
- Top Merchants: {json.dumps(top_merchants)}

Return ONLY this JSON with NO additional text:
{{
    "insights": [
        "Specific insight about spending patterns",
        "Notable trend or observation",
        "Comparison or benchmark insight"
    ],
    "recommendations": [
        "Actionable step to improve finances",
        "Specific saving opportunity",
        "Budget optimization suggestion"
    ],
    "spending_health": "good",
    "health_score": 75,
    "trends": [
        "Notable spending trend"
    ],
    "next_month_forecast": {{
        "predicted_total": {total_amount:.0f},
        "risk_areas": ["category1", "category2"]
    }}
}}

Focus on practical, actionable advice."""
        
        try:
            response = llm.invoke(prompt)
            result = response.content
            
            # Clean up response
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            elif result.startswith('```'):
                result = result.replace('```', '').strip()
            
            # Extract JSON
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                result = result[start_idx:end_idx]
            
            parsed = json.loads(result)
            
            # Ensure required fields with defaults
            parsed.setdefault("insights", [f"You've spent ${total_amount:.2f} across {len(expense_data)} transactions"])
            parsed.setdefault("recommendations", ["Track expenses regularly", "Create a monthly budget"])
            parsed.setdefault("spending_health", "moderate")
            parsed.setdefault("health_score", 70)
            parsed.setdefault("trends", [])
            parsed.setdefault("next_month_forecast", {"predicted_total": total_amount, "risk_areas": []})
            
            return parsed
            
        except Exception as e:
            print(f"Insights AI generation error: {e}")
            return {
                "insights": [f"Total spending: ${total_amount:.2f} across {len(expense_data)} transactions"],
                "recommendations": ["Review spending patterns weekly", "Set category budgets"],
                "spending_health": "moderate",
                "health_score": 65,
                "trends": ["Regular expense tracking needed"],
                "next_month_forecast": {"predicted_total": total_amount, "risk_areas": list(top_categories.keys())[:2]}
            }
    
    def get_personalized_advice(self, user_query: str, context: Dict = None) -> str:
        """Get personalized financial advice from AI agent"""
        
        context_info = ""
        if context:
            context_info = f"\nUser Context: {json.dumps(context, indent=2)}"
        
        memory_context = f"""
        Recent Expenses: {len(self.agent_memory['recent_expenses'])} transactions
        Budget Status: {'Active' if self.agent_memory.get('budget_data') else 'Not set'}
        """
        
        prompt = f"""
        Provide personalized financial advice for this question:
        
        User Question: {user_query}
        {context_info}
        {memory_context}
        
        Provide a helpful, specific, and actionable response. Be encouraging and practical.
        Focus on concrete steps the user can take to improve their financial situation.
        
        Keep the response conversational and supportive, around 100-200 words.
        """
        
        try:
            return llm.invoke(prompt)
        except Exception as e:
            print(f"Personalized advice error: {e}")
            return "I recommend tracking your expenses regularly and creating a monthly budget to better understand your spending patterns."
    
    def update_agent_memory(self, expense_data: Dict):
        """Update agent memory with new expense data"""
        self.agent_memory["recent_expenses"].append(expense_data)
        
        # Keep only last 50 expenses in memory
        if len(self.agent_memory["recent_expenses"]) > 50:
            self.agent_memory["recent_expenses"] = self.agent_memory["recent_expenses"][-50:]