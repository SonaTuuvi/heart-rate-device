@echo off
setlocal EnableDelayedExpansion

:: Set your serial port (adjust if needed)
set PORT=COM3

:: List of folders to install
set FOLDERS=app core cloud history ui lib

:: Loop through each folder
for %%F in (%FOLDERS%) do (
    echo Installing folder: %%F
    mpremote connect %PORT% fs mkdir :/%%F 2>nul

    :: Copy .py files
    for %%f in (%%F\*.py) do (
        if exist "%%f" (
            echo   Uploading %%f
            mpremote connect %PORT% fs cp "%%f" ":/%%F/"
        )
    )

    :: Copy .json files
    for %%f in (%%F\*.json) do (
        if exist "%%f" (
            echo   Uploading %%f
            mpremote connect %PORT% fs cp "%%f" ":/%%F/"
        )
    )

    :: Copy .mpy files
    for %%f in (%%F\*.mpy) do (
        if exist "%%f" (
            echo   Uploading %%f
            mpremote connect %PORT% fs cp "%%f" ":/%%F/"
        )
    )

    :: Check for nested folders (like lib\umqtt)
    for /d %%D in (%%F\*) do (
        echo   Creating subfolder: %%F/%%~nxD
        mpremote connect %PORT% fs mkdir :/%%F/%%~nxD 2>nul

        for %%f in (%%D\*) do (
            echo     Uploading %%f
            mpremote connect %PORT% fs cp "%%f" ":/%%F/%%~nxD/"
        )
    )
)

:: Upload main.py
if exist "main.py" (
    echo Uploading main.py
    mpremote connect %PORT% fs cp "main.py" ":/"
)

echo Installation complete.
echo Running main.py...
mpremote connect %PORT% run main.py

pause
