"""
Budget Advisor Agent - AI agent specialized in budget planning and financial advice
"""
from crewai import Agent, Task
from langchain_groq import ChatGroq
import json
from datetime import datetime, timedelta
import calendar

class BudgetAdvisorAgent:
    def __init__(self, groq_api_key):
        self.llm = ChatGroq(
            temperature=0.3,
            groq_api_key=groq_api_key,
            model_name="llama-3.1-70b-versatile"
        )
        
        self.agent = Agent(
            role='Personal Finance Advisor & Budget Specialist',
            goal='Create personalized budgets and provide strategic financial guidance',
            backstory="""You are a certified financial planner with over 15 years of experience 
                        helping individuals and families achieve financial stability. You specialize 
                        in budget creation, expense optimization, and long-term financial planning.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Standard budget allocation percentages (50/30/20 rule variations)
        self.budget_guidelines = {
            "conservative": {
                "Food & Dining": 0.15,
                "Groceries": 0.12,
                "Transportation & Gas": 0.15,
                "Utilities & Bills": 0.10,
                "Healthcare & Medical": 0.08,
                "Shopping & Retail": 0.08,
                "Entertainment & Recreation": 0.05,
                "Home & Garden": 0.05,
                "Other": 0.12,
                "Savings": 0.10
            },
            "moderate": {
                "Food & Dining": 0.18,
                "Groceries": 0.15,
                "Transportation & Gas": 0.18,
                "Utilities & Bills": 0.12,
                "Healthcare & Medical": 0.06,
                "Shopping & Retail": 0.10,
                "Entertainment & Recreation": 0.08,
                "Home & Garden": 0.05,
                "Other": 0.08
            },
            "flexible": {
                "Food & Dining": 0.22,
                "Groceries": 0.12,
                "Transportation & Gas": 0.15,
                "Utilities & Bills": 0.10,
                "Healthcare & Medical": 0.05,
                "Shopping & Retail": 0.15,
                "Entertainment & Recreation": 0.12,
                "Home & Garden": 0.04,
                "Other": 0.05
            }
        }
    
    def create_personalized_budget(self, income, expense_history, financial_goals=None, risk_tolerance="moderate"):
        """Create a personalized budget based on income and spending history"""
        
        # Analyze current spending patterns
        spending_analysis = self._analyze_current_spending(expense_history)
        
        task = Task(
            description=f"""
            Create a personalized monthly budget for someone with:
            
            Monthly Income: ${income:.2f}
            Risk Tolerance: {risk_tolerance}
            Financial Goals: {financial_goals or "General financial stability"}
            
            Current Spending Analysis:
            {json.dumps(spending_analysis, indent=2)}
            
            Budget Guidelines to Consider:
            - 50% for needs (housing, utilities, groceries, transportation)
            - 30% for wants (dining out, entertainment, shopping)
            - 20% for savings and debt repayment
            
            Create a detailed budget with:
            1. Recommended allocation for each expense category
            2. Specific dollar amounts for each category
            3. Comparison with current spending patterns
            4. 3-5 specific recommendations for improvement
            5. Emergency fund target
            6. Savings goals breakdown
            
            Return JSON format:
            {{
                "monthly_budget": {{
                    "category_name": {{
                        "recommended_amount": 300.00,
                        "current_amount": 350.00,
                        "variance": -50.00,
                        "percentage_of_income": 0.15
                    }}
                }},
                "budget_summary": {{
                    "total_income": {income:.2f},
                    "total_allocated": 0.00,
                    "remaining_for_savings": 0.00,
                    "emergency_fund_target": 0.00
                }},
                "recommendations": [
                    "Specific actionable recommendation..."
                ],
                "savings_plan": {{
                    "monthly_savings_target": 0.00,
                    "emergency_fund_months": 6,
                    "goal_timeline": "description"
                }}
            }}
            
            Be specific and practical with recommendations.
            """,
            agent=self.agent,
            expected_output="JSON object with detailed personalized budget"
        )
        
        try:
            result = task.execute()
            budget_data = json.loads(result)
            
            # Add budget creation date and validity
            budget_data["created_date"] = datetime.now().strftime("%Y-%m-%d")
            budget_data["budget_type"] = risk_tolerance
            
            return budget_data
            
        except Exception as e:
            print(f"Budget creation error: {e}")
            return self._create_fallback_budget(income, spending_analysis)
    
    def _analyze_current_spending(self, expense_history):
        """Analyze current spending patterns"""
        if not expense_history:
            return {"message": "No spending history available"}
        
        # Calculate category totals for last 3 months
        categories = {}
        total_spent = 0
        monthly_amounts = {}
        
        # Group by month and category
        for expense in expense_history:
            amount = expense.get('amount', 0)
            category = expense.get('category', 'Other')
            date = expense.get('date', '')
            
            total_spent += amount
            categories[category] = categories.get(category, 0) + amount
            
            month = date[:7] if date else 'unknown'
            if month not in monthly_amounts:
                monthly_amounts[month] = 0
            monthly_amounts[month] += amount
        
        # Calculate averages
        months_count = len(monthly_amounts) if monthly_amounts else 1
        avg_monthly_spending = total_spent / months_count
        
        return {
            "total_spent": total_spent,
            "average_monthly": avg_monthly_spending,
            "category_breakdown": categories,
            "months_analyzed": months_count,
            "monthly_totals": monthly_amounts
        }
    
    def _create_fallback_budget(self, income, spending_analysis):
        """Create a basic budget when AI fails"""
        guidelines = self.budget_guidelines["moderate"]
        
        budget = {}
        total_allocated = 0
        
        for category, percentage in guidelines.items():
            amount = income * percentage
            budget[category] = {
                "recommended_amount": round(amount, 2),
                "current_amount": spending_analysis.get("category_breakdown", {}).get(category, 0),
                "variance": 0,
                "percentage_of_income": percentage
            }
            total_allocated += amount
        
        return {
            "monthly_budget": budget,
            "budget_summary": {
                "total_income": income,
                "total_allocated": round(total_allocated, 2),
                "remaining_for_savings": round(income - total_allocated, 2),
                "emergency_fund_target": round(income * 6, 2)
            },
            "recommendations": [
                "Track expenses regularly to stay within budget",
                "Build an emergency fund with 6 months of expenses",
                "Review and adjust budget monthly"
            ],
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "budget_type": "moderate"
        }
    
    def provide_financial_advice(self, current_situation):
        """Provide personalized financial advice based on current situation"""
        
        task = Task(
            description=f"""
            Provide comprehensive financial advice based on this situation:
            
            Current Financial Situation:
            {json.dumps(current_situation, indent=2)}
            
            Analyze the situation and provide:
            1. Assessment of current financial health
            2. Top 3 priority areas for improvement
            3. Specific action steps for the next 30 days
            4. Medium-term goals (3-6 months)
            5. Long-term recommendations (1+ years)
            6. Warning signs to watch for
            7. Positive trends to build upon
            
            Return JSON format:
            {{
                "financial_health_score": 85,
                "health_assessment": "good|excellent|needs_improvement|concerning",
                "priority_areas": [
                    "Emergency fund building",
                    "Expense reduction in dining",
                    "Income diversification"
                ],
                "next_30_days": [
                    "Specific actionable step...",
                    "Another concrete action..."
                ],
                "medium_term_goals": [
                    "3-6 month goal with timeline..."
                ],
                "long_term_strategy": [
                    "1+ year strategic recommendation..."
                ],
                "warning_signs": [
                    "Red flag to monitor..."
                ],
                "positive_trends": [
                    "Good habit to maintain..."
                ]
            }}
            
            Be encouraging but honest about areas needing improvement.
            """,
            agent=self.agent,
            expected_output="JSON object with comprehensive financial advice"
        )
        
        try:
            result = task.execute()
            return json.loads(result)
            
        except Exception as e:
            print(f"Financial advice error: {e}")
            return {
                "financial_health_score": 70,
                "health_assessment": "needs_improvement",
                "priority_areas": ["Expense tracking", "Budget creation", "Emergency fund"],
                "next_30_days": ["Start tracking all expenses daily"],
                "medium_term_goals": ["Build $1000 emergency fund"],
                "long_term_strategy": ["Increase income through skills development"],
                "warning_signs": ["Overspending in discretionary categories"],
                "positive_trends": ["Regular expense tracking habits"]
            }
    
    def generate_budget_alerts(self, current_spending, budget, month_progress):
        """Generate budget alerts and warnings"""
        
        alerts = []
        current_month_spending = current_spending.get('current_month', {})
        budget_allocations = budget.get('monthly_budget', {})
        
        for category, spent in current_month_spending.items():
            if category in budget_allocations:
                budget_amount = budget_allocations[category]['recommended_amount']
                spent_percentage = (spent / budget_amount) * 100 if budget_amount > 0 else 0
                
                # Calculate expected spending based on month progress
                expected_spent_percentage = month_progress * 100
                
                if spent_percentage > 90:
                    alerts.append({
                        "type": "critical",
                        "category": category,
                        "message": f"You've spent 90%+ of your {category} budget (${spent:.2f}/${budget_amount:.2f})"
                    })
                elif spent_percentage > expected_spent_percentage + 20:
                    alerts.append({
                        "type": "warning",
                        "category": category,
                        "message": f"{category} spending is {spent_percentage:.0f}% of budget, ahead of schedule"
                    })
                elif spent_percentage < expected_spent_percentage - 20:
                    alerts.append({
                        "type": "positive",
                        "category": category,
                        "message": f"Great job! {category} spending is under budget"
                    })
        
        return alerts
    
    def suggest_budget_adjustments(self, budget, actual_spending, months_data=3):
        """Suggest budget adjustments based on actual spending patterns"""
        
        task = Task(
            description=f"""
            Analyze actual spending vs budget for {months_data} months and suggest adjustments:
            
            Current Budget:
            {json.dumps(budget.get('monthly_budget', {}), indent=2)}
            
            Actual Spending Patterns:
            {json.dumps(actual_spending, indent=2)}
            
            Provide realistic budget adjustments that:
            1. Account for actual spending patterns
            2. Still promote financial health
            3. Are achievable and sustainable
            4. Don't compromise essential expenses
            
            Return JSON format:
            {{
                "adjustment_summary": "Overall assessment of needed changes",
                "category_adjustments": {{
                    "category_name": {{
                        "current_budget": 300.00,
                        "suggested_budget": 350.00,
                        "reason": "Explanation for adjustment",
                        "priority": "high|medium|low"
                    }}
                }},
                "reallocation_opportunities": [
                    "Move $50 from X to Y category because..."
                ],
                "behavioral_changes": [
                    "Consider meal planning to reduce food costs",
                    "Negotiate better rates for utilities"
                ]
            }}
            """,
            agent=self.agent,
            expected_output="JSON object with budget adjustment recommendations"
        )
        
        try:
            result = task.execute()
            return json.loads(result)
            
        except Exception as e:
            print(f"Budget adjustment error: {e}")
            return {
                "adjustment_summary": "Unable to generate detailed adjustments",
                "category_adjustments": {},
                "reallocation_opportunities": [],
                "behavioral_changes": ["Review spending patterns monthly"]
            }