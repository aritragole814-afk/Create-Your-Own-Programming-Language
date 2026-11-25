@echo off
echo ====================================================
echo Pushing NovaLang project to GitHub...
echo ====================================================
git push -u origin main
echo.
if %errorlevel% equ 0 (
    echo ====================================================
    echo [SUCCESS] Project successfully pushed to GitHub!
    echo Submit this URL to your teacher:
    echo https://github.com/aritragole814-afk/Create-Your-Own-Programming-Language
    echo ====================================================
) else (
    echo [ERROR] Push failed. Please make sure the repo exists on GitHub.
)
pause
