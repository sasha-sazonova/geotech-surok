PYTHON ?= python3

.PHONY: verify validate test regen quickstart scenario

verify: validate test

validate:
	$(PYTHON) workspace-geotech_surok/tools/validate_traceability.py

test:
	$(PYTHON) -m pytest -q

regen:
	$(PYTHON) -m pytest -q --force-regen

quickstart:
	$(PYTHON) workspace-geotech_surok/examples/quickstart_d1.py

SCENARIO ?= scenarios/d1-foundation.yaml

scenario:
	$(PYTHON) workspace-geotech_surok/tools/run_scenario.py $(SCENARIO)
