import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-widget_list",
    version = "0.0.1",
    author = "David Renne",
    author_email = "david_renne -at- yahoo com",
    description = ("An Advanced and flexible ajax data grid"),
    license = "BSD",
    keywords = "pagination",
    url = "http://packages.python.org/widget_list",
    packages=['widget_list'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Database :: Front-Ends",
        "License :: OSI Approved :: BSD License",
    ],
)