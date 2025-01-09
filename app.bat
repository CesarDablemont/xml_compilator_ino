@echo off

REM Exécution du script Python
echo Execution du script Python...
python .\python\main.py
IF %ERRORLEVEL% NEQ 0 (
    echo Erreur pendant l'execution du script Python.
    pause
    exit /b %ERRORLEVEL%
)
echo Script Python execute avec succes !
echo.

REM Compilation
echo Compilation du code ino...
.\arduino-cli_1.1.1_Windows_64bit\arduino-cli.exe compile --fqbn esp32:esp32:lolin_s2_mini ".\ardunio"
IF %ERRORLEVEL% NEQ 0 (
    echo Erreur pendant la compilation.
    pause
    exit /b %ERRORLEVEL%
)
echo Code compile avec succes !
echo.

REM Téléversement
echo Televersement du code ino...
.\arduino-cli_1.1.1_Windows_64bit\arduino-cli.exe upload --fqbn esp32:esp32:lolin_s2_mini -p COM4 ".\ardunio"
IF %ERRORLEVEL% NEQ 0 (
    echo Erreur pendant le televersement.
    pause
    exit /b %ERRORLEVEL%
)

echo Code televerse avec succes !
echo.
pause
