@echo OFF
set pygettext="C:\python\Tools\i18n\pygettext.py"
:: ----------
::
:: controls
::
:: ----------
call :run "controls" "postgis_controls" "main"
call :run "controls" "postgis_controls" "pgdb"
call :run "controls" "commons_controls" "file"
call :run "controls" "commons_controls" "time"
:: ----------
::
:: tests
::
:: ----------
REM call :run "tests" "postgis_controls" "pgdb"
REM call :run "tests" "commons_controls" "file"
REM call :run "tests" "commons_controls" "time"
call :done

:run
python %pygettext% -d %~1.%~2.%~3 -o locales\\%~1\\%~2\\%~3.pot %~1\\%~2\\%~3.py
EXIT /B 0

:done
echo "DONE"
EXIT /B %ERRORLEVEL%