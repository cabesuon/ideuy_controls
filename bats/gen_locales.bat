@echo OFF
set pygettext="C:\python\Tools\i18n\pygettext.py"
:: ----------
::
:: controls
::
:: ----------
call :run "controls" "postgis_controls" "main"
call :run "controls" "postgis_controls" "pgdb"
call :run "controls" "imagery_controls" "main"
call :run "controls" "imagery_controls" "raster"
call :run "controls" "imagery_controls" "results"
call :run "controls" "commons_controls" "file"
call :run "controls" "commons_controls" "time"
:: ----------
::
:: tests
::
:: ----------
call :run "tests" "postgis_controls_tests" "pgdb_tests"
call :run "tests" "imagery_controls_tests" "raster_tests"
call :run "tests" "imagery_controls_tests" "results_tests"
call :run "tests" "commons_controls_tests" "file_tests"
call :run "tests" "commons_controls_tests" "time_tests"
call :done

:run
python %pygettext% -d %~1.%~2.%~3 -o locales\\%~1\\%~2\\%~3.pot %~1\\%~2\\%~3.py
EXIT /B 0

:done
EXIT /B %ERRORLEVEL%