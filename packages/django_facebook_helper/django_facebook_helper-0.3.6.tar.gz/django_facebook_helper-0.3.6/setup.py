import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_facebook_helper",
    packages=['django_facebook_helper', 'tests'],
    version = "0.3.6",  
    include_package_data = True,
    author = "Samuel Barrado",
    author_email = "samuel.barrado@gmail.com",
    description = ("A Django application for helping in facebook login an managing."),
    license = "BSD",
    keywords = "django facebook",
    url = "http://packages.python.org/django_facebook_helper",
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)