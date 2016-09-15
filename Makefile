.PHONY: test
test:
	python gameplay/tests.py

generate:
	python models/generate_data.py
