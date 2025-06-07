from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes.database_routes import router as database_route
from app.routes.predict_routes import router as predict_route
from app.routes.api_routes import router as api_route
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from app.routes.api_routes import limiter


def get_api_key_identity(request: Request) -> str:
    # Extract API key from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split("Bearer ")[1].strip()
    return "anonymous"




app = FastAPI()
app.state.limiter = limiter 
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(database_route)
app.include_router(predict_route)
app.include_router(api_route)



@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    # Log the exception for server-side review
    print(f"Global exception handler caught: {exc} for request: {request.url}")
    # import traceback # Uncomment for full traceback
    # print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected server error occurred: {str(exc)}"},
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})


@app.get("/")
async def root():
    return {"message": "Server up and running"}
