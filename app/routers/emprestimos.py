from datetime import date

import psycopg
from fastapi import APIRouter, HTTPException

from app.database import get_cursor, row_to_dict, rows_to_list
from app.errors import pg_error
from app.schemas import EmprestimoCreate, EmprestimoDevolver

router = APIRouter(prefix="/api/emprestimos", tags=["emprestimos"])


@router.get("")
def listar_emprestimos():
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT e.id_usuario, u.nome AS nome_usuario,
                   e.id_livro, l.titulo AS titulo_livro,
                   e.data_emprestimo, e.data_prev_devolucao,
                   e.data_devolucao, e.status, e.observacao
            FROM emprestimo e
            JOIN usuario u ON u.id_usuario = e.id_usuario
            JOIN livro l ON l.id_livro = e.id_livro
            ORDER BY e.data_emprestimo DESC
            """
        )
        return rows_to_list(cur.fetchall())


@router.get("/detalhe")
def obter_emprestimo(id_usuario: int, id_livro: int, data_emprestimo: date):
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT e.id_usuario, u.nome AS nome_usuario,
                   e.id_livro, l.titulo AS titulo_livro,
                   e.data_emprestimo, e.data_prev_devolucao,
                   e.data_devolucao, e.status, e.observacao
            FROM emprestimo e
            JOIN usuario u ON u.id_usuario = e.id_usuario
            JOIN livro l ON l.id_livro = e.id_livro
            WHERE e.id_usuario = %s AND e.id_livro = %s AND e.data_emprestimo = %s
            """,
            (id_usuario, id_livro, data_emprestimo),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Emprestimo nao encontrado")
        return row_to_dict(row)


@router.post("", status_code=201)
def criar_emprestimo(body: EmprestimoCreate):
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO emprestimo
                    (id_usuario, id_livro, data_emprestimo, data_prev_devolucao, observacao)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_usuario, id_livro, data_emprestimo
                """,
                (
                    body.id_usuario,
                    body.id_livro,
                    body.data_emprestimo,
                    body.data_prev_devolucao,
                    body.observacao,
                ),
            )
            row = cur.fetchone()
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_emprestimo(row["id_usuario"], row["id_livro"], row["data_emprestimo"])


@router.patch("/devolver")
def devolver_emprestimo(body: EmprestimoDevolver):
    data_dev = body.data_devolucao or date.today()
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                UPDATE emprestimo
                SET data_devolucao = %s
                WHERE id_usuario = %s AND id_livro = %s AND data_emprestimo = %s
                RETURNING id_usuario, id_livro, data_emprestimo
                """,
                (data_dev, body.id_usuario, body.id_livro, body.data_emprestimo),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Emprestimo nao encontrado")
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_emprestimo(row["id_usuario"], row["id_livro"], row["data_emprestimo"])
