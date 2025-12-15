"""
ReportEngine Report State
"""
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

class ReportState:
    """Report generation state for ReportEngine"""
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        title: str = "",
        template_type: str = "comprehensive",
        engine_outputs: Dict[str, Any] = None,
        include_charts: bool = False,
        output_format: str = "markdown",
        initial_state: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.title = title
        self.template_type = template_type
        self.engine_outputs = engine_outputs or {}
        self.include_charts = include_charts
        self.output_format = output_format
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Report generation state
        self.current_step = "initializing"
        self.progress_percentage = 0
        self.report_structure = None
        self.report_content = None
        self.html_content = None
        self.pdf_content = None
        self.charts = None
        self.error = None
        
        # Initialize from existing state if provided
        if initial_state:
            self.from_dict(initial_state)
    
    def set_current_step(self, step: str):
        """Set the current step"""
        self.current_step = step
        self.updated_at = datetime.now()
    
    def set_progress_percentage(self, percentage: int):
        """Set the progress percentage"""
        self.progress_percentage = max(0, min(100, percentage))
        self.updated_at = datetime.now()
    
    def set_engine_outputs(self, outputs: Dict[str, Any]):
        """Set engine outputs"""
        self.engine_outputs = outputs
        self.updated_at = datetime.now()
    
    def set_report_structure(self, structure: Dict[str, Any]):
        """Set the report structure"""
        self.report_structure = structure
        self.updated_at = datetime.now()
    
    def set_report_content(self, content: str):
        """Set the report content"""
        self.report_content = content
        self.updated_at = datetime.now()
    
    def set_html_content(self, content: str):
        """Set the HTML content"""
        self.html_content = content
        self.updated_at = datetime.now()
    
    def set_pdf_content(self, content: str):
        """Set the PDF content"""
        self.pdf_content = content
        self.updated_at = datetime.now()
    
    def set_charts(self, charts: Dict[str, Any]):
        """Set the charts"""
        self.charts = charts
        self.updated_at = datetime.now()
    
    def set_error(self, error: str):
        """Set an error"""
        self.error = error
        self.current_step = "failed"
        self.updated_at = datetime.now()
    
    def get_current_step(self) -> str:
        """Get the current step"""
        return self.current_step
    
    def get_progress_percentage(self) -> int:
        """Get the progress percentage"""
        return self.progress_percentage
    
    def get_status(self) -> str:
        """Get the current status"""
        if self.error:
            return "failed"
        elif self.progress_percentage >= 100:
            return "completed"
        elif self.progress_percentage > 0:
            return "in_progress"
        else:
            return "pending"
    
    def get_content_for_format(self, format_type: str) -> Optional[str]:
        """Get content for a specific format"""
        if format_type == "html" and self.html_content:
            return self.html_content
        elif format_type == "pdf" and self.pdf_content:
            return self.pdf_content
        elif format_type in ["markdown", "txt"] and self.report_content:
            return self.report_content
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "template_type": self.template_type,
            "engine_outputs": self.engine_outputs,
            "include_charts": self.include_charts,
            "output_format": self.output_format,
            "current_step": self.current_step,
            "progress_percentage": self.progress_percentage,
            "report_structure": self.report_structure,
            "report_content": self.report_content,
            "html_content": self.html_content,
            "pdf_content": self.pdf_content,
            "charts": self.charts,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Initialize state from dictionary"""
        self.session_id = data.get("session_id", self.session_id)
        self.title = data.get("title", self.title)
        self.template_type = data.get("template_type", self.template_type)
        self.engine_outputs = data.get("engine_outputs", self.engine_outputs)
        self.include_charts = data.get("include_charts", self.include_charts)
        self.output_format = data.get("output_format", self.output_format)
        self.current_step = data.get("current_step", self.current_step)
        self.progress_percentage = data.get("progress_percentage", self.progress_percentage)
        self.report_structure = data.get("report_structure", self.report_structure)
        self.report_content = data.get("report_content", self.report_content)
        self.html_content = data.get("html_content", self.html_content)
        self.pdf_content = data.get("pdf_content", self.pdf_content)
        self.charts = data.get("charts", self.charts)
        self.error = data.get("error", self.error)
        
        if data.get("created_at"):
            self.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("updated_at"):
            self.updated_at = datetime.fromisoformat(data["updated_at"])
    
    def to_json(self) -> str:
        """Convert state to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "ReportState":
        """Create state from JSON"""
        data = json.loads(json_str)
        return cls(initial_state=data)
    
    def get_summary(self) -> str:
        """Get a summary of the report state"""
        status = self.get_status()
        progress = self.get_progress_percentage()
        
        summary = f"Report Session {self.session_id}\n"
        summary += f"Title: {self.title}\n"
        summary += f"Template: {self.template_type}\n"
        summary += f"Format: {self.output_format}\n"
        summary += f"Status: {status}\n"
        summary += f"Progress: {progress}%\n"
        summary += f"Current Step: {self.current_step}\n"
        
        if self.engine_outputs:
            summary += f"Engine Outputs: {len(self.engine_outputs)} engines\n"
        
        if self.charts:
            summary += f"Charts: {len(self.charts)} generated\n"
        
        if self.error:
            summary += f"Error: {self.error}\n"
        
        return summary
    
    def get_duration(self) -> float:
        """Get report generation duration in seconds"""
        return (self.updated_at - self.created_at).total_seconds()
    
    def is_complete(self) -> bool:
        """Check if report generation is complete"""
        return self.get_status() == "completed"
    
    def is_failed(self) -> bool:
        """Check if report generation has failed"""
        return self.get_status() == "failed"
    
    def is_in_progress(self) -> bool:
        """Check if report generation is in progress"""
        return self.get_status() == "in_progress"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata for the report"""
        return {
            "title": self.title,
            "template_type": self.template_type,
            "output_format": self.output_format,
            "include_charts": self.include_charts,
            "engine_count": len(self.engine_outputs),
            "chart_count": len(self.charts) if self.charts else 0,
            "duration": self.get_duration(),
            "status": self.get_status()
        }
    
    def add_metadata(self, metadata: Dict[str, Any]):
        """Add metadata to the state"""
        # This could be extended to store additional metadata
        self.updated_at = datetime.now()
    
    def get_chart_data(self, chart_type: str) -> Optional[Dict[str, Any]]:
        """Get specific chart data"""
        if not self.charts:
            return None
        
        return self.charts.get(chart_type)
    
    def get_all_chart_data(self) -> Dict[str, Any]:
        """Get all chart data"""
        return self.charts or {}
    
    def get_engine_output(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific engine"""
        return self.engine_outputs.get(engine_name)
    
    def get_all_engine_outputs(self) -> Dict[str, Any]:
        """Get all engine outputs"""
        return self.engine_outputs or {}
    
    def has_engine_output(self, engine_name: str) -> bool:
        """Check if output exists for a specific engine"""
        return engine_name in self.engine_outputs
    
    def get_engine_names(self) -> List[str]:
        """Get list of engine names with outputs"""
        return list(self.engine_outputs.keys())
    
    def get_report_size(self) -> int:
        """Get estimated report size in characters"""
        size = 0
        
        if self.report_content:
            size += len(self.report_content)
        
        if self.html_content:
            size += len(self.html_content)
        
        if self.pdf_content:
            size += len(self.pdf_content)
        
        return size
    
    def get_estimated_completion_time(self) -> Optional[datetime]:
        """Get estimated completion time based on current progress"""
        if self.progress_percentage <= 0:
            return None
        
        if self.is_complete():
            return self.updated_at
        
        # Simple estimation based on current progress
        elapsed = self.get_duration()
        estimated_total = elapsed * (100 / self.progress_percentage)
        estimated_completion = self.created_at + estimated_total
        
        return estimated_completion