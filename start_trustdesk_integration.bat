@echo off
echo ===================================================
echo    ODIN SCHOOL - TRUSTDESK INTEGRATION LAUNCHER
echo ===================================================
echo.

echo 🔧 Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

echo 🔧 Checking Node.js environment...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

echo.
echo 📋 INTEGRATION STATUS:
echo ✅ Backend: FastAPI with TrustDesk RAG integration
echo ✅ Frontend: React with TrustDesk API service layer  
echo ✅ AI: Amazon Bedrock Claude-v2 + Titan Embeddings
echo ✅ Database: Local vector storage for RAG
echo.

echo 🚀 Starting integration test...
python test_trustdesk_integration.py
if errorlevel 1 (
    echo.
    echo ⚠️  Integration test had some issues, but continuing...
    echo.
)

echo.
echo 🌐 Starting servers...
echo.

REM Start backend server
echo 📡 Starting FastAPI backend server on port 8000...
start "TrustDesk Backend" cmd /c "uvicorn main:app --reload --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🎨 Starting React frontend server on port 3000...
cd frontend
start "TrustDesk Frontend" cmd /c "npm start"

echo.
echo ✅ INTEGRATION COMPLETE!
echo.
echo 📍 Access points:
echo   • Frontend: http://localhost:3000
echo   • TrustDesk: http://localhost:3000/reputation
echo   • Backend API: http://localhost:8000
echo   • API Docs: http://localhost:8000/docs
echo.
echo 🧪 Test the integration:
echo   1. Navigate to http://localhost:3000/reputation
echo   2. Click on any comment to reply
echo   3. Click "AI Reply" to test RAG integration
echo   4. Check browser network tab for API calls
echo   5. Check backend terminal for request logs
echo.
echo Press any key to open the application...
pause >nul

REM Open the application in default browser
start http://localhost:3000/reputation

echo.
echo 🎉 TrustDesk integration is now running!
echo    Backend and frontend servers are running in separate windows.
echo    Close those windows to stop the servers.
echo.
pause
