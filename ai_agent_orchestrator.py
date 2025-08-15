"""
AI Agent Orchestrator - Coordinates multiple AI agents for expense tracking
"""
import json
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional, Any

# Simplified agent system without CrewAI dependency
class SimpleAgent:
    def __init__(self, role: str, goal: str, backstory: str, llm):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = llm
    
    def execute_task(self, prompt: str) -> str:
        """Execute a task using the LLM"""
        try:
            messages = [
                {"role": "system", "content": f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Agent task execution error: {e}")
            return ""

class AIAgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive expense management"""
    
    def __init__(self, groq_api_key: str):
        from groq import Groq
        self.groq_client = Groq(api_key=groq_api_key)
        
        # Initialize specialized agents
        self.receipt_agent = self._create_receipt_agent()
        self.categorization_agent = self._create_categorization_agent()  
        self.budget_agent = self._create_budget_agent()
        self.insights_agent = self._create_insights_agent()
        
        # Agent memory for context
        self.agent_memory = {
            "recent_expenses": [],
            "user_preferences": {},
            "spending_patterns": {},
            "budget_data": {}
        }
    
    def _create_receipt_agent(self) -> SimpleAgent:
        """Create Receipt Processing Agent"""
        return SimpleAgent(
            role="Receipt Processing Specialist",
            goal="Extract accurate financial data from receipt images using OCR and AI analysis",
            backstory="""You are an expert in optical character recognition and financial document processing. 
                        You specialize in extracting structured data from receipts, invoices, and purchase documents 
                        with high accuracy and attention to detail.""",
            llm=self.groq_client
        )
    
    def _create_categorization_agent(self) -> SimpleAgent:
        """Create Expense Categorization Agent"""
        return SimpleAgent(
            role="Expense Categorization Expert", 
            goal="Accurately categorize expenses and provide intelligent financial insights",
            backstory="""You are a certified financial advisor with expertise in personal finance management. 
                        You have helped thousands of individuals optimize their spending patterns and achieve 
                        financial goals through intelligent expense categorization.""",
            llm=self.groq_client
        )
    
    def _create_budget_agent(self) -> SimpleAgent:
        """Create Budget Advisory Agent"""
        return SimpleAgent(
            role="Personal Finance Advisor & Budget Specialist",
            goal="Create personalized budgets and provide strategic financial guidance",
            backstory="""You are a certified financial planner with over 15 years of experience helping 
                        individuals and families achieve financial stability. You specialize in budget creation, 
                        expense optimization, and long-term financial planning.""",
            llm=self.groq_client
        )
    
    def _create_insights_agent(self) -> SimpleAgent:
        """Create Financial Insights Agent"""
        return SimpleAgent(
            role="Financial Data Analyst & Insights Specialist",
            goal="Analyze spending patterns and provide actionable financial insights",
            backstory="""You are a financial data scientist specializing in personal finance analytics. 
                        You excel at identifying spending patterns, trends, and opportunities for financial 
                        optimization through data-driven insights.""",
            llm=self.groq_client
        )
    
    def process_receipt_with_ai(self, ocr_text: str, image_context: str = "") -> Dict[str, Any]:
        """Use AI agent to process receipt data with enhanced extraction"""
        
        prompt = f"""Extract financial data from this receipt text. Be very precise and return only valid JSON.

OCR Text:
{ocr_text}

Instructions:
1. Find the merchant/store name (usually at the top)
2. Extract the total amount (look for words like "total", "amount due", "balance")
3. Find the date (various formats possible)
4. List items purchased (exclude totals, taxes, etc.)
5. Suggest appropriate category based on merchant and items

Return ONLY this JSON structure with NO additional text:
{{
    "merchant": "exact store name",
    "amount": 0.00,
    "date": "YYYY-MM-DD",
    "items": ["item 1", "item 2"],
    "category_hint": "Food & Dining",
    "confidence": 0.90
}}

Use today's date {datetime.now().strftime('%Y-%m-%d')} if date unclear. Return "Unknown Merchant" if merchant unclear."""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a receipt data extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up response
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            elif result.startswith('```'):
                result = result.replace('```', '').strip()
            
            # Find JSON in response
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                result = result[start_idx:end_idx]
            
            parsed_data = json.loads(result)
            
            # Validate and clean data
            if not isinstance(parsed_data.get('amount'), (int, float)):
                parsed_data['amount'] = 0.0
            if not isinstance(parsed_data.get('items'), list):
                parsed_data['items'] = []
            if not parsed_data.get('merchant'):
                parsed_data['merchant'] = "Unknown Merchant"
                
            return parsed_data
            
        except Exception as e:
            print(f"Receipt AI processing error: {e}")
            return self._fallback_receipt_processing(ocr_text)
    
    def categorize_expense_with_ai(self, merchant: str, amount: float, items: List[str] = None, 
                                  context: Dict = None) -> Dict[str, Any]:
        """Use AI agent to categorize expenses intelligently"""
        
        items_text = ", ".join(items[:5]) if items else "No items listed"
        recent_categories = [exp.get('category') for exp in self.agent_memory["recent_expenses"][-10:]]
        recent_context = ", ".join(filter(None, recent_categories)) or "None"
        
        prompt = f"""Categorize this expense and return only valid JSON.

Merchant: {merchant}
Amount: ${amount:.2f}
Items: {items_text}
Recent categories: {recent_context}

Choose from these categories EXACTLY:
Food & Dining, Groceries, Shopping & Retail, Transportation & Gas, Entertainment & Recreation, Healthcare & Medical, Utilities & Bills, Home & Garden, Education & Learning, Travel & Vacation, Professional Services, Subscriptions & Memberships, Other

Return ONLY this JSON with NO additional text:
{{
    "category": "exact category name",
    "confidence": 0.85,
    "reasoning": "brief explanation",
    "tags": ["relevant", "tags"],
    "is_recurring": false
}}"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expense categorization expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
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
            
            # Validate category
            valid_categories = [
                "Food & Dining", "Groceries", "Shopping & Retail", "Transportation & Gas",
                "Entertainment & Recreation", "Healthcare & Medical", "Utilities & Bills",
                "Home & Garden", "Education & Learning", "Travel & Vacation", 
                "Professional Services", "Subscriptions & Memberships", "Other"
            ]
            
            if parsed.get("category") not in valid_categories:
                parsed["category"] = self._fallback_categorize(merchant, items)
            
            # Ensure required fields
            parsed.setdefault("confidence", 0.8)
            parsed.setdefault("reasoning", f"Categorized based on merchant: {merchant}")
            parsed.setdefault("tags", [])
            parsed.setdefault("is_recurring", False)
                
            return parsed
            
        except Exception as e:
            print(f"Categorization AI error: {e}")
            return {
                "category": self._fallback_categorize(merchant, items),
                "confidence": 0.6,
                "reasoning": f"Fallback categorization for {merchant}",
                "tags": [],
                "is_recurring": False
            }
    
    def _fallback_categorize(self, merchant: str, items: List[str] = None) -> str:
        """Simple fallback categorization"""
        merchant_lower = merchant.lower()
        
        if any(word in merchant_lower for word in ["grocery", "market", "food", "walmart", "target"]):
            return "Groceries"
        elif any(word in merchant_lower for word in ["restaurant", "cafe", "pizza", "burger", "starbucks"]):
            return "Food & Dining"
        elif any(word in merchant_lower for word in ["gas", "fuel", "shell", "exxon", "chevron"]):
            return "Transportation & Gas"
        elif any(word in merchant_lower for word in ["pharmacy", "cvs", "walgreens", "medical"]):
            return "Healthcare & Medical"
        else:
            return "Other"
    
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
            
            # Track recurring expenses
            if exp.get('is_recurring'):
                recurring_expenses.append(exp)
        
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

Recurring Expenses: {len(recurring_expenses)} identified

Create realistic budget using 50/30/20 principles but adjusted for actual spending patterns.

Return ONLY this JSON:
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
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a budget advisor creating personalized budgets from real spending data. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
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
            return self._fallback_budget_creation(income, categories)
    
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
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a financial analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            
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
            return self.budget_agent.execute_task(prompt)
        except Exception as e:
            print(f"Personalized advice error: {e}")
            return "I recommend tracking your expenses regularly and creating a monthly budget to better understand your spending patterns."
    
    def update_agent_memory(self, expense_data: Dict):
        """Update agent memory with new expense data"""
        self.agent_memory["recent_expenses"].append(expense_data)
        
        # Keep only last 50 expenses in memory
        if len(self.agent_memory["recent_expenses"]) > 50:
            self.agent_memory["recent_expenses"] = self.agent_memory["recent_expenses"][-50:]
    
    def _fallback_receipt_processing(self, ocr_text: str) -> Dict[str, Any]:
        """Fallback receipt processing without AI"""
        import re
        
        # Extract amount
        amount_matches = re.findall(r'\$\s*(\d+\.\d{2})', ocr_text)
        amount = max([float(m) for m in amount_matches]) if amount_matches else 0.0
        
        # Extract merchant (first reasonable line)
        lines = ocr_text.split('\n')
        merchant = "Unknown Merchant"
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d+$', line):
                merchant = re.sub(r'[^a-zA-Z0-9\s]', ' ', line).strip().title()
                if len(merchant) <= 30:
                    break
        
        return {
            "merchant": merchant,
            "amount": amount,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "items": [],
            "category_hint": "Other",
            "confidence": 0.5
        }
    
    def _fallback_budget_creation(self, income: float, current_spending: Dict) -> Dict[str, Any]:
        """Fallback budget creation without AI"""
        
        # Basic 50/30/20 allocation
        needs_budget = income * 0.5
        wants_budget = income * 0.3
        savings_budget = income * 0.2
        
        budget = {
            "Food & Dining": {"recommended": income * 0.15, "current": current_spending.get("Food & Dining", 0), "percentage": 0.15},
            "Groceries": {"recommended": income * 0.12, "current": current_spending.get("Groceries", 0), "percentage": 0.12},
            "Transportation & Gas": {"recommended": income * 0.15, "current": current_spending.get("Transportation & Gas", 0), "percentage": 0.15},
            "Utilities & Bills": {"recommended": income * 0.08, "current": current_spending.get("Utilities & Bills", 0), "percentage": 0.08},
            "Shopping & Retail": {"recommended": income * 0.10, "current": current_spending.get("Shopping & Retail", 0), "percentage": 0.10},
            "Entertainment & Recreation": {"recommended": income * 0.08, "current": current_spending.get("Entertainment & Recreation", 0), "percentage": 0.08},
            "Other": {"recommended": income * 0.12, "current": current_spending.get("Other", 0), "percentage": 0.12}
        }
        
        return {
            "monthly_budget": budget,
            "budget_summary": {
                "total_income": income,
                "total_allocated": income * 0.8,
                "savings_target": savings_budget,
                "emergency_fund_target": income * 6
            },
            "recommendations": [
                "Track all expenses to stay within budget limits",
                "Build an emergency fund with 6 months of expenses",
                "Review and adjust your budget monthly based on actual spending"
            ],
            "budget_health_score": 75,
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }