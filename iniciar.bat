@echo off
setlocal

rem Always run from the folder that contains this script.
cd /d "%~dp0"

echo Iniciando o ambiente virtual...
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Não foi encontrado um ambiente virtual em .venv.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: Não foi possível ativar o ambiente virtual.
    timeout /t 5 /nobreak >nul
    exit /b 1
)

cls 

echo Ambiente virtual pronto. Aguarde...
timeout /t 2 /nobreak >nul

echo Iniciando o download...
echo .
python "download_post.py"
set "SCRIPT_EXIT_CODE=%ERRORLEVEL%"

@echo off
cls

echo Encerrando o ambiente virtual...
call deactivate

if not "%SCRIPT_EXIT_CODE%"=="0" (
    echo download_post.py finished with error code %SCRIPT_EXIT_CODE%.
    timeout /t 5 /nobreak >nul
)

endlocal & exit /b %SCRIPT_EXIT_CODE%
