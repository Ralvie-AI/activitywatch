@echo off
:: Use 'call' to ensure the script continues after the conda command finishes
call conda remove --name myenv --all -y
call conda clean --all -y
call conda create -n myenv python=3.11.15 -y

:: You must 'call' activate to change the environment context for the rest of the script
call conda activate myenv



:: Standard pip installs
pip install poetry==1.8.4 poetry-core==1.9.1 poetry-plugin-export==1.8.0 pyqtdarktheme PySide6==6.9.1 PySide6_Addons==6.9.1 PySide6_Essentials==6.9.1 Cython==3.2.8


make package
@REM pause



@REM conda remove --name myenv --all && conda create -n myenv python=3.11 && conda activate myenv

@REM download python anaconda there
@REM https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Windows-x86_64.exe
@REM python pyinstxtractor.py dist/hello.exe
