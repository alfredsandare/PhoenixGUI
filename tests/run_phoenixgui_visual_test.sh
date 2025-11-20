#!/bin/bash
cd ..
bash build.sh
bash install.sh
cd tests
python3 run_frame.py