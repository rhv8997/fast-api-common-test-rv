import re
import traceback
from time import perf_counter_ns
from uuid import uuid4

from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from uuid6 import uuid7


class LoggingMiddleware(BaseHTTPMiddleware):
    EXCLUDED_PATTERN_STRINGS = [r"/health$"]
    EXCLUDED_PATTERNS = [re.compile(pattern) for pattern in EXCLUDED_PATTERN_STRINGS]

    async def dispatch(self, request: Request, call_next):
        log_enabled = True
        for pattern in self.EXCLUDED_PATTERNS:
            if pattern.search(str(request.url)):
                log_enabled = False
        tic = perf_counter_ns()
        request_id = str(uuid7())  # todo: make this otel / aws xray aware
        with logger.contextualize(request_id=request_id):
            if log_enabled:
                logger.info("started processing request")
            try:
                response = await call_next(request)
            except Exception as _:
                logger.error(traceback.format_exc())
                response = JSONResponse(content={}, status_code=500)
            finally:
                toc = perf_counter_ns()
                duration = (toc - tic) / 1000000
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time"] = request_id
                if log_enabled:
                    logger.info("finished processing request")
                    logger.info(
                        f"method={request.method} url={request.url} status_code={response.status_code} duration={duration} request_id={request_id}"
                    )
            return response
