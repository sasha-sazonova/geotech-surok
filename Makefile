PYTHON ?= python3

.PHONY: verify validate test regen

verify: validate test

validate:
	$(PYTHON) tools/validate_traceability.py

test:
	$(PYTHON) -m pytest -q

regen:
	$(PYTHON) -m pytest -q --force-regen
