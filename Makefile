install:
	pip install .

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf build
	rm -rf dist
	rm -rf simple-screen.egg-info
