#!/usr/bin/env bash
cd ..
python setup.py install
cd tests
pytest -s
