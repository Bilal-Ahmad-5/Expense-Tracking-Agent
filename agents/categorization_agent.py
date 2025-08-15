"""
Categorization Agent - AI agent specialized in expense categorization and analysis
"""
from crewai import Agent, Task
from langchain_groq import ChatGroq
import json

class CategorizationAgent:
    def __init__(self, groq_api_key):
        self.llm = ChatGroq(
            temperature=0.2,
            groq_api_key=groq_api_key,
            model_name="llama-3.1-70b-versatile"
        )
        
        self.agent = Agent(
            role='Expense Categorization Expert',
            goal='Accurately categorize expenses and provide detailed financial insights',
            backstory="""You are a certified financial advisor with expertise in personal 
                        finance management and expense categorization. You have helped thousands 
                        of individuals optimize their spending patterns and achieve financial goals.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
        
        self.categories = [
            "Food & Dining",
            "Groceries", 
            "Shopping & Retail",
            "Transportation & Gas",
            "Entertainment & Recreation",
            "Healthcare & Medical",
            "Utilities & Bills",
            "Home & Garden",
            "Education & Learning",
            "Travel & Vacation",
            "Professional Services",
            "Subscriptions & Memberships",
            "Other"
        ]
        
        # Enhanced keyword mapping
        self.category_keywords = {
            "Food & Dining": [
                "restaurant", "cafe", "starbucks", "mcdonalds", "pizza", "burger", "kfc", 
                "subway", "taco bell", "chipotle", "dining", "bar", "pub", "bistro"
            ],
            "Groceries": [
                "grocery", "supermarket", "walmart", "target", "kroger", "safeway", 
                "whole foods", "trader joe", "costco", "sams club", "food store"
            ],
            "Shopping & Retail": [
                "amazon", "ebay", "store", "mall", "clothing", "fashion", "shoes", 
                "electronics", "best buy", "apple store", "retail", "boutique"
            ],
            "Transportation & Gas": [
                "gas", "fuel", "shell", "exxon", "bp", "chevron", "mobil", "uber", 
                "lyft", "taxi", "parking", "metro", "bus", "train", "car wash"
            ],
            "Entertainment & Recreation": [
                "movie", "theater", "cinema", "netflix", "spotify", "game", "concert", 
                "sports", "gym", "fitness", "recreation", "park", "museum"
            ],
            "Healthcare & Medical": [
                "pharmacy", "cvs", "walgreens", "hospital", "doctor", "medical", 
                "health", "clinic", "dental", "vision", "insurance", "medication"
            ],
            "Utilities & Bills": [
                "electric", "electricity", "water", "internet", "phone", "cable", 
                "utility", "bill", "service", "telecom", "energy", "heating"
            ],
            "Home & Garden": [
                "home depot", "lowes", "hardware", "garden", "furniture", "decor", 
                "improvement", "repair", "maintenance", "cleaning", "household"
            ],
            "Education & Learning": [
                "school", "university", "education", "books", "tuition", "course", 
                "training", "workshop", "seminar", "learning", "academic"
            ],
            "Travel & Vacation": [
                "hotel", "airbnb", "airline", "flight", "airport", "travel", "vacation", 
                "rental", "tourism", "booking", "expedia", "trip"
            ],
            "Professional Services": [
                "lawyer", "accountant", "consultant", "service", "professional", 
                "business", "office", "meeting", "conference", "networking"
            ],
            "Subscriptions & Memberships": [
                "subscription", "membership", "monthly", "annual", "premium", "pro", 
                "plus", "streaming", "software", "app", "service plan"
            ]
        }
    
    def categorize_expense(self, merchant, amount, items=None, previous_categories=None):
        """Intelligent expense categorization using AI"""
        
        # First pass: Rule-based categorization
        rule_based_category = self._rule_based_categorization(merchant, items or [])
        
        # Second pass: AI-enhanced categorization
        ai_category = self._ai_categorization(merchant, amount, items or [], previous_categories or [])
        
        # Combine results with confidence scoring
        category, confidence = self._combine_categorization_results(
            rule_based_category, ai_category, merchant, items or []
        )
        
        # Generate explanation
        explanation = self._generate_explanation(merchant, amount, category, items or [])
        
        return {
            "category": category,
            "confidence": confidence,
            "explanation": explanation,
            "rule_based_suggestion": rule_based_category,
            "ai_suggestion": ai_category
        }
    
    def _rule_based_categorization(self, merchant, items):
        """Enhanced rule-based categorization"""
        merchant_lower = merchant.lower()
        items_text = " ".join(items).lower()
        
        # Score each category
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in merchant_lower:
                    score += 3  # Merchant match is stronger
                if keyword in items_text:
                    score += 1  # Item match is weaker
            
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def _ai_categorization(self, merchant, amount, items, previous_categories):
        """AI-powered categorization with context"""
        
        items_text = ", ".join(items[:5]) if items else "No items listed"
        previous_context = ", ".join(set(previous_categories[-10:])) if previous_categories else "None"
        
        task = Task(
            description=f"""
            Analyze this expense and categorize it accurately:
            
            Merchant: {merchant}
            Amount: ${amount:.2f}
            Items purchased: {items_text}
            Recent categories used: {previous_context}
            
            Available categories: {', '.join(self.categories)}
            
            Consider:
            1. The merchant name and business type
            2. The items purchased (if available)
            3. The amount (some categories have typical ranges)
            4. Context from recent transactions
            
            Respond with JSON containing:
            {{
                "category": "exact_category_name",
                "reasoning": "brief explanation for the choice",
                "confidence": 0.95
            }}
            
            Choose the most appropriate category from the available list.
            """,
            agent=self.agent,
            expected_output="JSON object with categorization result"
        )
        
        try:
            result = task.execute()
            parsed = json.loads(result)
            
            category = parsed.get("category", "Other")
            if category not in self.categories:
                category = "Other"
                
            return {
                "category": category,
                "reasoning": parsed.get("reasoning", ""),
                "confidence": parsed.get("confidence", 0.7)
            }
            
        except Exception as e:
            print(f"AI categorization error: {e}")
            return None
    
    def _combine_categorization_results(self, rule_based, ai_result, merchant, items):
        """Combine rule-based and AI results with confidence scoring"""
        
        if rule_based and ai_result:
            if rule_based == ai_result["category"]:
                # Both agree - high confidence
                return rule_based, min(0.95, ai_result["confidence"] + 0.1)
            else:
                # Disagreement - prefer AI with moderate confidence
                return ai_result["category"], max(0.7, ai_result["confidence"] - 0.1)
        
        elif ai_result:
            return ai_result["category"], ai_result["confidence"]
        
        elif rule_based:
            return rule_based, 0.75
        
        else:
            # Fallback categorization based on amount patterns
            fallback = self._fallback_categorization(merchant, items)
            return fallback, 0.5
    
    def _fallback_categorization(self, merchant, items):
        """Last resort categorization"""
        merchant_lower = merchant.lower()
        
        # Common patterns
        if any(word in merchant_lower for word in ["food", "restaurant", "cafe"]):
            return "Food & Dining"
        elif any(word in merchant_lower for word in ["store", "shop", "mart"]):
            return "Shopping & Retail"
        elif any(word in merchant_lower for word in ["gas", "fuel", "oil"]):
            return "Transportation & Gas"
        else:
            return "Other"
    
    def _generate_explanation(self, merchant, amount, category, items):
        """Generate human-readable explanation for categorization"""
        
        explanations = {
            "Food & Dining": f"Meal/dining expense at {merchant}",
            "Groceries": f"Grocery shopping at {merchant}",
            "Shopping & Retail": f"Retail purchase at {merchant}",
            "Transportation & Gas": f"Transportation/fuel expense at {merchant}",
            "Entertainment & Recreation": f"Entertainment expense at {merchant}",
            "Healthcare & Medical": f"Healthcare expense at {merchant}",
            "Utilities & Bills": f"Utility/bill payment to {merchant}",
            "Home & Garden": f"Home improvement expense at {merchant}",
            "Education & Learning": f"Educational expense at {merchant}",
            "Travel & Vacation": f"Travel expense at {merchant}",
            "Professional Services": f"Professional service from {merchant}",
            "Subscriptions & Memberships": f"Subscription/membership fee to {merchant}",
            "Other": f"Miscellaneous expense at {merchant}"
        }
        
        base_explanation = explanations.get(category, f"Expense at {merchant}")
        
        # Add item context if available
        if items:
            item_preview = ", ".join(items[:2])
            base_explanation += f" (items: {item_preview})"
        
        return base_explanation
    
    def analyze_spending_patterns(self, expenses_data):
        """Analyze spending patterns and provide insights"""
        
        if not expenses_data:
            return []
        
        # Prepare analysis data
        total_amount = sum(exp['amount'] for exp in expenses_data)
        categories = {}
        merchants = {}
        monthly_trends = {}
        
        for exp in expenses_data:
            # Category analysis
            cat = exp.get('category', 'Other')
            categories[cat] = categories.get(cat, 0) + exp['amount']
            
            # Merchant analysis
            merchant = exp.get('merchant', 'Unknown')
            merchants[merchant] = merchants.get(merchant, 0) + exp['amount']
            
            # Monthly trends
            date = exp.get('date', '')
            month = date[:7] if date else 'Unknown'
            monthly_trends[month] = monthly_trends.get(month, 0) + exp['amount']
        
        task = Task(
            description=f"""
            Analyze this spending data and provide actionable financial insights:
            
            Total Spending: ${total_amount:.2f}
            Number of Transactions: {len(expenses_data)}
            
            Category Breakdown:
            {json.dumps(categories, indent=2)}
            
            Top Merchants:
            {json.dumps(dict(sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:10]), indent=2)}
            
            Monthly Trends:
            {json.dumps(monthly_trends, indent=2)}
            
            Provide 5-7 specific, actionable insights in JSON format:
            {{
                "insights": [
                    "Specific insight about spending patterns...",
                    "Actionable recommendation for improvement...",
                    "Notable trend or opportunity..."
                ],
                "top_recommendations": [
                    "Priority action item 1",
                    "Priority action item 2"
                ],
                "spending_health": "excellent|good|moderate|concerning",
                "key_metrics": {{
                    "top_category": "category name",
                    "top_category_percentage": 0.35,
                    "average_transaction": 45.67
                }}
            }}
            
            Focus on practical advice for better financial management.
            """,
            agent=self.agent,
            expected_output="JSON object with comprehensive spending analysis"
        )
        
        try:
            result = task.execute()
            return json.loads(result)
        except Exception as e:
            print(f"Spending analysis error: {e}")
            return {
                "insights": ["Unable to generate detailed insights at this time."],
                "top_recommendations": ["Review your spending regularly"],
                "spending_health": "unknown",
                "key_metrics": {}
            }