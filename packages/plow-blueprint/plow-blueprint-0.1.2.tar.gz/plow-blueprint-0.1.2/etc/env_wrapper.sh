#!/bin/bash
#
# Wraps the execution of plow tasks on the render farm.
#
source ${BLUEPRINT_SCRIPTS_PATH}/prerun.sh

# Set a temporary directory for the process.
export PLOW_TASK_TEMPDIR="${TMPDIR}/${PLOW_JOB_NAME}/${PLOW_TASK_NAME}"
export TMPDIR="$PLOW_TASK_TMPDIR"

# Make sure it exists
mkdir -p $PLOW_TASK_TEMPDIR

eval $@
ret_code=$?

# Clean up the temp directory
rm -f ${PLOW_TASK_TEMPDIR}/*

source ${BLUEPRINT_SCRIPTS_PATH}/postrun.sh

if [ $ret_code != 0 ]; then
  exit $ret_code
fi
