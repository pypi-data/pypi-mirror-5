#!/bin/sh
#
# this is the script run by the Jenkins server to run the build and tests.  Be
# sure to always run it in its dir, i.e. ./run-tests.sh, otherwise it might
# remove things that you don't want it to.

if [ `dirname $0` != "." ]; then
    echo "only run this script like ./`basename $0`"
    exit
fi

set -e
set -x

if [ -z $WORKSPACE ]; then
    WORKSPACE=`pwd`
fi


#------------------------------------------------------------------------------#
# run local tests
cd $WORKSPACE/tests
./run-tests.sh


#------------------------------------------------------------------------------#
# test install using site packages
rm -rf $WORKSPACE/env
virtualenv --system-site-packages $WORKSPACE/env
. $WORKSPACE/env/bin/activate
pip install -e $WORKSPACE

# run tests in new pip+virtualenv install
. $WORKSPACE/env/bin/activate
keysync=$WORKSPACE/env/bin/keysync $WORKSPACE/tests/run-tests.sh


#------------------------------------------------------------------------------#
# test install using packages from pypi
rm -rf $WORKSPACE/env
virtualenv --no-site-packages $WORKSPACE/env
. $WORKSPACE/env/bin/activate
pip install -e $WORKSPACE

# run tests in new pip+virtualenv install
. $WORKSPACE/env/bin/activate
keysync=$WORKSPACE/env/bin/keysync $WORKSPACE/tests/run-tests.sh


#------------------------------------------------------------------------------#
# run pylint

cd $WORKSPACE
set +e
# disable E1101 until there is a plugin to handle this properly:
#   Module 'sys' has no '_MEIPASS' member
# disable F0401 until there is a plugin to handle this properly:
#   keysync-gui:25: [F] Unable to import 'ordereddict'
PYTHONPATH=$WORKSPACE/.pylint-plugins \
    pylint --output-format=parseable --reports=n \
    --disable=E1101,F0401 \
    --load-plugins astng_hashlib \
    otrapps/*.py keysync keysync-gui > $WORKSPACE/pylint.parseable
# only tell jenkins there was an error if we got ERROR or FATAL
[ $(($? & 1)) = "1" ] && exit 1
[ $(($? & 2)) = "2" ] && exit 2
set -e
