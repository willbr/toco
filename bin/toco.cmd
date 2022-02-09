@echo off
set here=%~dp0
set src_dir=%here%..\src\
rem echo %here%
rem echo %src_dir%
python %src_dir%toco.py %1

