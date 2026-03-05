from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine
from . import models

from .routers import auth
from .routers import transactions
from .routers import analytics
from .routers import budgets

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SpendIQ API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    return {"message": "SpendIQ backend is running"}


@app.get("/login-page")
def serve_login_page():
    return FileResponse("app/static/login.html")


@app.get("/register-page")
def serve_register_page():
    return FileResponse("app/static/register.html")


@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("app/static/dashboard.html")


app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(budgets.router)