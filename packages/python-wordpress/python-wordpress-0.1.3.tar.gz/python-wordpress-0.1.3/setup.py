from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name = "python-wordpress",
    description = "A Python client for the WordPress JSON API plugin",
    long_description = readme,
    version = "0.1.3",
    author = "Chris Amico",
    author_email = "eyeseast@gmail.com",
    py_modules = ['wordpress'],
    url = "https://github.com/eyeseast/python-wordpress",
    license = "MIT",
    install_requires = ['httplib2'],
    classifiers = [
        'Environment :: Web Environment',
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)