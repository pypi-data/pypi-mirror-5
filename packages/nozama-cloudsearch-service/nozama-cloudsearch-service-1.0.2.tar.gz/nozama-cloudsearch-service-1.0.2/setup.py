# -*- coding: utf-8 -*-
"""
Setuptools script for content-classify-service (content.classify.service)

"""
from setuptools import setup, find_packages

# Get the version from the source or the cached egg version:
import json
import ConfigParser
cp = ConfigParser.ConfigParser()
try:
    cp.read('../eggs_version.ini')
    version = dict(cp.items('default'))['version']
except:
    # inside and egg, read the cache version instead.
    with file("cached_version.json", "r") as fd:
        version = json.loads(fd.read())['egg_version']
else:
    # write out the version so its cached for in egg use:
    with file("cached_version.json", "w") as fd:
        fd.write(json.dumps(dict(egg_version=version)))


Name = 'nozama-cloudsearch-service'
ProjectUrl = ""
Version = version
Author = 'Oisin Mulvihill'
AuthorEmail = 'oisin dot mulvihill a-t  gmail dot com'
Maintainer = 'Oisin Mulvihill'
License = 'BSD'
Summary = (
    'A REST service which implements the Amazon CloudSearch for local testing'
    'purposes. This is *not* intended as a replacement for CloudSearch.'
)
Description = Summary
ShortDescription = Summary

needed = [
    "pytest",
    "evasion-common",
    "decorator",
    "paste",
    "pyramid",
    "pyramid_jinja2",
    "pyramid_beaker",
    "waitress",
]

test_needed = [
]

test_suite = 'nozama.cloudsearch.service.tests'

EagerResources = [
    'nozama',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

# Web Entry points
EntryPoints = """
[paste.app_factory]
    main = nozama.cloudsearch.service:main
"""

setup(
    url=ProjectUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords='web wsgi bfg pylons pyramid',
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    tests_require=test_needed,
    test_suite=test_suite,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points=EntryPoints,
    namespace_packages=['nozama', 'nozama.cloudsearch'],
)
