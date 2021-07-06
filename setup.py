from setuptools import setup, find_packages

setup(
    name='flask_restify',
    version='0.3.0',
    url='https://github.com/BetaS/flask-restify',
    author="BetaS",
    author_email="thou1999@gmail.com",
    description="Flask + Swagger UI for Restful API",
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        'flask',
        'Flask-SQLAlchemy'
    ],
    include_package_data=True
)