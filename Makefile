PYTHON ?= python3

.PHONY: verify validate test regen quickstart

verify: validate test

validate:
	$(PYTHON) tools/validate_traceability.py

test:
	$(PYTHON) -m pytest -q

regen:
	$(PYTHON) -m pytest -q --force-regen

quickstart:
	$(PYTHON) examples/quickstart_d1.py
