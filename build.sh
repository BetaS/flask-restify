#!env/bin/activate

/bin/bash ./flask_restify/docs/ui/update.sh

rm dist/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload --repository flask-restify dist/*
