const ROUTES = {
  "/": ["GET"],
  "/health": ["GET"],
  "/history": ["GET"],
  "/reproduce": ["POST"],
  "/minimize": ["POST"],
  "/generate-test": ["POST"],
};

const CORS_RESPONSE_HEADERS = [
  "access-control-allow-origin",
  "access-control-allow-methods",
  "access-control-allow-headers",
  "access-control-max-age",
];

function corsHeaders(origin) {
  const headers = new Headers();
  if (origin) {
    headers.set("Access-Control-Allow-Origin", origin);
    headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    headers.set("Access-Control-Allow-Headers", "Content-Type");
    headers.set("Access-Control-Max-Age", "86400");
    headers.set("Vary", "Origin");
  }
  return headers;
}

function jsonResponse(status, detail, headers) {
  const responseHeaders = new Headers(headers);
  responseHeaders.set("Content-Type", "application/json; charset=utf-8");
  return new Response(JSON.stringify({ detail }), {
    status,
    headers: responseHeaders,
  });
}

export default {
  async fetch(request, env) {
    const requestUrl = new URL(request.url);
    const origin = request.headers.get("Origin");
    const allowedOrigins = new Set(
      (env.ALLOWED_ORIGINS || "")
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean),
    );

    if (origin && !allowedOrigins.has(origin)) {
      return jsonResponse(403, "Origin is not allowed");
    }

    const responseCorsHeaders = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      if (!origin) {
        return jsonResponse(400, "Origin is required for preflight requests");
      }
      return new Response(null, { status: 204, headers: responseCorsHeaders });
    }

    const methods = ROUTES[requestUrl.pathname];
    if (!methods) {
      return jsonResponse(404, "Route not found", responseCorsHeaders);
    }
    if (!methods.includes(request.method)) {
      return jsonResponse(405, "Method not allowed", responseCorsHeaders);
    }

    if (!env.BACKEND_URL || !env.BACKEND_API_KEY) {
      return jsonResponse(503, "Proxy is not configured", responseCorsHeaders);
    }

    let backendOrigin;
    try {
      const backendUrl = new URL(env.BACKEND_URL);
      if (backendUrl.protocol !== "http:" && backendUrl.protocol !== "https:") {
        throw new Error("Unsupported backend protocol");
      }
      backendOrigin = backendUrl.origin;
    } catch {
      return jsonResponse(503, "Proxy backend URL is invalid", responseCorsHeaders);
    }

    const upstreamUrl = new URL(requestUrl.pathname + requestUrl.search, backendOrigin);
    const upstreamHeaders = new Headers();
    for (const name of ["Accept", "Content-Type"]) {
      const value = request.headers.get(name);
      if (value) upstreamHeaders.set(name, value);
    }
    upstreamHeaders.set("X-API-Key", env.BACKEND_API_KEY);

    try {
      const upstreamResponse = await fetch(upstreamUrl, {
        method: request.method,
        headers: upstreamHeaders,
        body: request.method === "POST" ? request.body : undefined,
        redirect: "manual",
      });
      const headers = new Headers(upstreamResponse.headers);
      for (const name of CORS_RESPONSE_HEADERS) headers.delete(name);
      responseCorsHeaders.forEach((value, name) => headers.set(name, value));
      return new Response(upstreamResponse.body, {
        status: upstreamResponse.status,
        statusText: upstreamResponse.statusText,
        headers,
      });
    } catch {
      return jsonResponse(502, "Backend is unavailable", responseCorsHeaders);
    }
  },
};
