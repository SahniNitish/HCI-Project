import { Trash2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function ExpenseList({ expenses, onDelete }) {
  if (!expenses || expenses.length === 0) {
    return (
      <div className="text-center py-12" data-testid="no-expenses">
        <p className="text-gray-500">No expenses yet. Start tracking your spending!</p>
      </div>
    );
  }

  const getCategoryColor = (category) => {
    const colors = {
      Food: "bg-orange-100 text-orange-700",
      Transportation: "bg-blue-100 text-blue-700",
      Shopping: "bg-pink-100 text-pink-700",
      Entertainment: "bg-purple-100 text-purple-700",
      Bills: "bg-red-100 text-red-700",
      Healthcare: "bg-green-100 text-green-700",
      Education: "bg-indigo-100 text-indigo-700",
      Other: "bg-gray-100 text-gray-700"
    };
    return colors[category] || colors.Other;
  };

  return (
    <div className="space-y-3" data-testid="expense-list">
      {expenses.map((expense) => (
        <div
          key={expense.id}
          data-testid={`expense-item-${expense.id}`}
          className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm"
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-medium text-gray-900">{expense.description}</h4>
              {expense.ai_categorized && (
                <Sparkles className="w-4 h-4 text-purple-600" title="AI Categorized" />
              )}
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Badge className={getCategoryColor(expense.category)}>{expense.category}</Badge>
              <span>•</span>
              <span>{new Date(expense.date).toLocaleDateString()}</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-lg font-semibold text-gray-900">${expense.amount.toFixed(2)}</span>
            <Button
              data-testid={`delete-expense-${expense.id}`}
              variant="ghost"
              size="sm"
              onClick={() => onDelete(expense.id)}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}