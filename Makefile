setup:
		python3 -m venv ~/.udacity-devops

install:
		pip install --upgrade pip &&\
					pip install -r requirements.txt
server:
		bash ./run_docker.sh
				
test:
		python -m pytest -vv --cov=flask_udacity_final_project tests/test_predictions.py
			python -m pytest --nbval notebook.ipynb

commands:
		bash ./commands.sh

lint:
		#hadolint Dockerfile #uncomment to explore linting Dockerfiles
			pylint --disable=R,C,W1203 app.py

all: install lint test
