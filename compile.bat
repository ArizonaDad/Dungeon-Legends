@echo off
echo Compiling Tabletop Tavern...
echo.

echo Current directory: %cd%
echo.

echo Checking if NVGT exists...
if exist c:\nvgt\nvgt.exe (echo NVGT found!) else (echo NVGT NOT FOUND!)
echo.

echo Checking if client exists...
if exist "%cd%\client\client.nvgt" (echo client.nvgt found!) else (echo client.nvgt NOT FOUND!)
echo.

echo Checking if server exists...
if exist "%cd%\server\Server.nvgt" (echo Server.nvgt found!) else (echo Server.nvgt NOT FOUND!)
echo.

echo Compiling client...
c:\nvgt\nvgt.exe -c "%cd%\client\client.nvgt"
echo Client exit code: %errorlevel%
echo.

echo Compiling server...
c:\nvgt\nvgt.exe -c "%cd%\server\Server.nvgt"
echo Server exit code: %errorlevel%
echo.

echo Done!
pause