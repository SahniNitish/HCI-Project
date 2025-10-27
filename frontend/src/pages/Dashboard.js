import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { LogOut, Plus, TrendingUp, DollarSign, ShoppingBag, Sparkles, Calendar } from "lucide-react";
import AddExpenseDialog from "@/components/AddExpenseDialog";
import SetBudgetDialog from "@/components/SetBudgetDialog";
import ExpenseList from "@/components/ExpenseList";
import CategoryChart from "@/components/CategoryChart";
import MonthlyTrendChart from "@/components/MonthlyTrendChart";
import AIAdvisor from "@/components/AIAdvisor";
import BudgetOverview from "@/components/BudgetOverview";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard({ user, onLogout }) {
  const [expenses, setExpenses] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [showSetBudget, setShowSetBudget] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [expensesRes, budgetsRes, statsRes] = await Promise.all([
        axios.get(`${API}/expenses`),
        axios.get(`${API}/budgets`),
        axios.get(`${API}/dashboard/stats`)
      ]);
      setExpenses(expensesRes.data);
      setBudgets(budgetsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleExpenseAdded = () => {
    fetchData();
    setShowAddExpense(false);
  };

  const handleBudgetSet = () => {
    fetchData();
    setShowSetBudget(false);
  };

  const handleDeleteExpense = async (expenseId) => {
    try {
      await axios.delete(`${API}/expenses/${expenseId}`);
      toast.success("Expense deleted");
      fetchData();
    } catch (error) {
      toast.error("Failed to delete expense");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome back, {user.name}!</h1>
              <p className="text-sm text-gray-600">Track, analyze, and optimize your spending</p>
            </div>
            <div className="flex items-center gap-3">
              <Button
                data-testid="add-expense-button"
                onClick={() => setShowAddExpense(true)}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Expense
              </Button>
              <Button
                data-testid="set-budget-button"
                onClick={() => setShowSetBudget(true)}
                variant="outline"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Set Budget
              </Button>
              <Button
                data-testid="logout-button"
                onClick={onLogout}
                variant="ghost"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Expenses</CardTitle>
              <DollarSign className="w-4 h-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">${stats?.total_expenses?.toFixed(2) || "0.00"}</div>
              <p className="text-xs text-gray-500 mt-1">{stats?.expense_count || 0} transactions</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Top Category</CardTitle>
              <ShoppingBag className="w-4 h-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats?.top_category || "None"}</div>
              <p className="text-xs text-gray-500 mt-1">Highest spending</p>
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">This Month</CardTitle>
              <Calendar className="w-4 h-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                ${stats?.monthly_trend?.slice(-1)[0]?.amount?.toFixed(2) || "0.00"}
              </div>
              <p className="text-xs text-gray-500 mt-1">Current month spending</p>
            </CardContent>
          </Card>
        </div>

        {/* AI Financial Advisor */}
        <div className="mb-8">
          <AIAdvisor />
        </div>

        {/* Budget Overview */}
        <div className="mb-8">
          <BudgetOverview budgets={budgets} expenses={expenses} />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                Category Breakdown
              </CardTitle>
              <CardDescription>Your spending by category</CardDescription>
            </CardHeader>
            <CardContent>
              <CategoryChart data={stats?.category_breakdown || []} />
            </CardContent>
          </Card>

          <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                Monthly Trend
              </CardTitle>
              <CardDescription>Last 6 months spending</CardDescription>
            </CardHeader>
            <CardContent>
              <MonthlyTrendChart data={stats?.monthly_trend || []} />
            </CardContent>
          </Card>
        </div>

        {/* Expense List */}
        <Card className="border-0 shadow-lg bg-white/90 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Recent Expenses</CardTitle>
            <CardDescription>Your latest transactions</CardDescription>
          </CardHeader>
          <CardContent>
            <ExpenseList expenses={expenses} onDelete={handleDeleteExpense} />
          </CardContent>
        </Card>
      </div>

      {/* Dialogs */}
      <AddExpenseDialog
        open={showAddExpense}
        onClose={() => setShowAddExpense(false)}
        onSuccess={handleExpenseAdded}
      />
      <SetBudgetDialog
        open={showSetBudget}
        onClose={() => setShowSetBudget(false)}
        onSuccess={handleBudgetSet}
      />
    </div>
  );
}