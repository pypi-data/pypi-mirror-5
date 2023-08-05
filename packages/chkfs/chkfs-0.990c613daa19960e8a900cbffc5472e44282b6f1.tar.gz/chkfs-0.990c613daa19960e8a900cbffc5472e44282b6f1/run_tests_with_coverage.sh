#!/bin/bash

coverage run --branch ./test_chkfs.py --verbose
TEST_RESULT=$?

set -e
coverage html
python -c 'import webbrowser; webbrowser.open("./htmlcov/chkfs.html")'

exit $TEST_RESULT
