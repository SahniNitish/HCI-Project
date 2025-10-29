import sys
from pathlib import Path

# Add parent directory to path to import server
sys.path.append(str(Path(__file__).parent.parent))

from server import app

# Export the FastAPI app for Vercel
# Vercel will automatically handle the ASGI interface
