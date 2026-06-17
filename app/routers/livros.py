from typing import Optional

import psycopg
from fastapi import APIRouter, HTTPException, Query

from app.database import get_cursor, row_to_dict, rows_to_list
from app.errors import pg_error
from app.schemas import LivroCreate, LivroUpdate

router = APIRouter(prefix="/api/livros", tags=["livros"])


@router.get("")
def listar_livros(busca: Optional[str] = Query(None)):
    with get_cursor() as (_, cur):
        if busca:
            cur.execute(
                """
                SELECT l.id_livro, l.titulo, l.resumo, l.ano_publicacao,
                       l.id_categoria, c.nome AS categoria
                FROM livro l
                JOIN categoria c ON c.id_categoria = l.id_categoria
                WHERE l.titulo ILIKE %s
                ORDER BY l.titulo
                """,
                (f"%{busca}%",),
            )
        else:
            cur.execute(
                """
                SELECT l.id_livro, l.titulo, l.resumo, l.ano_publicacao,
                       l.id_categoria, c.nome AS categoria
                FROM livro l
                JOIN categoria c ON c.id_categoria = l.id_categoria
                ORDER BY l.titulo
                """
            )
        return rows_to_list(cur.fetchall())


@router.get("/{id_livro}")
def obter_livro(id_livro: int):
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT l.id_livro, l.titulo, l.resumo, l.ano_publicacao,
                   l.id_categoria, c.nome AS categoria
            FROM livro l
            JOIN categoria c ON c.id_categoria = l.id_categoria
            WHERE l.id_livro = %s
            """,
            (id_livro,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Livro nao encontrado")
        return row_to_dict(row)


@router.post("", status_code=201)
def criar_livro(body: LivroCreate):
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO livro (titulo, resumo, ano_publicacao, id_categoria)
                VALUES (%s, %s, %s, %s)
                RETURNING id_livro
                """,
                (body.titulo, body.resumo, body.ano_publicacao, body.id_categoria),
            )
            new_id = cur.fetchone()["id_livro"]
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_livro(new_id)


@router.put("/{id_livro}")
def atualizar_livro(id_livro: int, body: LivroUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    sets = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [id_livro]
    try:
        with get_cursor() as (_, cur):
            cur.execute(f"UPDATE livro SET {sets} WHERE id_livro = %s RETURNING id_livro", values)
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Livro nao encontrado")
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_livro(id_livro)


@router.delete("/{id_livro}", status_code=204)
def remover_livro(id_livro: int):
    try:
        with get_cursor() as (_, cur):
            cur.execute("DELETE FROM livro WHERE id_livro = %s RETURNING id_livro", (id_livro,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Livro nao encontrado")
    except psycopg.Error as exc:
        raise pg_error(exc)
