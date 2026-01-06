#!/bin/bash
echo "alias pip-scan='python3 $(pwd)/pip_scan.py'" >> ~/.bashrc
source ~/.bashrc
echo "Алиас 'pip-scan' создан! Используйте его вместо pip."