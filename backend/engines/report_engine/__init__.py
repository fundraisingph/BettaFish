"""
ReportEngine Module
"""
from .services.report_service import ReportService
from .state.state import ReportState
from .models.schemas import (
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportTemplateRequest,
    ReportTemplateResponse,
    ReportStreamRequest,
    ProgressResponse
)

# Report Agent (main class)
class ReportAgent:
    """Main agent class for ReportEngine"""
    
    def __init__(self):
        self.report_service = ReportService()
    
    async def generate_report(self, **kwargs):
        """Generate a report"""
        return await self.report_service.generate_report(**kwargs)
    
    async def get_templates(self, **kwargs):
        """Get available report templates"""
        return await self.report_service.get_templates(**kwargs)
    
    async def stream_report(self, **kwargs):
        """Stream report generation progress"""
        return await self.report_service.stream_report(**kwargs)

__all__ = [
    "ReportAgent",
    "ReportState",
    "ReportService",
    "ReportGenerationRequest",
    "ReportGenerationResponse",
    "ReportTemplateRequest",
    "ReportTemplateResponse",
    "ReportStreamRequest",
    "ProgressResponse"
]