"""
This MWE tests to see if a "loosely" pinned requirement in install_requires can
be strictly pinned.

This does seem to work correctly.
"""
from setuptools import find_packages
from setuptools import setup


if __name__ == "__main__":
    setupkw = {}

    setupkw["install_requires"] = [
        'ubelt>=1.0.0',
    ]
    setupkw["extras_require"] = {
        'strict': ['ubelt==1.0.0'],
    }

    setupkw["name"] = 'setup_req_test'
    setupkw["version"] = '1.0.0'
    setupkw["author"] = "joncrall"
    setupkw["author_email"] = "erotemic@gmail.com"
    setupkw["url"] = 'foobar.com'
    setupkw["description"] = "A mwe"
    setupkw["long_description"] = 'fobar'
    setupkw["long_description_content_type"] = "text/x-rst"
    setupkw["packages"] = find_packages(".")
    setup(**setupkw)
