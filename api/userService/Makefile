.PHONY: run format migrate create-migration test

run:
	uvicorn app.main:app --reload

format:
	black .

migrate:
	alembic upgrade head

create-migration:
	alembic revision --autogenerate -m "new change"

test:
	pytest tests/

activate:
	env/Scripts/activate

dependencies:
	pip install -r requirements.txt
	a