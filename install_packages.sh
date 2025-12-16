#!/usr/bin/env bash
set -e

# garante que estamos no venv
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "Ative o virtualenv antes: source venv/bin/activate"
  exit 1
fi

python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

python -m pip install --upgrade numpy
python -m pip install --upgrade pandas
python -m pip install --upgrade jupyterlab
python -m pip install --upgrade pprintpp
python -m pip install --upgrade xlrd
python -m pip install --upgrade openpyxl
python -m pip install --upgrade xlsxwriter
python -m pip install --upgrade sqlalchemy
python -m pip install --upgrade flet
