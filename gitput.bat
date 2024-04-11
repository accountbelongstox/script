@echo off
SETLOCAL EnableDelayedExpansion
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "DEL=%%a"
)

for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set datetime=%%a
set "year=%datetime:~0,4%"
set "month=%datetime:~4,2%"
set "day=%datetime:~6,2%"
set "hour=%datetime:~8,2%"
set "minute=%datetime:~10,2%"
set "second=%datetime:~12,2%"
set "timestamp=%year%-%month%-%day%@%hour%-%minute%-%second%"
set "core_node_dir=%~dp0core_node\"

call :ColorText 0a "-------------------"
echo.
call :ColorText 0C "Submit_github"
echo.
call :ColorText 0b "-------------------"
echo.
call :ColorText 19 "-------------------"
echo.
call :ColorText 2F "%timestamp%"
echo.
call :ColorText 4e "-------------------"
echo.

echo.
call :ColorText 0a "Entering--" 
echo %cd%
call :ColorText 0a "--------------------------------" 
echo.
git remote -v
call :ColorText 0a "--------------------------------" 
echo.
echo.
echo.
call :ColorText 2F "----------------------------------------------------------------" 
echo.
git add .
git commit -m "%timestamp%"
git pull
git add .
git commit -m "%timestamp%"
git push --set-upstream origin main
echo.
call :ColorText 19 "----------------------------------------------------------------" 
echo.
echo.

if exist "%core_node_dir%" (
    cd /d "%core_node_dir%"
    call :ColorText 0a "Entering--" 
    echo %core_node_dir%
    call :ColorText 0a "--------------------------------" 
    echo.
    git remote -v
    call :ColorText 0a "--------------------------------" 
    echo.
    echo Current working directory: %cd%
    echo.
    echo.
    call :ColorText 2F "----------------------------------------------------------------" 
    echo.
    git add .
    git commit -m "%timestamp%"
    git pull
    git add .
    git commit -m "%timestamp%"
    git push --set-upstream origin main
    call :ColorText 19 "----------------------------------------------------------------" 
    echo.
)
goto :eof

:ColorText
<nul set /p ".=%DEL%" > "%~2"
REM echo "%~2"
findstr /v /a:%1 /R "^$" "%~2" nul
del "%~2"

