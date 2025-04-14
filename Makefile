all:
	python3 app.py
clean:
	rm -rf instance/data.db
	python3 app.py