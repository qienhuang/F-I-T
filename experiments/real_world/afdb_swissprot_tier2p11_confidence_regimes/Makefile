# Minimal helper commands for this case
.PHONY: run run_b0 run_b1 run_b2 smoke smoke_b0 smoke_b1

run:
	python -m src.run --prereg EST_PREREG.yaml

run_b0:
	python -m src.run --prereg EST_PREREG.yaml --run_id B0_$(shell date -u +%Y%m%d_%H%M%S)

run_b1:
	# Ensure data/pae is populated for selected accessions
	python -m src.run --prereg EST_PREREG.yaml --run_id B1_$(shell date -u +%Y%m%d_%H%M%S)

run_b2:
	# Ensure data/pae and data/msa are populated for selected accessions
	python -m src.run --prereg EST_PREREG.yaml --run_id B2_$(shell date -u +%Y%m%d_%H%M%S)

smoke:
	$(MAKE) smoke_b0
	$(MAKE) smoke_b1

smoke_b0:
	python -m src.run --prereg EST_PREREG.fixture_B0.yaml --run_id fixture_b0

smoke_b1:
	python -m src.run --prereg EST_PREREG.fixture_B1.yaml --run_id fixture_b1
