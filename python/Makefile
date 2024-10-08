.PHONY: test run clean

VENV_DIR := venv

test: $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && \
	pip install -r requirements.txt && \
	pytest && \
	deactivate

run: $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && \
	pip install -r requirements.txt && \
	fastapi dev main.py

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

clean:
	rm -rf $(VENV_DIR)