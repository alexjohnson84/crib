
test:
	python gameplay/tests.py
testapp:
	python app/tests.py

generate:
	# Generate fake data and store them as log files.  On every move, each
	# choice is a random choice of legal moves
	seq 100 | xargs -Iz python models/generate_data.py True
	python models/parse_logs.py True

generate_modeled:
	python models/generate_data.py
	python models/parse_logs.py

clean:
	rm -rf data/logs*
	rm -f data/*base_table.txt
	mkdir data/logs
	mkdir data/logs/random
	mkdir data/logs/model
	find . -name \*.pyc -delete

model:
	mkdir -p models/hand_model
	mkdir -p models/peg_model
	python models/generate_hand_models.py
	python models/generate_peg_models.py

model_cv:
	rm -f graphs/*
	python models/generate_peg_models.py True
	python models/generate_hand_models.py True

build:
	mkdir data/
	make clean
	make generate
	make model_cv
	make model
	make generate_modeled

play:
	python app/app.py

build_config:
	# Builds new configuration file for flask.  Copies database information from
	# config_base and creates a random hexidecimal code for the secretkey
	rm -f config.py
	cp config_base.py config.py
	echo -n "SECRET_KEY = '" >> config.py
	hexdump -n 16 -v -e '/1 "%02X"' /dev/urandom >> config.py
	echo "'" >> config.py

install:
	virtualenv cc_virt
	source cc_virt/bin/activate
	pip install -r requirements.txt
	make build_config

full_build:
	pip install -r requirements.txt
	make build

generate_graphs:
	python graphs/generate_graphs.py
