#!/bin/bash

coverage run ./test_chkstore.py --verbose
TEST_RESULT=$?

set -e
coverage html
python -c 'import webbrowser; webbrowser.open("./htmlcov/chkstore.html")'

exit $TEST_RESULT
