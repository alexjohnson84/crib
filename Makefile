.PHONY: test
test:
	python gameplay/tests.py

generate:
	make clean
	python models/generate_data.py
	python models/parse_logs.py
clean:
	rm -f data/*
