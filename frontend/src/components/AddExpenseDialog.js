import { useState } from "react";
import axios from "axios";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CATEGORIES = ["Food", "Transportation", "Shopping", "Entertainment", "Bills", "Healthcare", "Education", "Other"];

export default function AddExpenseDialog({ open, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    amount: "",
    category: "",
    description: "",
    date: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(false);
  const [useAI, setUseAI] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        amount: parseFloat(formData.amount),
        description: formData.description,
        date: formData.date,
        category: useAI ? null : formData.category
      };

      await axios.post(`${API}/expenses`, payload);
      toast.success(useAI ? "Expense added with AI categorization!" : "Expense added successfully!");
      setFormData({
        amount: "",
        category: "",
        description: "",
        date: new Date().toISOString().split('T')[0]
      });
      onSuccess();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to add expense");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md" data-testid="add-expense-dialog">
        <DialogHeader>
          <DialogTitle>Add New Expense</DialogTitle>
          <DialogDescription>
            Track your spending and let AI categorize it for you
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="amount">Amount ($)</Label>
            <Input
              id="amount"
              data-testid="expense-amount-input"
              type="number"
              step="0.01"
              placeholder="0.00"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              data-testid="expense-description-input"
              placeholder="e.g., Grocery shopping at Walmart"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="date">Date</Label>
            <Input
              id="date"
              data-testid="expense-date-input"
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="useAI"
              data-testid="use-ai-checkbox"
              checked={useAI}
              onChange={(e) => setUseAI(e.target.checked)}
              className="rounded"
            />
            <Label htmlFor="useAI" className="cursor-pointer">
              Use AI to categorize automatically
            </Label>
          </div>

          {!useAI && (
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
                required={!useAI}
              >
                <SelectTrigger data-testid="expense-category-select">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent position="popper" sideOffset={5}>
                  {CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat} data-testid={`expense-category-${cat}`}>
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <div className="flex gap-3">
            <Button type="button" variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button
              type="submit"
              data-testid="submit-expense-button"
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              disabled={loading}
            >
              {loading ? "Adding..." : "Add Expense"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}