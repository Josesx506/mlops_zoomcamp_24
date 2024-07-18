setup:
	sh scripts/setup.sh

integration_test: setup
	sh scripts/integration_test.sh

train:
	sh scripts/train.sh

clean:
	cd backend/ && poetry run python pkg/clean.py