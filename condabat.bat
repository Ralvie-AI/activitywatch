@echo off
:: Use 'call' to ensure the script continues after the conda command finishes
call conda remove --name myenv --all -y
call conda clean --all -y
call conda create -n myenv python=3.11.15 -y

:: You must 'call' activate to change the environment context for the rest of the script
call conda activate myenv



:: Standard pip installs
pip install -r scripts/requirements/requirements.txt


make package
@REM pause



@REM conda remove --name myenv --all && conda create -n myenv python=3.11 && conda activate myenv

@REM download python anaconda there
@REM https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Windows-x86_64.exe
@REM python pyinstxtractor.py dist/hello.exe
