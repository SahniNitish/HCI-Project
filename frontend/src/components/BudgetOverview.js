import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrendingUp, AlertTriangle } from "lucide-react";

export default function BudgetOverview({ budgets, expenses }) {
  if (!budgets || budgets.length === 0) {
    return (
      <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            Budget Overview
          </CardTitle>
          <CardDescription>Set budgets to track your spending limits</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-4">No budgets set yet</p>
        </CardContent>
      </Card>
    );
  }

  const currentDate = new Date();
  const currentMonth = currentDate.getMonth() + 1;
  const currentYear = currentDate.getFullYear();

  const calculateSpent = (category) => {
    return expenses
      .filter((exp) => {
        const expDate = new Date(exp.date);
        return (
          exp.category === category &&
          expDate.getMonth() + 1 === currentMonth &&
          expDate.getFullYear() === currentYear
        );
      })
      .reduce((sum, exp) => sum + exp.amount, 0);
  };

  const currentBudgets = budgets.filter(
    (b) => b.month === currentMonth && b.year === currentYear
  );

  if (currentBudgets.length === 0) {
    return (
      <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            Budget Overview
          </CardTitle>
          <CardDescription>No budgets for current month</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm" data-testid="budget-overview">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-green-600" />
          Budget Overview
        </CardTitle>
        <CardDescription>Your spending vs budget for this month</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {currentBudgets.map((budget) => {
            const spent = calculateSpent(budget.category);
            const percentage = (spent / budget.limit) * 100;
            const isOverBudget = percentage > 100;
            const isNearLimit = percentage > 80 && !isOverBudget;

            return (
              <div key={budget.id} className="space-y-2" data-testid={`budget-item-${budget.category}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{budget.category}</span>
                    {(isOverBudget || isNearLimit) && (
                      <AlertTriangle
                        className={`w-4 h-4 ${isOverBudget ? 'text-red-600' : 'text-yellow-600'}`}
                      />
                    )}
                  </div>
                  <span className="text-sm text-gray-600">
                    ${spent.toFixed(2)} / ${budget.limit.toFixed(2)}
                  </span>
                </div>
                <Progress
                  value={Math.min(percentage, 100)}
                  className="h-2"
                  indicatorClassName={isOverBudget ? 'bg-red-600' : isNearLimit ? 'bg-yellow-600' : 'bg-green-600'}
                />
                <p className="text-xs text-gray-500">
                  {percentage.toFixed(0)}% used
                  {isOverBudget && " - Over budget!"}
                  {isNearLimit && " - Near limit"}
                </p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}