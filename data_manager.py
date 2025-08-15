import pandas as pd
import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, data_file="expenses.json"):
        self.data_file = data_file
        self.ensure_data_file()
    
    def ensure_data_file(self):
        """Ensure the data file exists"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump([], f)
    
    def load_expenses(self):
        """Load expenses from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            if not data:
                return pd.DataFrame(columns=[
                    'date', 'merchant', 'amount', 'category', 'confidence', 'description',
                    'ai_tags', 'is_recurring', 'timestamp'
                ])
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            # Handle missing columns for backward compatibility
            if 'ai_tags' not in df.columns:
                df['ai_tags'] = df.apply(lambda x: [], axis=1)
            if 'is_recurring' not in df.columns:
                df['is_recurring'] = False
            if 'timestamp' not in df.columns:
                df['timestamp'] = datetime.now().isoformat()
            
            return df.sort_values('date', ascending=False)
            
        except Exception as e:
            print(f"Error loading expenses: {e}")
            return pd.DataFrame(columns=[
                'date', 'merchant', 'amount', 'category', 'confidence', 'description',
                'ai_tags', 'is_recurring', 'timestamp'
            ])
    
    def save_expenses(self, expenses_df):
        """Save expenses DataFrame to JSON file"""
        try:
            data = expenses_df.to_dict('records')
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving expenses: {e}")
            return False
    
    def add_expense(self, expense_data):
        """Add a new expense"""
        try:
            # Load existing data
            expenses_df = self.load_expenses()
            
            # Add timestamp for uniqueness
            expense_data['timestamp'] = datetime.now().isoformat()
            
            # Convert to DataFrame and append
            new_expense_df = pd.DataFrame([expense_data])
            
            if expenses_df.empty:
                updated_df = new_expense_df
            else:
                updated_df = pd.concat([expenses_df, new_expense_df], ignore_index=True)
            
            # Save updated data
            return self.save_expenses(updated_df)
            
        except Exception as e:
            print(f"Error adding expense: {e}")
            return False
    
    def delete_expense(self, index):
        """Delete an expense by index"""
        try:
            expenses_df = self.load_expenses()
            
            if 0 <= index < len(expenses_df):
                expenses_df = expenses_df.drop(expenses_df.index[index])
                return self.save_expenses(expenses_df)
            
            return False
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    def update_expense(self, index, updated_data):
        """Update an existing expense"""
        try:
            expenses_df = self.load_expenses()
            
            if 0 <= index < len(expenses_df):
                for key, value in updated_data.items():
                    expenses_df.iloc[index, expenses_df.columns.get_loc(key)] = value
                
                return self.save_expenses(expenses_df)
            
            return False
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False
    
    def get_category_summary(self):
        """Get spending summary by category"""
        try:
            expenses_df = self.load_expenses()
            
            if expenses_df.empty:
                return {}
            
            summary = expenses_df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).to_dict()
            return summary
            
        except Exception as e:
            print(f"Error getting category summary: {e}")
            return {}
    
    def get_monthly_summary(self):
        """Get spending summary by month"""
        try:
            expenses_df = self.load_expenses()
            
            if expenses_df.empty:
                return {}
            
            expenses_df['month'] = pd.to_datetime(expenses_df['date']).dt.to_period('M')
            summary = expenses_df.groupby('month')['amount'].sum().to_dict()
            
            # Convert periods to strings for JSON serialization
            return {str(k): v for k, v in summary.items()}
            
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return {}
    
    def clear_all_data(self):
        """Clear all expense data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump([], f)
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def export_to_csv(self):
        """Export expenses to CSV string"""
        try:
            expenses_df = self.load_expenses()
            return expenses_df.to_csv(index=False)
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""
    
    def export_to_json(self):
        """Export expenses to JSON string"""
        try:
            expenses_df = self.load_expenses()
            return expenses_df.to_json(orient='records', indent=2)
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return ""
