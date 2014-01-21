#!/usr/bin/env python
from setuptools import setup
from pip.req import parse_requirements

import os.path

install_reqs = parse_requirements("REQUIREMENTS.txt")
reqs = [str(ir.req) for ir in install_reqs]

files = [os.path.join(r,item).replace("flask_dashboards/", "")
         for r, d, f in os.walk("flask_dashboards/static") for item in f]
files += [os.path.join(r,item).replace("flask_dashboards/", "")
          for r, d, f in os.walk("flask_dashboards/templates") for item in f]
files += [os.path.join(r,item).replace("flask_dashboards/", "")
          for r, d, f in os.walk("flask_dashboards/widgets") for item in f]

setup(
    name = "flask-dashboards",
    version = "0.1.0",
    author = "Atomic Labs, LLC",
    author_email = "ben@atomicmgmt.com",
    description = ("Adds easy dashboard endpoints to Flask"),
    license = "MIT",
    url = "http://www.atomicmgmt.com",
    packages=["flask_dashboards"],
    package_data={"flask_dashboards": files},
    install_requires=reqs,
    zip_safe=False
)
