
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

build:
	make clean
	make generate

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
