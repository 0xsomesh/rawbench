import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from litellm import ModelResponse

@dataclass
class Result:
    id: str
    prompt_id: str
    model_id: str
    test_id: str
    input_messages: List[Dict[str, str]]
    output_content: str
    output_messages: List[ModelResponse]
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0
    latency_ms: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


class ResultCollector:
    def __init__(self):
        self.results = []
    
    def add_result(self, result: Result):
        """Add a result to the collector."""
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all results."""
        if not self.results:
            return {
                'total_results': 0,
                'successful_results': 0,
                'failed_results': 0,
                'success_rate': 0.0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'avg_latency': 0.0
            }
        
        total_results = len(self.results)
        
        total_tokens = sum(r.total_tokens or 0 for r in self.results)
        avg_latency = sum(r.latency_ms or 0 for r in self.results) / total_results if total_results > 0 else 0
        count_models = len(set(r.model_id for r in self.results))
        count_prompts = len(set(r.prompt_id for r in self.results))
        return {
            'total_results': total_results,
            'total_tokens': total_tokens,
            'avg_latency': avg_latency,
            'count_models': count_models,
            'count_prompts': count_prompts
        }
    
    def export_to_json(self, filepath: str):
        """Export all results to JSON file."""
        data = {
            'summary': self.get_summary(),
            'results': [r.to_dict() for r in self.results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)