from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai
from ..Chatbot.gemini_api import Gemini_api
from ..Chatbot.generate_plot import GeneratePlot
from ..Chatbot.latex_pdf.latex_generator import LatexGenerator
import os
from typing import Dict, Any

router = APIRouter()
gemini_bot = Gemini_api()
plot_generator = GeneratePlot(None, None, gemini_bot)
latex_generator = LatexGenerator(gemini_bot)

# Request models
class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None

class PlotRequest(BaseModel):
    description: str
    data: Optional[Dict[str, Any]] = None

class PDFRequest(BaseModel):
    content: str
    title: Optional[str] = None
    template_type: Optional[str] = "basic"  # basic, report, academic, etc.

# Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/ask", response_model=APIResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question to the AI bot
    """
    try:
        response = await gemini_bot.generate_ai_response(request.question, request.context)
        return {
            "success": True,
            "message": "Question answered successfully",
            "data": {"answer": response}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/plot", response_model=APIResponse)
async def generate_plot(request: PlotRequest, background_tasks: BackgroundTasks):
    """
    Generate a plot based on description or data
    """
    try:
        # If data is provided, use it directly, otherwise generate from description
        if request.data:
            plot_path = await plot_generator.create_plot_from_data(request.data)
        else:
            plot_path = await plot_generator.create_plot_from_description(request.description)

        # Convert plot to base64 if needed
        with open(plot_path, "rb") as image_file:
            import base64
            encoded_image = base64.b64encode(image_file.read()).decode()

        # Clean up the file in background
        background_tasks.add_task(os.remove, plot_path)

        return {
            "success": True,
            "message": "Plot generated successfully",
            "data": {
                "image": encoded_image,
                "format": "base64"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf", response_model=APIResponse)
async def generate_pdf(request: PDFRequest):
    """
    Generate a PDF document based on content and template
    """
    try:
        pdf_path = await latex_generator.generate_pdf(
            content=request.content,
            title=request.title,
            template_type=request.template_type
        )

        # Convert PDF to base64
        with open(pdf_path, "rb") as pdf_file:
            import base64
            encoded_pdf = base64.b64encode(pdf_file.read()).decode()

        return {
            "success": True,
            "message": "PDF generated successfully",
            "data": {
                "pdf": encoded_pdf,
                "format": "base64"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
