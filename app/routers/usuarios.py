import psycopg
from fastapi import APIRouter, HTTPException

from app.database import get_cursor, row_to_dict, rows_to_list
from app.errors import pg_error
from app.schemas import TipoLeitor, UsuarioCreate, UsuarioUpdate

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])

_USUARIO_SELECT = """
SELECT
    u.id_usuario, u.nome, u.cpf, u.email, u.telefone,
    CASE
        WHEN e.id_usuario IS NOT NULL THEN 'ESTUDANTE'
        WHEN p.id_usuario IS NOT NULL THEN 'PROFESSOR'
        WHEN f.id_usuario IS NOT NULL THEN 'FUNCIONARIO'
    END AS tipo,
    e.matricula, e.curso, e.periodo, e.limite_emprestimo,
    p.departamento, p.titulacao, p.sala,
    f.cod_funcional, f.setor, f.cargo, f.turno
FROM usuario u
LEFT JOIN estudante e ON e.id_usuario = u.id_usuario
LEFT JOIN professor p ON p.id_usuario = u.id_usuario
LEFT JOIN funcionario f ON f.id_usuario = u.id_usuario
"""


def _insert_subtipo(cur, id_usuario: int, tipo: TipoLeitor, data: dict):
    if tipo == "ESTUDANTE":
        cur.execute(
            """
            INSERT INTO estudante (id_usuario, matricula, curso, periodo, limite_emprestimo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                id_usuario,
                data["matricula"],
                data["curso"],
                data.get("periodo"),
                data.get("limite_emprestimo"),
            ),
        )
    elif tipo == "PROFESSOR":
        cur.execute(
            """
            INSERT INTO professor (id_usuario, departamento, titulacao, sala)
            VALUES (%s, %s, %s, %s)
            """,
            (
                id_usuario,
                data["departamento"],
                data.get("titulacao"),
                data.get("sala"),
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO funcionario (id_usuario, cod_funcional, setor, cargo, turno)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                id_usuario,
                data["cod_funcional"],
                data["setor"],
                data.get("cargo"),
                data.get("turno"),
            ),
        )


def _update_subtipo(cur, id_usuario: int, tipo: TipoLeitor, data: dict):
    if tipo == "ESTUDANTE":
        cur.execute(
            """
            UPDATE estudante
            SET matricula = %s, curso = %s, periodo = %s, limite_emprestimo = %s
            WHERE id_usuario = %s
            """,
            (
                data["matricula"],
                data["curso"],
                data.get("periodo"),
                data.get("limite_emprestimo"),
                id_usuario,
            ),
        )
    elif tipo == "PROFESSOR":
        cur.execute(
            """
            UPDATE professor
            SET departamento = %s, titulacao = %s, sala = %s
            WHERE id_usuario = %s
            """,
            (
                data["departamento"],
                data.get("titulacao"),
                data.get("sala"),
                id_usuario,
            ),
        )
    else:
        cur.execute(
            """
            UPDATE funcionario
            SET cod_funcional = %s, setor = %s, cargo = %s, turno = %s
            WHERE id_usuario = %s
            """,
            (
                data["cod_funcional"],
                data["setor"],
                data.get("cargo"),
                data.get("turno"),
                id_usuario,
            ),
        )


def _clear_subtipos(cur, id_usuario: int):
    cur.execute("DELETE FROM estudante WHERE id_usuario = %s", (id_usuario,))
    cur.execute("DELETE FROM professor WHERE id_usuario = %s", (id_usuario,))
    cur.execute("DELETE FROM funcionario WHERE id_usuario = %s", (id_usuario,))


def _subtipo_payload(body) -> dict:
    return body.model_dump()


def _merge_subtipo(current: dict, body: UsuarioUpdate) -> dict:
    merged = dict(current)
    for key in (
        "matricula", "curso", "periodo", "limite_emprestimo",
        "departamento", "titulacao", "sala",
        "cod_funcional", "setor", "cargo", "turno",
    ):
        val = getattr(body, key, None)
        if val is not None:
            merged[key] = val
    return merged


def _subtipo_foi_informado(body: UsuarioUpdate) -> bool:
    if body.tipo is not None:
        return True
    return any(
        getattr(body, key) is not None
        for key in (
            "matricula", "curso", "periodo", "limite_emprestimo",
            "departamento", "titulacao", "sala",
            "cod_funcional", "setor", "cargo", "turno",
        )
    )


def _fetch_usuario(cur, id_usuario: int):
    cur.execute(f"{_USUARIO_SELECT} WHERE u.id_usuario = %s", (id_usuario,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return row_to_dict(row)


@router.get("")
def listar_usuarios():
    with get_cursor() as (_, cur):
        cur.execute(f"{_USUARIO_SELECT} ORDER BY u.nome")
        return rows_to_list(cur.fetchall())


@router.get("/{id_usuario}")
def obter_usuario(id_usuario: int):
    with get_cursor() as (_, cur):
        return _fetch_usuario(cur, id_usuario)


@router.post("", status_code=201)
def criar_usuario(body: UsuarioCreate):
    data = _subtipo_payload(body)
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO usuario (nome, cpf, email, telefone)
                VALUES (%s, %s, %s, %s)
                RETURNING id_usuario
                """,
                (body.nome, body.cpf, body.email, body.telefone),
            )
            new_id = cur.fetchone()["id_usuario"]
            _insert_subtipo(cur, new_id, body.tipo, data)
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_usuario(new_id)


@router.put("/{id_usuario}")
def atualizar_usuario(id_usuario: int, body: UsuarioUpdate):
    fields = {
        k: v
        for k, v in body.model_dump().items()
        if k not in {
            "tipo", "matricula", "curso", "periodo", "limite_emprestimo",
            "departamento", "titulacao", "sala",
            "cod_funcional", "setor", "cargo", "turno",
        }
        and v is not None
    }
    data = _subtipo_payload(body)
    try:
        with get_cursor() as (_, cur):
            current = _fetch_usuario(cur, id_usuario)
            if fields:
                sets = ", ".join(f"{k} = %s" for k in fields)
                values = list(fields.values()) + [id_usuario]
                cur.execute(
                    f"UPDATE usuario SET {sets} WHERE id_usuario = %s RETURNING id_usuario",
                    values,
                )
                if not cur.fetchone():
                    raise HTTPException(status_code=404, detail="Usuario nao encontrado")

            if not _subtipo_foi_informado(body):
                return row_to_dict(current)

            new_tipo = body.tipo or current.get("tipo")
            if not new_tipo:
                raise HTTPException(
                    status_code=400,
                    detail="Informe o perfil do leitor (estudante, professor ou funcionario)",
                )

            merged = _merge_subtipo(current, body)
            if body.tipo and body.tipo != current.get("tipo"):
                _clear_subtipos(cur, id_usuario)
                _insert_subtipo(cur, id_usuario, new_tipo, merged)
            elif current.get("tipo"):
                _update_subtipo(cur, id_usuario, current["tipo"], merged)
            else:
                _insert_subtipo(cur, id_usuario, new_tipo, merged)
    except psycopg.Error as exc:
        raise pg_error(exc)
    return obter_usuario(id_usuario)


@router.delete("/{id_usuario}", status_code=204)
def remover_usuario(id_usuario: int):
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                "DELETE FROM usuario WHERE id_usuario = %s RETURNING id_usuario",
                (id_usuario,),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    except psycopg.Error as exc:
        raise pg_error(exc)
