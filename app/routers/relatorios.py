from fastapi import APIRouter

from app.database import get_cursor, rows_to_list

router = APIRouter(prefix="/api/relatorios", tags=["relatorios"])


@router.get("/emprestimos-detalhados")
def relatorio_join():
    with get_cursor() as (_, cur):
        cur.execute(
            "SELECT * FROM vw_emprestimos_detalhados ORDER BY data_emprestimo DESC"
        )
        return rows_to_list(cur.fetchall())


@router.get("/por-status")
def relatorio_group_by():
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT status, COUNT(*) AS total
            FROM emprestimo
            GROUP BY status
            ORDER BY status
            """
        )
        return rows_to_list(cur.fetchall())


@router.get("/categorias-populares")
def relatorio_having():
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT c.nome AS categoria, COUNT(l.id_livro) AS qtd_livros
            FROM categoria c
            JOIN livro l ON l.id_categoria = c.id_categoria
            GROUP BY c.id_categoria, c.nome
            HAVING COUNT(l.id_livro) > 1
            ORDER BY qtd_livros DESC
            """
        )
        return rows_to_list(cur.fetchall())
