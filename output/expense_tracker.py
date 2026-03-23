"""
Expense Tracker Module
Simple expense tracking with add, list, and category total functions.
"""

import json
import os
from datetime import datetime

# Global list to store expenses
expenses = []


def add_expense(amount, category, description=""):
    """Add a new expense to the tracker.
    
    Args:
        amount: The expense amount (float or int)
        category: The expense category (string)
        description: Optional description (string)
    """
    expense = {
        "id": len(expenses) + 1,
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    expenses.append(expense)
    return expense


def list_expenses():
    """List all expenses in the tracker.
    
    Returns:
        List of all expense dictionaries
    """
    return expenses.copy()


def calculate_total_by_category():
    """Calculate total expenses by category.
    
    Returns:
        Dictionary with categories as keys and total amounts as values
    """
    category_totals = {}
    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]
        category_totals[category] = category_totals.get(category, 0) + amount
    return category_totals


def save_to_file(filename="expenses.json"):
    """Save expenses to a JSON file.
    
    Args:
        filename: Name of the file to save to
    """
    with open(filename, "w") as f:
        json.dump(expenses, f, indent=2)


def load_from_file(filename="expenses.json"):
    """Load expenses from a JSON file.
    
    Args:
        filename: Name of the file to load from
    """
    global expenses
    if os.path.exists(filename):
        with open(filename, "r") as f:
            expenses = json.load(f)


def clear_expenses():
    """Clear all expenses from the tracker."""
    global expenses
    expenses.clear()


if __name__ == "__main__":
    # Example usage
    print("Expense Tracker Module")
    print("=" * 50)
    
    # Add some example expenses
    add_expense(25.50, "Food", "Lunch at cafe")
    add_expense(45.00, "Transport", "Bus pass")
    add_expense(12.99, "Food", "Groceries")
    add_expense(100.00, "Entertainment", "Movie tickets")
    
    # List all expenses
    print("\nAll Expenses:")
    for expense in list_expenses():
        print(f"ID: {expense['id']}, Amount: ${expense['amount']:.2f}, "
              f"Category: {expense['category']}, Description: {expense['description']}")
    
    # Calculate totals by category
    print("\nTotals by Category:")
    totals = calculate_total_by_category()
    for category, total in totals.items():
        print(f"{category}: ${total:.2f}")
    
    # Save to file
    save_to_file()
    print(f"\nSaved {len(expenses)} expenses to expenses.json")