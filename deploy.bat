@echo off
title GEO Monitor Deploy Tool
echo.
echo =========================================
echo    GEO AI Monitor - Deploy Tool
echo =========================================
echo.

REM Check Git
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git not found
    echo Please install Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git installed
echo.

REM Check files
if not exist "index.html" (
    echo [ERROR] index.html not found
    echo Please run this script in geo-monitor folder
    pause
    exit /b 1
)

echo [OK] Files checked
echo.

echo Select deploy method:
echo.
echo 1. Vercel Deploy (Recommend - Auto update)
echo 2. GitHub Pages Deploy (Simple)
echo 3. Create GitHub Repo only
echo 0. Exit
echo.

set /p choice="Enter option (0-3): "

if "%choice%"=="1" goto VERCEL
if "%choice%"=="2" goto GITHUB_PAGES
if "%choice%"=="3" goto CREATE_REPO
if "%choice%"=="0" goto EXIT
goto MENU

:CREATE_REPO
echo.
echo Creating GitHub Repository...
echo.
set /p username="Enter your GitHub username: "

echo.
echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit"

echo.
echo Please create GitHub repository:
echo https://github.com/new
echo.
echo Repository name: geo-monitor
echo Select: Public
echo.
pause

echo.
echo Enter repository URL (e.g., https://github.com/%username%/geo-monitor.git):
set /p repo_url="Repo URL: "

git remote add origin %repo_url%
git branch -M main
git push -u origin main

echo.
echo [OK] Repository created!
echo URL: https://github.com/%username%/geo-monitor
echo.
pause
goto MENU

:VERCEL
echo.
echo Vercel Deploy...
echo.
echo Prerequisites:
echo 1. Register at https://github.com
echo 2. Login at https://vercel.com with GitHub
echo 3. Push code to GitHub repository
echo.
pause

echo.
echo Visit Vercel to import project:
echo https://vercel.com/new
echo.
echo Steps:
echo 1. Click "Import Git Repository"
echo 2. Select geo-monitor repository
echo 3. Framework Preset: Other
echo 4. Click "Deploy"
echo.
echo After deploy, you will get URL like:
echo https://geo-monitor-xxx.vercel.app
echo.
start https://vercel.com/new
pause
goto MENU

:GITHUB_PAGES
echo.
echo GitHub Pages Deploy...
echo.
echo Steps:
echo 1. Visit https://github.com/new
echo 2. Repository name: geo-monitor
echo 3. Select: Public
echo 4. Check "Add a README file"
echo 5. Click "Create repository"
echo.
echo Then:
echo 1. Click "Add file" -^> "Upload files"
echo 2. Drag and drop index.html
echo 3. Click "Commit changes"
echo 4. Go to Settings -^> Pages
echo 5. Source: Deploy from a branch
echo 6. Branch: main, Folder: / (root)
echo 7. Click "Save"
echo.
echo Wait 2-5 minutes, then visit:
echo https://yourname.github.io/geo-monitor
echo.
start https://github.com/new
pause
goto MENU

:EXIT
echo.
echo Thank you!
echo.
echo After deploy, you can:
echo - Share the URL with friends
echo - Generate QR code
echo - Embed in other websites
echo.
pause
exit /b 0
