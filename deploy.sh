#!/usr/bin/env bash

python3.6 setup.py sdist

FNAME=dist/`python setup.py --fullname`.tar.gz

cp $FNAME ../barn04-server/lib/flask_restify.tar.gz
cp $FNAME ../sharekim-server/lib/flask_restify.tar.gz
cp $FNAME ../nazipsa-lab-server/lib/flask_restify.tar.gz