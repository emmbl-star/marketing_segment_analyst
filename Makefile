default: pytest

pytest:
	echo "no tests"

install_requirements:
	@pip install -r requirements.txt

streamlit:
	-@streamlit run app.py

clean:
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} +
