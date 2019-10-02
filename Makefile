PYTHON_MODULE_DIR=./
PYTHON_MODULE=autorizator
PYTHON_BINARIES=
PYTHON_MODULE_FILES=$(shell find $(PYTHON_MODULE) -type f -name '*.py')

TESTS_DIR=tests
TESTS_UNIT_DIR=$(TESTS_DIR)/unit
TESTS_UNIT_FILES=$(shell find $(TESTS_UNIT_DIR) -type f -name '*.py')

PYTHON_BIN=pipenv run python

PYTEST_MODULE=pytest
PYTEST_PARAMS=$(TESTS_UNIT_DIR) -vvv

COVERAGE_BIN=pipenv run coverage
COVERAGE_CMD_RUN=$(COVERAGE_BIN) run
COVERAGE_CMD_REPORT=$(COVERAGE_BIN) report
COVERAGE_REPORT_ARGS=--skip-covered
COVERAGE_CMD_HTML=$(COVERAGE_BIN) html
COVERAGE_HTML_DIR=.htmlcov
COVERAGE_HTML_ARGS=$(COVERAGE_REPORT_ARGS) -d $(COVERAGE_HTML_DIR)
COVERAGE_REPORT_FILES=$(PYTHON_BINARIES) $(PYTHON_MODULE_FILES)

PYLINT_BIN ?= pipenv run pylint
PYLINT_RC_FILE=.pylintrc
PYLINT_PARAMS ?= --output-format=parseable --reports=no

FLAKE8_BIN ?= pipenv run flake8
FLAKE8_CONFIG_FILE=.flake8
FLAKE8_PARAMS=

MYPY_BIN ?= pipenv run mypy
MYPY_PARAMS=

.PHONY: lint
lint:
	$(PYLINT_BIN) --rcfile=$(PYLINT_RC_FILE) $(PYLINT_PARAMS) $(PYTHON_MODULE)
	$(FLAKE8_BIN) --config=$(FLAKE8_CONFIG_FILE) $(FLAKE8_PARAMS) $(PYTHON_MODULE)
	$(MYPY_BIN) $(MYPY_PARAMS) $(PYTHON_MODULE)

.PHONY: test
test:
	$(PYTHON_BIN) -m $(PYTEST_MODULE) $(PYTEST_PARAMS)

.coverage: $(COVERAGE_REPORT_FILES) $(TESTS_UNIT_FILES)
	$(MAKE) test PYTEST_PARAMS="$(PYTEST_PARAMS) --cov-report= --cov=autorizator"

.PHONY: report-coverage
report-coverage: .coverage
	@ $(COVERAGE_CMD_REPORT) $(COVERAGE_REPORT_ARGS) $(COVERAGE_REPORT_FILES)

.PHONY: report-coverage-html
report-coverage-html: .coverage
	@ echo "Generating HTML code coverage report ..."
	@ $(COVERAGE_CMD_HTML) $(COVERAGE_HTML_ARGS) $(COVERAGE_REPORT_FILES)
	@ echo "Report: file://$$(pwd)/$(COVERAGE_HTML_DIR)/index.html"

.PHONY: system-test
system-test:
	export PATH=$$(pwd):$$PATH; cd tests/system && ./run.sh

.PHONY: check
check: lint report-coverage

.PHONY: clean
clean:
	rm -rf .coverage $(COVERAGE_HTML_DIR)
