import { useState } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Sparkles, Loader2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AIAdvisor() {
  const [advice, setAdvice] = useState(null);
  const [loading, setLoading] = useState(false);

  const getAdvice = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/ai/financial-advice`);
      setAdvice(response.data.advice);
    } catch (error) {
      toast.error("Failed to generate advice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-blue-50" data-testid="ai-advisor-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-600" />
          AI Financial Advisor
        </CardTitle>
        <CardDescription>Get personalized savings tips based on your spending patterns</CardDescription>
      </CardHeader>
      <CardContent>
        {!advice ? (
          <div className="text-center py-8">
            <Button
              data-testid="get-advice-button"
              onClick={getAdvice}
              disabled={loading}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Analyzing your spending...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Get AI Financial Advice
                </>
              )}
            </Button>
          </div>
        ) : (
          <div className="space-y-4" data-testid="advice-content">
            <div className="p-4 rounded-lg bg-white/70 backdrop-blur-sm border border-purple-200">
              <div className="whitespace-pre-wrap text-gray-700">{advice}</div>
            </div>
            <Button
              data-testid="refresh-advice-button"
              onClick={getAdvice}
              disabled={loading}
              variant="outline"
              size="sm"
            >
              {loading ? "Generating..." : "Get New Advice"}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}