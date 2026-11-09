import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import worker from "../src/index.js";

const env = {
  BACKEND_URL: "https://backend.example.test",
  BACKEND_API_KEY: "server-only-key",
  ALLOWED_ORIGINS: "https://app.example.test,http://localhost:5173",
};

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
});

test("forwards allowed API requests with the server-side key", async () => {
  let upstreamRequest;
  globalThis.fetch = async (url, init) => {
    upstreamRequest = { url: new URL(url), init };
    return new Response('{"success":true}', {
      headers: { "Content-Type": "application/json" },
    });
  };

  const request = new Request("https://proxy.example.test/reproduce?mode=full", {
    method: "POST",
    headers: {
      Origin: "https://app.example.test",
      "Content-Type": "application/json",
      "X-API-Key": "untrusted-client-key",
      Authorization: "Bearer untrusted-token",
    },
    body: '{"code":"print(1)"}',
  });
  const response = await worker.fetch(request, env);

  assert.equal(upstreamRequest.url.href, "https://backend.example.test/reproduce?mode=full");
  assert.equal(upstreamRequest.init.headers.get("X-API-Key"), "server-only-key");
  assert.equal(upstreamRequest.init.headers.get("Authorization"), null);
  assert.equal(upstreamRequest.init.headers.has("Cookie"), false);
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), "https://app.example.test");
  assert.deepEqual(await response.json(), { success: true });
});

test("answers allowed preflight without contacting the backend", async () => {
  globalThis.fetch = async () => {
    assert.fail("preflight must not call the backend");
  };

  const response = await worker.fetch(
    new Request("https://proxy.example.test/history", {
      method: "OPTIONS",
      headers: { Origin: "https://app.example.test" },
    }),
    env,
  );

  assert.equal(response.status, 204);
  assert.equal(response.headers.get("Access-Control-Allow-Methods"), "GET, POST, OPTIONS");
  assert.equal(response.headers.get("Access-Control-Allow-Headers"), "Content-Type");
});

test("rejects origins outside the configured allowlist", async () => {
  globalThis.fetch = async () => {
    assert.fail("disallowed origins must not contact the backend");
  };

  const response = await worker.fetch(
    new Request("https://proxy.example.test/history", {
      headers: { Origin: "https://other.example.test" },
    }),
    env,
  );

  assert.equal(response.status, 403);
  assert.equal(response.headers.get("Access-Control-Allow-Origin"), null);
});

test("limits proxying to known routes and methods", async () => {
  globalThis.fetch = async () => {
    assert.fail("unknown routes and methods must not contact the backend");
  };

  const unknownRoute = await worker.fetch(
    new Request("https://proxy.example.test/admin", {
      headers: { Origin: "https://app.example.test" },
    }),
    env,
  );
  const wrongMethod = await worker.fetch(
    new Request("https://proxy.example.test/reproduce", {
      headers: { Origin: "https://app.example.test" },
    }),
    env,
  );

  assert.equal(unknownRoute.status, 404);
  assert.equal(wrongMethod.status, 405);
});

test("fails closed when the backend key is not configured", async () => {
  globalThis.fetch = async () => {
    assert.fail("an unconfigured proxy must not contact the backend");
  };

  const response = await worker.fetch(
    new Request("https://proxy.example.test/history", {
      headers: { Origin: "https://app.example.test" },
    }),
    { ...env, BACKEND_API_KEY: "" },
  );

  assert.equal(response.status, 503);
});
