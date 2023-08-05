#!/bin/bash

export PYTHONPATH=".:$PYTHONPATH"

coverage run ./test_jsonchkstore.py --verbose
TEST_RESULT=$?

set -e
coverage html
python -c 'import webbrowser; webbrowser.open("./htmlcov/jsonchkstore.html")'

exit $TEST_RESULT
