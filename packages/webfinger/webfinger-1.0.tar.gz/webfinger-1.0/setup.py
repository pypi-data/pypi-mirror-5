from setuptools import setup
from webfinger import __version__

long_description = open('README.rst').read()

setup(name="webfinger",
    version=str(__version__),
    py_modules=["webfinger"],
    description="Simple Python implementation of WebFinger client protocol",
    author="Jeremy Carbaugh",
    author_email="jcarbaugh@gmail.com",
    license='BSD',
    url="http://github.com/jcarbaugh/python-webfinger/",
    long_description=long_description,
    install_requires=["requests"],
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
