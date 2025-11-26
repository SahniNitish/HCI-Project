# Personal Finance Manager

A full-stack personal finance management application built with React frontend and FastAPI backend.

## Prerequisites

- Node.js and npm
- Python 3.9+

## Installation and Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install --legacy-peer-deps
```

## Running the Application

### Start the Backend Server

1. Navigate to the backend directory and activate virtual environment:
```bash
cd backend
source venv/bin/activate
```

2. Start the FastAPI server:
```bash
python server.py
```

The backend will run on `http://localhost:8000`

### Start the Frontend Server

1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. The application should load with the personal finance management interface
3. Both servers must be running simultaneously for full functionality

## Stopping the Application

To stop the servers:
- Press `Ctrl+C` in both terminal windows
- Deactivate the Python virtual environment: `deactivate`
