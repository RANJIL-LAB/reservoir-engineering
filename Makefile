VENV = venv/bin

.PHONY: run test clean

run:
	$(VENV)/streamlit run app.py

test:
	$(VENV)/pytest test_cases.py -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
