PYTHON = python
SETUP = setup.py

.PHONY: all

all:
	$(PYTHON) $(SETUP) sdist bdist_wheel
