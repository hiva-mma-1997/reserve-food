@echo off
cd /d C:\Users\Food reserve\Desktop\reserve-hydro\zwitter
call .venv\Scripts\activate.bat
python -m waitress --host=0.0.0.0 --port=8000 zwitter.wsgi:application