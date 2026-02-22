.PHONY: dev frontend backend install

dev:
	@echo "Starting CrowdTest (frontend + backend)..."
	@trap 'kill 0' EXIT; \
	cd backend && uvicorn app.main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait

frontend:
	cd frontend && npm run dev

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

install:
	cd frontend && npm install
	cd backend && pip install -r requirements.txt
