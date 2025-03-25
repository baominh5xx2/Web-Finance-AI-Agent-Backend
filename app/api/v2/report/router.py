from fastapi import APIRouter
from fastapi.responses import FileResponse
from . import services
from .schemas import AnalysisResponse

router = APIRouter()

@router.get("/pdf/{symbol}")
def get_pdf(symbol: str):
    file_path = services.generate_pdf_report(symbol)
    return FileResponse(file_path, media_type="application/pdf", filename=f"Financial_Report_{symbol}.pdf")
