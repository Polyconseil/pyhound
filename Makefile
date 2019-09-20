.PHONY: clean docs test

clean:
	rm -fr build/
	rm -fr dist/
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '*~' -delete

update:
	pip install -r requirements_dev.txt
	pip install -e .

quality: clean
	python setup.py sdist
	twine check dist/*
	pylint --rcfile=.pylintrc --reports=no --output-format=colorized setup.py tests pyhound

release: clean
	fullrelease

test:
	nose
