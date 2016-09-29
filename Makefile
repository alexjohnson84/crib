
test:
	python gameplay/tests.py
testapp:
	python app/tests.py

generate:
	seq 1 | xargs -Iz python models/generate_data.py True
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
	make clean
	make generate
	make model_cv
	make model

play:
	python app/app.py

build_config:
	rm config.py
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
	make install
	make create_database
	make build

generate_graphs:
	python graphs/generate_graphs.py
