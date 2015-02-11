@echo off
rem Copyright 2013 Google Inc. All Rights Reserved.

echo %CmdCmdLine% | find /i "%~0" >nul
SET INTERACTIVE=%ERRORLEVEL%

echo Welcome to the Google Cloud SDK!

SETLOCAL

IF "%CLOUDSDK_PYTHON%"=="" (
  FOR %%i in (python.exe) do (SET CLOUDSDK_PYTHON=%%~$PATH:i)
)
IF "%CLOUDSDK_PYTHON%"=="" (
  echo.
  echo To use the Google Cloud SDK, you must have Python installed and on your PATH.
  echo As an alternative, you may also set the CLOUDSDK_PYTHON environment variable
  echo to the location of your Python executable.
  %COMSPEC% /C exit 1
) ELSE (
  %COMSPEC% /C "%CLOUDSDK_PYTHON% "%~dp0bin\bootstrapping\install.py" %*"
)

IF _%INTERACTIVE%_==_0_ (
  IF _%CLOUDSDK_CORE_DISABLE_PROMPTS%_==__ (
    echo Google Cloud SDK installer will now exit.
    PAUSE
  )
)

ENDLOCAL

%COMSPEC% /C exit %ERRORLEVEL%
