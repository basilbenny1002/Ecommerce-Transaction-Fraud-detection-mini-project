from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.database_routes import router as database_route

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

app.include_router(database_route)
# @app.exception_handler(Exception)
# async def validation_exception_handler(request: Request, exc: Exception):
#     print("Exception:", exc)
#     return JSONResponse(
#         status_code=500,
#         content={"detail": str(exc)},
#     )



@app.get("/")
async def root():
    return {"message": "Server up and running"}

