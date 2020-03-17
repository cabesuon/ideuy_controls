@echo OFF
call :run "tests\imagery_controls_tests\raster_test.py"
call :run "tests\imagery_controls_tests\results_test.py"
call :run "tests\commons_controls_tests\file_test.py"
call :run "tests\commons_controls_tests\time_test.py"
call :run "tests\postgis_controls_tests\pgdb_test.py"
call :done

:run
python -m unittest %~1
EXIT /B 0

:done
EXIT /B %ERRORLEVEL%
