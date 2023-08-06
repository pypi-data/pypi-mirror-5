set PATH=d:\qwerty\freelance\Pyinstaller\pyinstaller-1.5.1\
set OUTDIR=exe
set PROGRAM=pyNanoCMS
mkdir %OUTDIR%
%PATH%Configure.py
%PATH%Makespec.py -F -w -X -o %OUTDIR% %PROGRAM%.py --icon=peach.ico
REM -n name
REM --icon=<FILE.ICO>
REM -w no console
REM --icon=peach.ico
REM --icon=favicon.ico
%PATH%Build.py %OUTDIR%\%PROGRAM%.spec
copy %OUTDIR%\dist\%PROGRAM%.exe .
del logdict*.log
del *.pyc
rmdir /S /Q %OUTDIR%
pause