@echo off
REM Traz para o Drive os episodios que ja foram ao ar.
REM
REM Roda NESTA maquina porque o servidor do GitHub nao enxerga o Drive: os episodios
REM 3 e 4 nasceram na nuvem e sumiram do arquivo da casa ate alguem notar.
REM
REM Nao precisa acertar o horario. O script baixa o que falta e ignora o que ja esta la,
REM entao maquina desligada as 8h so adia o arquivamento, nao o perde.

cd /d "C:\Users\adm_legale\Downloads\compasso-podcast"

echo. >> "ops\arquivar.log"
echo ===== %DATE% %TIME% ===== >> "ops\arquivar.log"

git pull --rebase --quiet origin main >> "ops\arquivar.log" 2>&1
python "scripts\arquivar_no_drive.py" >> "ops\arquivar.log" 2>&1

echo (codigo de saida %ERRORLEVEL%) >> "ops\arquivar.log"
