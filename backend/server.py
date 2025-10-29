from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import json

# Try to import emergentintegrations, use mock if not available
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:
    # Mock classes for when emergentintegrations is not available
    class UserMessage:
        def __init__(self, text: str):
            self.text = text

    class LlmChat:
        def __init__(self, **kwargs):
            pass

        async def run_astream(self, message):
            yield {"type": "text", "text": "Other"}

ROOT_DIR = Path(__file__).parent
# Load .env only if it exists (for local development)
env_file = ROOT_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
if not mongo_url:
    raise RuntimeError("MONGO_URL environment variable is not set")

client = AsyncIOMotorClient(mongo_url)
db_name = os.environ.get('DB_NAME', 'expense_tracker_db')
db = client[db_name]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your_jwt_secret_key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# ==================== Models ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExpenseCreate(BaseModel):
    amount: float
    category: Optional[str] = None
    description: str
    date: str  # YYYY-MM-DD format

class Expense(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    amount: float
    category: str
    description: str
    date: str
    ai_categorized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BudgetCreate(BaseModel):
    category: str
    limit: float
    month: int
    year: int

class Budget(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    category: str
    limit: float
    month: int
    year: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIInsight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insight_type: str
    content: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    month: Optional[int] = None
    year: Optional[int] = None

class DashboardStats(BaseModel):
    total_expenses: float
    expense_count: int
    top_category: str
    monthly_trend: List[dict]
    category_breakdown: List[dict]

# ==================== Helper Functions ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token(user_id: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    token_data = {"user_id": user_id, "exp": expiration}
    return jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def categorize_expense_with_ai(description: str, amount: float) -> str:
    """Use AI to categorize expense based on description and amount"""
    try:
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=llm_key,
            session_id="expense_categorization",
            system_message="You are an expense categorization assistant. Categorize expenses into one of these categories ONLY: Food, Transportation, Shopping, Entertainment, Bills, Healthcare, Education, Other. Return only the category name, nothing else."
        ).with_model("openai", "gpt-4o")
        
        message = UserMessage(text=f"Categorize this expense: '{description}' (Amount: ${amount})")
        response = await chat.send_message(message)
        
        category = response.strip()
        valid_categories = ["Food", "Transportation", "Shopping", "Entertainment", "Bills", "Healthcare", "Education", "Other"]
        
        if category in valid_categories:
            return category
        return "Other"
    except Exception as e:
        logging.error(f"AI categorization failed: {e}")
        return "Other"

async def generate_financial_advice(user_id: str) -> str:
    """Generate personalized financial advice based on user's spending patterns"""
    try:
        # Get last 30 days of expenses
        expenses = await db.expenses.find({"user_id": user_id}).sort("created_at", -1).limit(100).to_list(100)
        
        if not expenses:
            return "Start tracking your expenses to get personalized financial advice!"
        
        # Calculate spending by category
        category_totals = {}
        total_spent = 0
        for exp in expenses:
            cat = exp.get('category', 'Other')
            amt = exp.get('amount', 0)
            category_totals[cat] = category_totals.get(cat, 0) + amt
            total_spent += amt
        
        # Get budgets
        budgets = await db.budgets.find({"user_id": user_id}).to_list(100)
        
        # Prepare context for AI
        context = f"""User's spending data:
- Total spent: ${total_spent:.2f}
- Number of transactions: {len(expenses)}
- Spending by category: {json.dumps(category_totals, indent=2)}
- Budgets: {json.dumps([{'category': b['category'], 'limit': b['limit']} for b in budgets], indent=2)}
"""
        
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"financial_advisor_{user_id}",
            system_message="You are a personal financial advisor. Analyze the user's spending patterns and provide 3-4 actionable, personalized savings tips. Be encouraging and specific. Format your response as a list of tips."
        ).with_model("openai", "gpt-4o")
        
        message = UserMessage(text=context)
        response = await chat.send_message(message)
        
        return response
    except Exception as e:
        logging.error(f"Financial advice generation failed: {e}")
        return "Unable to generate advice at this time. Please try again later."

# ==================== Auth Routes ====================

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name
    )
    
    user_doc = user.model_dump()
    user_doc['password_hash'] = hash_password(user_data.password)
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user.id)
    return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.name}}

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc or not verify_password(credentials.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user_doc['id'])
    return {"token": token, "user": {"id": user_doc['id'], "email": user_doc['email'], "name": user_doc['name']}}

@api_router.get("/auth/me", response_model=User)
async def get_me(user_id: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return user_doc

# ==================== Expense Routes ====================

@api_router.post("/expenses", response_model=Expense)
async def create_expense(expense_data: ExpenseCreate, user_id: str = Depends(get_current_user)):
    # Auto-categorize if no category provided
    category = expense_data.category
    ai_categorized = False
    
    if not category:
        category = await categorize_expense_with_ai(expense_data.description, expense_data.amount)
        ai_categorized = True
    
    expense = Expense(
        user_id=user_id,
        amount=expense_data.amount,
        category=category,
        description=expense_data.description,
        date=expense_data.date,
        ai_categorized=ai_categorized
    )
    
    expense_doc = expense.model_dump()
    expense_doc['created_at'] = expense_doc['created_at'].isoformat()
    
    await db.expenses.insert_one(expense_doc)
    return expense

@api_router.get("/expenses", response_model=List[Expense])
async def get_expenses(user_id: str = Depends(get_current_user)):
    expenses = await db.expenses.find({"user_id": user_id}, {"_id": 0}).sort("date", -1).to_list(1000)
    
    for exp in expenses:
        if isinstance(exp.get('created_at'), str):
            exp['created_at'] = datetime.fromisoformat(exp['created_at'])
    
    return expenses

@api_router.delete("/expenses/{expense_id}")
async def delete_expense(expense_id: str, user_id: str = Depends(get_current_user)):
    result = await db.expenses.delete_one({"id": expense_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

# ==================== Budget Routes ====================

@api_router.post("/budgets", response_model=Budget)
async def create_budget(budget_data: BudgetCreate, user_id: str = Depends(get_current_user)):
    # Check if budget already exists for this category/month/year
    existing = await db.budgets.find_one({
        "user_id": user_id,
        "category": budget_data.category,
        "month": budget_data.month,
        "year": budget_data.year
    })
    
    if existing:
        # Update existing budget
        await db.budgets.update_one(
            {"id": existing['id']},
            {"$set": {"limit": budget_data.limit}}
        )
        existing['limit'] = budget_data.limit
        if isinstance(existing.get('created_at'), str):
            existing['created_at'] = datetime.fromisoformat(existing['created_at'])
        return existing
    
    budget = Budget(
        user_id=user_id,
        category=budget_data.category,
        limit=budget_data.limit,
        month=budget_data.month,
        year=budget_data.year
    )
    
    budget_doc = budget.model_dump()
    budget_doc['created_at'] = budget_doc['created_at'].isoformat()
    
    await db.budgets.insert_one(budget_doc)
    return budget

@api_router.get("/budgets", response_model=List[Budget])
async def get_budgets(user_id: str = Depends(get_current_user)):
    budgets = await db.budgets.find({"user_id": user_id}, {"_id": 0}).to_list(100)
    
    for budget in budgets:
        if isinstance(budget.get('created_at'), str):
            budget['created_at'] = datetime.fromisoformat(budget['created_at'])
    
    return budgets

# ==================== Dashboard & Analytics ====================

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user_id: str = Depends(get_current_user)):
    expenses = await db.expenses.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    if not expenses:
        return {
            "total_expenses": 0,
            "expense_count": 0,
            "top_category": "None",
            "monthly_trend": [],
            "category_breakdown": []
        }
    
    # Calculate stats
    total_expenses = sum(exp['amount'] for exp in expenses)
    expense_count = len(expenses)
    
    # Category breakdown
    category_totals = {}
    for exp in expenses:
        cat = exp['category']
        category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
    
    category_breakdown = [{"category": k, "amount": v} for k, v in category_totals.items()]
    category_breakdown.sort(key=lambda x: x['amount'], reverse=True)
    
    top_category = category_breakdown[0]['category'] if category_breakdown else "None"
    
    # Monthly trend (last 6 months)
    monthly_totals = {}
    for exp in expenses:
        month_key = exp['date'][:7]  # YYYY-MM
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + exp['amount']
    
    monthly_trend = [{"month": k, "amount": v} for k, v in sorted(monthly_totals.items())[-6:]]
    
    return {
        "total_expenses": total_expenses,
        "expense_count": expense_count,
        "top_category": top_category,
        "monthly_trend": monthly_trend,
        "category_breakdown": category_breakdown
    }

# ==================== AI Financial Advisor ====================

@api_router.get("/ai/financial-advice")
async def get_financial_advice(user_id: str = Depends(get_current_user)):
    advice = await generate_financial_advice(user_id)
    
    # Save insight to database
    insight = AIInsight(
        user_id=user_id,
        insight_type="financial_advice",
        content=advice
    )
    
    insight_doc = insight.model_dump()
    insight_doc['generated_at'] = insight_doc['generated_at'].isoformat()
    
    await db.ai_insights.insert_one(insight_doc)
    
    return {"advice": advice}

@api_router.get("/ai/insights", response_model=List[AIInsight])
async def get_ai_insights(user_id: str = Depends(get_current_user)):
    insights = await db.ai_insights.find({"user_id": user_id}, {"_id": 0}).sort("generated_at", -1).limit(10).to_list(10)
    
    for insight in insights:
        if isinstance(insight.get('generated_at'), str):
            insight['generated_at'] = datetime.fromisoformat(insight['generated_at'])
    
    return insights

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Vercel serverless handler using Mangum
from mangum import Mangum
handler = Mangum(app, lifespan="off")