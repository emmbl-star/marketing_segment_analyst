default: pytest

pytest:
	@python -m pytest -q

install_requirements:
	@pip install -r requirements.txt

install_dev_requirements:
	@pip install -r requirements-dev.txt

streamlit:
	-@streamlit run app.py

clean:
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} +
