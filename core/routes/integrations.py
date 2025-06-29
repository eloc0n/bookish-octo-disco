from fastapi import APIRouter, status, HTTPException
from core.crud.integrations import initialize

router = APIRouter(prefix="/import", tags=["Integration"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def fetch_data():
    try:
        initialize()
        return {"detail": "Import started in the background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
