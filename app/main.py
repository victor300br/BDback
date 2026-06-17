from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import categorias, emprestimos, health, livros, relatorios, usuarios

app = FastAPI(
    title="BiblioCampusUECE",
    description="API REST do Projeto Final — Biblioteca Universitaria (PostgreSQL TP3)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(categorias.router)
app.include_router(livros.router)
app.include_router(usuarios.router)
app.include_router(emprestimos.router)
app.include_router(relatorios.router)
