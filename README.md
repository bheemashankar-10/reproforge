# ReproForge

ReproForge is a Python bug-reproduction prototype with a React interface, a
FastAPI backend, Docker-based code execution, and MongoDB run history.

## Current behavior

- Reproduce accepts Python source code and runs it once in a Docker container.
	It returns success, stdout, stderr, and the process return code. It does not
	accept a separate input value, repeat runs, classify flaky failures, or parse
	exception details into separate fields.
- Minimize applies ddmin to a list of strings using a predicate that checks for
	caller-supplied required items. It does not rerun the submitted program or
	compare exception signatures, so this is not yet end-to-end failing-input
	minimization.
- Generate test returns pytest source for the submitted code. With an expected
	error string it checks for a nonzero exit and matching stderr; without one it
	checks for a successful exit. It does not use a minimized input or confirm a
	failure before generating the test.
- History stores reproduce, minimize, and generate-test requests and responses
	in MongoDB and provides a view of recent runs.
- The React UI exposes the three workflows and run history. The generated test
	is returned as text; the app does not save it directly to a project.

## API

FastAPI provides `GET /`, `GET /health`, `POST /reproduce`, `POST /minimize`,
`POST /generate-test`, and `GET /history`. Interactive API documentation is
available at the backend's `/docs`. The workflow and history routes require
`X-API-Key`; the root and health routes do not. Request bodies are validated
with Pydantic.

## Execution and security

Submitted code runs in `python:3.12-alpine` with networking disabled, 128 MB
memory, 0.5 CPU, a 64-process limit, a read-only filesystem, a non-root user,
and a bounded execution time and output size. Docker must be installed and
running, and the image must be available locally because execution uses
`--pull never`.

The Cloudflare Worker in `cloudflare-worker/` is the browser-facing API proxy.
It allows only the app's API routes, applies an origin allowlist, and injects
`BACKEND_API_KEY` server-side. Do not put that key in Vite variables or frontend
code. The origin allowlist is a CORS policy, not authentication: a non-browser
client can spoof an `Origin` header and call the public Worker. Add Cloudflare
rate limiting or a real user-authentication mechanism before exposing this to
untrusted traffic. The shared backend key does not identify individual users
or provide per-user quotas.

## Local Development

Copy `.env.example` to `.env.local` and replace the example API key with a
unique local value. `.env.local` is ignored by Git:

```sh
cp .env.example .env.local
```

Start the local stack with its explicit Docker-socket override:

```sh
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up --build
```

Open the frontend at <http://localhost:8080>. The local Worker proxy is at
<http://localhost:8787>, the backend at <http://localhost:8001>, and MongoDB
uses the persistent `mongodb_data` volume. The local override runs the backend
as root and mounts the host Docker socket so it can start sandbox containers.
This grants the backend broad control of the local Docker engine. Use this only
on a trusted development machine; never use this override for a public service.
The base Compose file does not mount the socket. Set `MONGODB_URI` and
`MONGODB_DB` when running the backend outside Compose.

## Deploy the proxy

From `cloudflare-worker/`, authenticate Wrangler and deploy with the backend
URL and exact public frontend origin. Set the API key as a Worker secret using
the same value configured as the backend's `API_KEY`:

```sh
npx wrangler@4 login
npx wrangler@4 secret put BACKEND_API_KEY
npx wrangler@4 deploy --var BACKEND_URL:https://your-backend.example --var ALLOWED_ORIGINS:https://your-frontend.example
```

`ALLOWED_ORIGINS` may contain comma-separated exact origins. Configure the
frontend deployment's `VITE_API_BASE_URL` to the Worker URL and rebuild the
frontend. The backend key stays in the Worker secret and is never sent to the
browser. Deployment requires Cloudflare credentials and has not been run from
this repository checkout.

For local development, create `cloudflare-worker/.dev.vars` with these values
and start `npx wrangler@4 dev` from that directory:

```env
BACKEND_URL=http://127.0.0.1:8000
BACKEND_API_KEY=your-local-api-key
ALLOWED_ORIGINS=http://localhost:5173
```

Start the backend with the same `API_KEY` and the frontend with
`VITE_API_BASE_URL=http://127.0.0.1:8787`.

## Not included yet

There is no Cloudflare deployment automation, Ruff configuration, Render
configuration, or hosted deployment verification in this repository. GitHub
Actions runs the project checks but does not deploy. Regression tests do not yet cover timeouts or hard crashes as
dedicated outcomes. Hosted reproduction still needs a separate isolated runner
service; do not expose the host Docker socket to a public backend as a deployment
shortcut. This remains a demo/portfolio project, not a hardened multi-tenant
execution service.

## Checks

```sh
python -m pytest backend/tests -q
node --test cloudflare-worker/test/worker.test.mjs
docker compose --env-file .env.example -f docker-compose.yml -f docker-compose.local.yml config --quiet
cd frontend
npm run lint
npm run build
```
