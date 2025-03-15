from pydantic import BaseModel

class AnalysisResponse(BaseModel):
    analysis: str
