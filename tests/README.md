# Testing

1. Install the packages required for development and testing:

```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
```

2. Run the tests:

```bash
nosetests
```

To see test coverage, run the following and then open `./htmlcov/index.html` in your browser:

```bash
nosetests --with-coverage --cover-branches --cover-package=timber tests
coverage html --include='timber*'
```