all:
	python app.py
clean:
	rm -rf instance/data.db
	python app.py