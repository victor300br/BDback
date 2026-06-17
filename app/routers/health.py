from fastapi import APIRouter, HTTPException

from app.database import get_cursor

router = APIRouter(prefix="/api", tags=["sistema"])


@router.get("/health")
def health():
    try:
        with get_cursor() as (_, cur):
            cur.execute("SELECT 1 AS ok")
            cur.fetchone()
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc))
