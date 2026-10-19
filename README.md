# ReproForge

ReproForge is a small web app for running Python snippets, minimizing example
inputs, and generating pytest regression tests. Run history is stored in MongoDB.

## Run with Docker Compose

From the repository root:

```sh
docker compose up --build
```

Open the frontend at <http://localhost:8080> and the API at
<http://localhost:8001>. Compose starts MongoDB with a persistent `mongodb_data`
volume. To use a different database, set `MONGODB_URI` and optionally
`MONGODB_DB` in the environment (or in a root `.env` file).

## Run locally

Start MongoDB and set `MONGODB_URI` (defaults are only configured by Compose).
Then start the API from the repository root:

```sh
python -m pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

The local frontend defaults to the API at `http://127.0.0.1:8000`. Set
`VITE_API_BASE_URL` before building or starting Vite to use another API URL.

## Checks

```sh
python -m pytest backend/tests -q
cd frontend
npm run lint
npm run build
```
