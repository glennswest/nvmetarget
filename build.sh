rm dist/*
python -m build --wheel
pip install dist/* --force-reinstall
