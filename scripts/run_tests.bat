@echo OFF
set current=%cd%
set venv="d:\workspace\virtualenvs\ide"
cd "d:\workspace\github\ideuy\ideuy_controls"
call %venv%\Scripts\activate.bat
echo %cd%
call :run "tests\postgis_controls_tests\pgdb.py"
call :run "tests\commons_controls_tests\file.py"
call :run "tests\commons_controls_tests\time.py"
cd %current%
call %venv%\Scripts\deactivate.bat
call :done

:run
echo ">>>>> "%~1
python -m unittest %~1
EXIT /B 0

:done
echo "DONE"
EXIT /B %ERRORLEVEL%