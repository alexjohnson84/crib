
test:
	python gameplay/tests.py

generate:
	seq 50 | xargs -Iz python models/generate_data.py
	python models/parse_logs.py

clean:
	rm -rf data/logs*
	rm -f data/*base_table.txt
	mkdir data/logs
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
	make model

play:
	python app/app.py

build_config:
	echo -n "SECRET_KEY = '" > config.py
	hexdump -n 16 -v -e '/1 "%02X"' /dev/urandom >> config.py
	echo "'" >> config.py

install:
	virtualenv cc_virt
	source cc_virt/bin/activate
	pip install -r requirements.txt
	make build_config
