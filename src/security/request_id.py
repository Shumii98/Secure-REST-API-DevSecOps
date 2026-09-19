import uuid

from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Assigns a unique ID to every request, so it can be traced across
    logs and audit events. Honors an incoming X-Request-ID header if
    a client/proxy already set one, otherwise generates a new one.
    """

    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response