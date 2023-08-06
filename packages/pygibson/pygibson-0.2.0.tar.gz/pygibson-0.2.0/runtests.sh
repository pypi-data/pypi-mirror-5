#!/bin/sh

die() {
    echo "$1";
    exit 1;
}

usage() {
    echo "$0 [--build|-b] [--debug|-d] [--logs|-l] [test_extension.TestUnixSockets]"
    exit 1;
}

BUILD_DIR=`python <<EOT
import sys
from distutils import util
v = sys.version[:3]
p = util.get_platform()
build_dir = "build/lib.%s-%s" % (p, v)
sys.stdout.write(build_dir)
EOT`

LOGS="/dev/null"
BUILD=""
DEBUG=""

TEMP=`getopt -o bdlh --long build,debug,logs,help -n 'runtests.sh' -- "$@"`

if [ $? != 0 ] ; then usage ; fi

eval set -- "$TEMP"

while true; do
    case "$1" in
        -b|--build) BUILD="1"; shift;;
        -d|--debug) DEBUG="--pygibson-debug"; shift;;
        -l|--logs)  LOGS="/tmp/pygibson.test.log"; shift;;
        -h|--help)  usage; shift;;
        --) shift; break;;
        *) usage;;
    esac
done;

if [ -n "$BUILD" ]; then
    python setup.py clean --all;
    python setup.py build $DEBUG || die "Build failed";
    export PYTHONPATH=$BUILD_DIR:$PYTHONPATH;
fi;

if [ "$LOGS" != "/dev/null" ]; then echo "Logs can be found at $LOGS"; fi;

python -m tests.run $* > $LOGS

if [ $? != 0 ]; then die "Tests failed"; fi;

