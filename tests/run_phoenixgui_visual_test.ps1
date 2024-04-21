cd ..
python setup.py bdist_wheel
pip uninstall PhoenixGUI
pip install dist/PhoenixGUI-0.1.0-py3-none-any.whl
cd tests
python run_frame.py
