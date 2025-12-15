"""
QueryEngine Research State
"""
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

class ResearchState:
    """Research state for QueryEngine"""
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        query: str = "",
        research_type: str = "comprehensive",
        max_iterations: int = 3,
        initial_state: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id or str(uuid.uuid4())
        self.query = query
        self.research_type = research_type
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.iterations = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Initialize from existing state if provided
        if initial_state:
            self.from_dict(initial_state)
    
    def add_iteration_results(
        self,
        search_results: List[Dict[str, Any]],
        summary: str,
        insights: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add results for an iteration"""
        self.current_iteration += 1
        
        iteration_data = {
            "iteration": self.current_iteration,
            "search_results": search_results,
            "summary": summary,
            "insights": insights or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        self.iterations.append(iteration_data)
        self.updated_at = datetime.now()
    
    def get_current_iteration(self) -> int:
        """Get current iteration number"""
        return self.current_iteration
    
    def get_max_iterations(self) -> int:
        """Get maximum iterations"""
        return self.max_iterations
    
    def is_complete(self) -> bool:
        """Check if research is complete"""
        return self.current_iteration >= self.max_iterations
    
    def get_latest_results(self) -> Optional[Dict[str, Any]]:
        """Get results from latest iteration"""
        if self.iterations:
            return self.iterations[-1]
        return None
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all iteration results"""
        return self.iterations
    
    def get_all_search_results(self) -> List[Dict[str, Any]]:
        """Get all search results from all iterations"""
        all_results = []
        for iteration in self.iterations:
            all_results.extend(iteration.get("search_results", []))
        return all_results
    
    def get_all_summaries(self) -> List[str]:
        """Get all summaries from all iterations"""
        return [iteration.get("summary", "") for iteration in self.iterations]
    
    def get_all_insights(self) -> List[str]:
        """Get all insights from all iterations"""
        all_insights = []
        for iteration in self.iterations:
            all_insights.extend(iteration.get("insights", []))
        return all_insights
    
    def update_query(self, new_query: str):
        """Update the research query"""
        self.query = new_query
        self.updated_at = datetime.now()
    
    def update_max_iterations(self, new_max: int):
        """Update maximum iterations"""
        self.max_iterations = new_max
        self.updated_at = datetime.now()
    
    def reset_iterations(self):
        """Reset all iterations"""
        self.current_iteration = 0
        self.iterations = []
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "session_id": self.session_id,
            "query": self.query,
            "research_type": self.research_type,
            "max_iterations": self.max_iterations,
            "current_iteration": self.current_iteration,
            "iterations": self.iterations,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Initialize state from dictionary"""
        self.session_id = data.get("session_id", self.session_id)
        self.query = data.get("query", self.query)
        self.research_type = data.get("research_type", self.research_type)
        self.max_iterations = data.get("max_iterations", self.max_iterations)
        self.current_iteration = data.get("current_iteration", self.current_iteration)
        self.iterations = data.get("iterations", self.iterations)
        
        if data.get("created_at"):
            self.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("updated_at"):
            self.updated_at = datetime.fromisoformat(data["updated_at"])
    
    def to_json(self) -> str:
        """Convert state to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "ResearchState":
        """Create state from JSON"""
        data = json.loads(json_str)
        return cls(initial_state=data)
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage"""
        if self.max_iterations == 0:
            return 100.0
        return (self.current_iteration / self.max_iterations) * 100
    
    def get_status(self) -> str:
        """Get current status"""
        if self.is_complete():
            return "completed"
        elif self.current_iteration == 0:
            return "pending"
        else:
            return "in_progress"
    
    def get_summary(self) -> str:
        """Get a summary of the research state"""
        status = self.get_status()
        progress = self.get_progress_percentage()
        
        summary = f"Research Session {self.session_id}\n"
        summary += f"Query: {self.query}\n"
        summary += f"Type: {self.research_type}\n"
        summary += f"Status: {status}\n"
        summary += f"Progress: {progress:.1f}% ({self.current_iteration}/{self.max_iterations} iterations)\n"
        
        if self.iterations:
            summary += f"Total search results: {len(self.get_all_search_results())}\n"
            summary += f"Total insights: {len(self.get_all_insights())}\n"
        
        return summary
    
    def get_latest_summary(self) -> str:
        """Get the latest summary"""
        if self.iterations:
            return self.iterations[-1].get("summary", "")
        return ""
    
    def get_latest_insights(self) -> List[str]:
        """Get the latest insights"""
        if self.iterations:
            return self.iterations[-1].get("insights", [])
        return []
    
    def get_iteration_count(self) -> int:
        """Get the number of completed iterations"""
        return len(self.iterations)
    
    def has_results(self) -> bool:
        """Check if any results exist"""
        return len(self.iterations) > 0
    
    def get_metadata(self, iteration: Optional[int] = None) -> Dict[str, Any]:
        """Get metadata for a specific iteration or all iterations"""
        if iteration is not None:
            if 0 < iteration <= len(self.iterations):
                return self.iterations[iteration - 1].get("metadata", {})
            return {}
        
        # Get combined metadata from all iterations
        combined_metadata = {}
        for iteration_data in self.iterations:
            combined_metadata.update(iteration_data.get("metadata", {}))
        
        return combined_metadata
    
    def add_metadata(self, metadata: Dict[str, Any], iteration: Optional[int] = None):
        """Add metadata to a specific iteration or all iterations"""
        if iteration is not None and 0 < iteration <= len(self.iterations):
            self.iterations[iteration - 1]["metadata"].update(metadata)
        else:
            # Add to latest iteration if exists
            if self.iterations:
                self.iterations[-1]["metadata"].update(metadata)
        
        self.updated_at = datetime.now()
    
    def get_duration(self) -> float:
        """Get research duration in seconds"""
        return (self.updated_at - self.created_at).total_seconds()
    
    def get_average_results_per_iteration(self) -> float:
        """Get average number of search results per iteration"""
        if not self.iterations:
            return 0.0
        
        total_results = sum(len(iteration.get("search_results", [])) for iteration in self.iterations)
        return total_results / len(self.iterations)
    
    def get_average_insights_per_iteration(self) -> float:
        """Get average number of insights per iteration"""
        if not self.iterations:
            return 0.0
        
        total_insights = sum(len(iteration.get("insights", [])) for iteration in self.iterations)
        return total_insights / len(self.iterations)
