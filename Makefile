.PHONY: test clean

VENV_DIR := venv

test: $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && \
	pip install -r requirements.txt && \
	pytest && \
	deactivate

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

clean:
	rm -rf $(VENV_DIR)