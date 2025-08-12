@echo off
echo Installing Odin School Analytics Hub...
echo.

echo Step 1: Installing Node.js dependencies...
call npm install

echo.
echo Step 2: Starting development server...
echo The application will open in your browser at http://localhost:3000
echo.

call npm start

pause
