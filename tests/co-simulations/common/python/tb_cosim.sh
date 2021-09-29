#!/bin/bash
set -e
ENTITY=$1
DIR="/tmp/PyWbFBD/"
LOG_FILE="$ENTITY.log"
PYTHON_FILE="../../../tests/co-simulations/$ENTITY/python/tb_cosim.py"

export PYTHONPATH="$PYTHONPATH:$PWD/../../../tests/co-simulations/common/python/"

mkdir -p $DIR
if [ ! -f "$PYTHON_FILE" ]; then
	>&2 echo "$PYTHON_FILE not found"
	exit 1
fi
python3 $PYTHON_FILE > "$DIR$LOG_FILE" 2>&1 &
