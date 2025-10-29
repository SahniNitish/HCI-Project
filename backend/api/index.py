import sys
import os
from pathlib import Path

# Add parent directory to path to import server
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

# Import the FastAPI app
from server import app

# This is required for Vercel to recognize the app
app = app
