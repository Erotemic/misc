#!/bin/bash
__doc__="""
SeeAlso:
    ~/code/pyflann_ibeis/pyproject.toml
    ~/code/pyflann_ibeis/dev/docker/make_base_image.py 
"""
cibuildwheel --config-file pyproject.toml --platform linux --arch x86_64
