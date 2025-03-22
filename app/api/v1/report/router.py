from fastapi import APIRouter
from fastapi.responses import FileResponse
from . import services
from .schemas import AnalysisResponse

router = APIRouter()

@router.get("/pdf/{symbol}")
def get_pdf(symbol: str):
    file_path = services.generate_pdf_report(symbol)
    return FileResponse(file_path, media_type="application/pdf", filename=f"Financial_Report_{symbol}.pdf")

@router.get("/analysis", response_model=AnalysisResponse)
def get_analysis():
    return {"analysis": services.get_financial_analysis()}

@router.get("/company-overview")
def get_company_overview():
    """Generate a PDF with company overview information."""
    file_path = services.generate_company_overview_pdf()
    return FileResponse(file_path, media_type="application/pdf", filename="Company_Overview.pdf")

@router.get("/financial-ratios")
def get_financial_ratios():
    """Generate a PDF with financial ratios information."""
    file_path = services.generate_financial_ratios_pdf()
    return FileResponse(file_path, media_type="application/pdf", filename="Financial_Ratios.pdf")
