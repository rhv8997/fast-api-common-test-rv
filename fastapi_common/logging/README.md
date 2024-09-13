# Basic Logging

Sets up some standard request logging


```python
from fastapi_common.logging import init_logging, LoggingMiddleware

init_logging() # add this as early as possible

app = FastAPI()

app.add_middleware(LoggingMiddleware)
```


