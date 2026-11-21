# Dairy Shop POS & Inventory Management System V1

A responsive web application for a small Kenyan dairy shop that sells milk, eggs, yoghurt, ice pops, and other products. The system records real sales, payments, inventory changes, stock purchases, stock counts, operating expenses, and reports.

## Stack

- Frontend: React, TypeScript, Vite, CSS, lucide-react icons
- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Migrations: Alembic
- Tests: pytest

## Business Rules Implemented

- Stock purchases increase inventory but are not treated as operating expenses.
- Operating expenses are recorded separately and reduce net profit.
- Money and quantities use decimal-safe backend calculations.
- Products are deactivated/reactivated instead of permanently deleted.
- Sales reduce inventory only after a sale transaction is created successfully.
- Sales that exceed available inventory are rejected.
- Every inventory change creates a stock movement audit trail.
- Physical stock counts create stock count and stock adjustment records.
- Cost of goods sold uses weighted average cost for V1.
- Products are data-driven; milk, eggs, yoghurt, and ice pops are seed data only.

## Project Structure

```text
backend/
  alembic/               Database migrations
  app/
    api/                 REST routes
    core/                Configuration
    db/                  SQLAlchemy session/base
    models/              Relational models
    schemas/             Pydantic request/response schemas
    services/            Business logic and calculations
    main.py              FastAPI entry point
    seed.py              Optional development seed data
  tests/                 Calculation and acceptance tests
frontend/
  src/
    components/          Shared UI pieces
    features/            Dashboard, POS, products, inventory, expenses, reports, settings
    services/            API client
    types/               TypeScript types
    utils/               Formatting helpers
docker-compose.yml       Local PostgreSQL
.env.example             Example environment variables
```

## Environment

Copy `.env.example` into the files used by each app:

```bash
cp .env.example backend/.env
cp .env.example frontend/.env
```

Important values:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/dairy_shop
VITE_API_URL=http://localhost:8000/api
SECRET_KEY=replace-for-deployment
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Database Setup

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Install backend dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Run migrations:

```bash
alembic upgrade head
```

Load optional seed data:

```bash
python -m app.seed
```

The seed data includes sample categories, expense categories, and sample products: Pasteurised Milk, Eggs, Yoghurt, and Ice Pops. The application logic does not depend on those products existing.

## Running The App

Backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend type/build check:

```bash
cd frontend
npm run build
```

## Production Build

Build the frontend:

```bash
cd frontend
npm run build
```

Run the backend behind a production ASGI server and set production database credentials in environment variables. Do not commit `.env` files or database passwords.

## Deploying Live On Render

This repo includes `render.yaml` for a one-click Render Blueprint deploy:

- `dairy-shop-web`: Vite static frontend
- `dairy-shop-api`: FastAPI backend
- `dairy-shop-db`: PostgreSQL database

Deploy steps:

1. Push this repository to GitHub or GitLab.
2. In Render, choose **New > Blueprint** and select the repository.
3. Render will create the frontend, backend, and database from `render.yaml`.
4. After the first deploy, open the `dairy-shop-web` URL.

The frontend receives the backend host through `VITE_API_HOST` at build time. The backend receives the frontend host through `FRONTEND_HOST` for CORS. Because Render's free web-service plan does not support pre-deploy commands, database migrations run with `alembic upgrade head` when the backend starts.

## API Highlights

- `GET /api/products`
- `POST /api/products`
- `PUT /api/products/{id}`
- `PATCH /api/products/{id}/deactivate`
- `PATCH /api/products/{id}/reactivate`
- `POST /api/sales`
- `GET /api/sales`
- `POST /api/inventory/receive`
- `POST /api/inventory/count`
- `GET /api/inventory/movements`
- `POST /api/expenses`
- `GET /api/reports/daily`
- `GET /api/reports/weekly`
- `GET /api/reports/monthly`
- `GET /api/reports/products`
- `GET /api/reports/milk`
- `GET /api/reports/inventory`
- `GET /api/reports/expenses`
- `GET /api/dashboard`

## Verification Notes

Frontend production build passed with:

```bash
npm run build
```

Python is not exposed in this shell (`python` is missing and `py` has no default interpreter), so backend pytest execution could not be performed locally here. The backend tests are included under `backend/tests/`, including the PDF acceptance flow.

## Known V1 Limits

- No authentication, roles, customer accounts, loyalty, barcode scanning, direct M-Pesa API, SMS, email, online ordering, payroll, or multi-branch support.
- M-Pesa is recorded as a payment method only; no direct payment-provider integration.
- Stock costing uses weighted average cost, documented here as the V1 costing method.
