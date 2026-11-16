from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas import PostMessageRequest, PostMessageResponse
from app.services.posting_service import PostingService

app = FastAPI(
    title="Posting API",
    version="1.0.0"
)

posting_service = PostingService()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        msg = err.get("msg")
        loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        errors.append(f"{loc}: {msg}" if loc else msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation Error",
            "details": errors
        }
    )

@app.get("/")
async def root():
    return {
        "status": "ok"
    }

@app.post(
    "/posting",
    response_model=PostMessageResponse,
    status_code=status.HTTP_200_OK
)
async def post_message(payload: PostMessageRequest):
    return await posting_service.publish_all(payload.message)

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
