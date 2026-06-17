import psycopg
from fastapi import APIRouter, HTTPException

from app.database import get_cursor, row_to_dict, rows_to_list
from app.errors import pg_error
from app.schemas import CategoriaCreate, CategoriaUpdate

router = APIRouter(prefix="/api/categorias", tags=["categorias"])


@router.get("")
def listar_categorias():
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT id_categoria, nome, descricao, icone, palavras_chave
            FROM categoria ORDER BY nome
            """
        )
        return rows_to_list(cur.fetchall())


@router.get("/{id_categoria}")
def obter_categoria(id_categoria: int):
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT id_categoria, nome, descricao, icone, palavras_chave
            FROM categoria WHERE id_categoria = %s
            """,
            (id_categoria,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Categoria nao encontrada")
        return row_to_dict(row)


@router.post("", status_code=201)
def criar_categoria(body: CategoriaCreate):
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO categoria (nome, descricao, icone, palavras_chave)
                VALUES (%s, %s, %s, %s)
                RETURNING id_categoria
                """,
                (body.nome, body.descricao, body.icone, body.palavras_chave),
            )
            new_id = cur.fetchone()["id_categoria"]
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_categoria(new_id)


@router.put("/{id_categoria}")
def atualizar_categoria(id_categoria: int, body: CategoriaUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    sets = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [id_categoria]
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                f"UPDATE categoria SET {sets} WHERE id_categoria = %s RETURNING id_categoria",
                values,
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Categoria nao encontrada")
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_categoria(id_categoria)


@router.delete("/{id_categoria}", status_code=204)
def remover_categoria(id_categoria: int):
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                "DELETE FROM categoria WHERE id_categoria = %s RETURNING id_categoria",
                (id_categoria,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Categoria nao encontrada")
    except psycopg.Error as exc:
        raise pg_error(exc)
