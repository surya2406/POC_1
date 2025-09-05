import json
from typing import Iterator
from fastapi.responses import StreamingResponse

def sse_response(generator: Iterator[dict]) -> StreamingResponse:
    def _iter():
        for payload in generator:
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    return StreamingResponse(_iter(), media_type="text/event-stream")
