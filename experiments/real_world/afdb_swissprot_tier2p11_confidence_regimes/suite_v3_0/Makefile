# AFDB Non‑LLM Small‑Models Suite (v3.1)
#
# Usage:
#   make smoke          # run smoke checks for all subcases
#   make pae            # run PAE subcase smoke
#   make msa            # run MSA subcase smoke
#   make dual           # run dual-oracle subcase smoke
#   make clean          # remove smoke outputs + synthetic metrics
#   make help

SHELL := /usr/bin/env bash

CASE_DIR := $(abspath $(CURDIR)/..)
SUBCASES := $(CASE_DIR)/subcases

.PHONY: help smoke pae msa dual clean

help:
	@echo "AFDB Non‑LLM Small‑Models Suite (v3.1)"
	@echo ""
	@echo "Targets:"
	@echo "  make smoke   - run smoke checks for all subcases (equivalent to bash suite_ci_check.sh)"
	@echo "  make pae     - run PAE proxy alarm smoke"
	@echo "  make msa     - run MSA deficit proxy smoke"
	@echo "  make dual    - run dual-oracle active acquisition smoke"
	@echo "  make clean   - remove out_smoke/ and synthetic metrics artifacts"
	@echo ""
	@echo "Env install (single env):"
	@echo "  pip install -r requirements.all.txt"

smoke:
	@bash suite_ci_check.sh

pae:
	@cd $(SUBCASES)/pae_proxy_alarm && bash scripts/ci_check.sh

msa:
	@cd $(SUBCASES)/msa_deficit_proxy && bash scripts/ci_check.sh

dual:
	@cd $(SUBCASES)/dual_oracle_active_acquisition && bash scripts/ci_check.sh

clean:
	@echo "Cleaning smoke outputs..."
	@rm -rf $(SUBCASES)/pae_proxy_alarm/out_smoke $(SUBCASES)/pae_proxy_alarm/data/synthetic_metrics.csv || true
	@rm -rf $(SUBCASES)/msa_deficit_proxy/out_smoke $(SUBCASES)/msa_deficit_proxy/data/synthetic_metrics.csv || true
	@rm -rf $(SUBCASES)/dual_oracle_active_acquisition/out_smoke $(SUBCASES)/dual_oracle_active_acquisition/data/synthetic_metrics.csv || true
	@echo "Done."
