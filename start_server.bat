@echo off
cd /d F:\Programming\Django\Django_practices_3\zwitter
call .venv\Scripts\activate.bat
python -m waitress --host=0.0.0.0 --port=8000 zwitter.wsgi:application