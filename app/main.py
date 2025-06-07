from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routes.database_routes import router as database_route
from app.routes.predict_routes import router as predict_route


app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(database_route)
app.include_router(predict_route)

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


@app.get("/")
async def root():
    return {"message": "Server up and running"}
