from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

from ..config import load_config, validate_config 
from ..core import Evaluation
from ..results import ResultCollector

class EvaluationService:
    """Handles core benchmarking operations"""
    
    def run_evaluation(self, 
                     config_path: str, 
                     output_path: Optional[str] = None) -> Dict[str, Any]:
        config = load_config(config_path)
        if validate_config(config) is not True:
            raise ValueError("Invalid configuration file")
        evaluator = Evaluation(config)
        collector = evaluator.run()
        
        self._save_results(collector, output_path)
    
    def list(self, dir) -> List[Dict[str, Any]]:
        tests_dir = Path(dir)
        if not tests_dir.exists():
            return []
            
        evaluations = []
        for file in tests_dir.glob("**/*.yaml"):
            config = load_config(str(file))
            evaluations.append({
                "name": file.stem,
                "path": str(file.relative_to(tests_dir)),
                "description": config.get("description", ""),
                "num_tests": len(config.get("tests", []))
            })
        return evaluations
    
    def _save_results(self, collector: ResultCollector, output_path: str):
        print(f"Saving results to {output_path}")
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        json_path = str(output_file.with_suffix(".json"))
        print(f"Saving results to {json_path}")
        collector.export_to_json(str(json_path))