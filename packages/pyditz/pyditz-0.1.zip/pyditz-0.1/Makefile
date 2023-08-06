# Makefile for python module.

SETUP = python setup.py

SRC_FORMATS = gztar,zip
BIN_FORMATS = wininst

.DEFAULT:;	@ $(SETUP) $@
.PHONY:		build dist

all:		build
dist:		sdist
tags:;		find . -name '*.py' | xargs etags

build:;		@ $(SETUP) $@
sdist:;		@ $(SETUP) $@ --formats=$(SRC_FORMATS)
bdist:;		@ $(SETUP) $@ --formats=$(BIN_FORMATS)
help:;		@ $(SETUP) --help
commands:;	@ $(SETUP) --help-commands

clean:;		rm -rf MANIFEST PKG-INFO build dist *.egg-info
