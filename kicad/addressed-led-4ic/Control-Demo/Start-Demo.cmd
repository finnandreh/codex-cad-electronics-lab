@echo off
cd /d "%~dp0"
where node >nul 2>nul || (echo Install Node.js 20 or newer from nodejs.org first. & pause & exit /b 1)
if not exist node_modules call npm ci --ignore-scripts --no-fund --no-audit
if errorlevel 1 exit /b 1
echo Open http://127.0.0.1:8788 after the server is ready.
echo Press Ctrl+C to stop only this local demonstration.
node server.mjs
