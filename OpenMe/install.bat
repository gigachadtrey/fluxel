@echo off
setlocal enabledelayedexpansion

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    echo This script requires administrative privileges.
    echo Please right-click on the script and select "Run as administrator".
    pause
    exit /b
)

:admin
echo Running with administrative privileges.

:: Set up Fluxel
echo Setting up Fluxel...

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v MaxPathLength /t REG_DWORD /d 32768 /f

:: Create a directory for Fluxel
mkdir C:\Fluxel 2>nul

:: Use the fluxel_interpreter.py in the same directory as install.bat
set "interpreter_path=%~dp0interpreter.py"
if not exist "%interpreter_path%" (
    echo fluxel_interpreter.py not found in the same directory as install.bat.
    echo Please make sure fluxel_interpreter.py is in the same folder as this script.
    pause
    exit /b 1
)

:: Copy the interpreter to the Fluxel directory
copy /Y "%interpreter_path%" C:\Fluxel\interpreter.py
if %errorlevel% neq 0 (
    echo Failed to copy the interpreter. Please make sure you have the correct permissions.
    pause
    exit /b 1
)

:: Find Python executable
set "python_exe="
for /d %%D in ("C:\Program Files\WindowsApps\Python*") do (
    if exist "%%D\python.exe" (
        set "python_exe=%%D\python.exe"
        goto :found_python
    )
)

:: If not found in WindowsApps, try to find Python elsewhere
for %%I in (python.exe) do (
    set "python_exe=%%~$PATH:I"
    if not "!python_exe!"=="" goto :found_python
)

:found_python
if "%python_exe%"=="" (
    echo Python executable not found. Please make sure Python is installed.
    pause
    exit /b 1
)

:: Add .flux file association
assoc .flux=FluxelFile
ftype FluxelFile="%python_exe%" C:\Fluxel\interpreter.py "%%1"

:: Add Fluxel to PATH without using PowerShell
for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "current_path=%%B"
setx PATH "C:\Fluxel;%current_path%" /M
if %errorlevel% neq 0 (
    echo Failed to update PATH. You may need to add C:\Fluxel to your PATH manually.
    pause
)

:: Create a batch file to run .flux files
echo @echo off > C:\Fluxel\fluxel.bat
echo "%python_exe%" C:\Fluxel\fluxel_interpreter.py %%* >> C:\Fluxel\fluxel.bat

echo Fluxel has been successfully installed!
echo Python executable found at: %python_exe%
echo.
echo Please restart your command prompt or IDE to use the updated PATH.
echo You can now run Fluxel scripts using: fluxel your_script.flux
pause
