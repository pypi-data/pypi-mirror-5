init:
	pip install -r requirements.txt

test:
	py.test

logintest:
	python test/interactive/login.py

docs:
	$(MAKE) -C docs html

viewdocs:
	cd docs/_build/html; open http://127.0.0.1:8000/; python -m SimpleHTTPServer

dist: test clean
	python setup.py sdist

release: test clean
	python setup.py sdist upload

clean:
	rm -rf webalerts.egg-info
	rm -rf build
	rm -rf dist
	rm -rf docs/_build
	find . -name '.DS_Store' -exec rm -f {} \;
	find . -name '*.sw?' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '__pycache__' -type d -depth -exec rm -rf {} \;

lint:
	pylint webalerts

.PHONY: init test logintest docs viewdocs dist release clean lint
