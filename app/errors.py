import psycopg
from fastapi import HTTPException


def pg_error(exc: Exception) -> HTTPException:
    if isinstance(exc, psycopg.errors.IntegrityError):
        return HTTPException(status_code=409, detail=str(exc).split("\n")[0])
    if isinstance(exc, psycopg.Error):
        return HTTPException(status_code=400, detail=str(exc).split("\n")[0])
    raise exc
