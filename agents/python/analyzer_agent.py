"""
Analyzer Agent - Pure Python Implementation
Execution: Python (No LLM Required)

Purpose: Calculate complexity scores, build dependency graphs,
and determine optimal migration order.
"""

import json
import os
from typing import Dict, List, Set
from collections import defaultdict
from dataclasses import dataclass, asdict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import ParsedModule, AnalysisResult


@dataclass
class ComplexityWeights:
    """Configurable weights for complexity calculation."""
    entity: float = 2.0
    attribute: float = 0.5
    relationship: float = 1.5
    server_action: float = 3.0
    client_action: float = 2.0
    screen: float = 4.0
    aggregate: float = 1.0
    rest_consume: float = 3.0
    rest_expose: float = 3.5
    timer: float = 2.5
    process: float = 5.0
    extension: float = 4.0


class AnalyzerAgent:
    """
    Pure Python agent - No LLM required.
    Analyzes parsed modules for complexity and dependencies.
    """
    
    def __init__(self, weights: ComplexityWeights = None):
        self.weights = weights or ComplexityWeights()
    
    def analyze(self, modules: Dict[str, ParsedModule]) -> AnalysisResult:
        """Perform complete analysis on all modules."""
        complexity_scores = self._calculate_complexity(modules)
        dependency_graph = self._build_dependency_graph(modules)
        migration_order = self._determine_migration_order(dependency_graph, complexity_scores)
        risk_assessment = self._assess_risks(modules)
        statistics = self._gather_statistics(modules)
        
        total = sum(complexity_scores.values())
        level = self._get_complexity_level(total)
        
        return AnalysisResult(
            modules=list(modules.keys()),
            complexity_scores=complexity_scores,
            total_complexity=total,
            complexity_level=level,
            migration_order=migration_order,
            dependency_graph=dependency_graph,
            risk_assessment=risk_assessment,
            statistics=statistics
        )
    
    def _calculate_complexity(self, modules: Dict[str, ParsedModule]) -> Dict[str, float]:
        """Calculate complexity score for each module."""
        scores = {}
        
        for name, module in modules.items():
            score = 0.0
            
            score += len(module.entities) * self.weights.entity
            for entity in module.entities:
                score += len(entity.get("attributes", [])) * self.weights.attribute
            
            score += len(module.relationships) * self.weights.relationship
            score += len(module.server_actions) * self.weights.server_action
            score += len(module.client_actions) * self.weights.client_action
            score += len(module.screens) * self.weights.screen
            score += len(module.aggregates) * self.weights.aggregate
            score += len(module.rest_consumes) * self.weights.rest_consume
            score += len(module.rest_exposes) * self.weights.rest_expose
            score += len(module.timers) * self.weights.timer
            score += len(module.processes) * self.weights.process
            score += len(module.extensions) * self.weights.extension
            
            scores[name] = round(score, 2)
        
        return scores
    
    def _build_dependency_graph(self, modules: Dict[str, ParsedModule]) -> Dict[str, List[str]]:
        """Build module dependency graph."""
        graph = defaultdict(list)
        module_names = set(modules.keys())
        
        for name, module in modules.items():
            for dep in module.dependencies:
                dep_name = dep.get("name") or dep.get("producer")
                if dep_name and dep_name in module_names:
                    if dep_name not in graph[name]:
                        graph[name].append(dep_name)
            
            for rel in module.relationships:
                to_entity = rel.get("to_entity", "")
                for other_name, other_module in modules.items():
                    if other_name != name:
                        for entity in other_module.entities:
                            if entity.get("name") == to_entity:
                                if other_name not in graph[name]:
                                    graph[name].append(other_name)
        
        for name in modules:
            if name not in graph:
                graph[name] = []
        
        return dict(graph)
    
    def _determine_migration_order(
        self,
        dependency_graph: Dict[str, List[str]],
        complexity_scores: Dict[str, float]
    ) -> List[str]:
        """Determine optimal migration order using topological sort."""
        in_degree = defaultdict(int)
        for node in dependency_graph:
            if node not in in_degree:
                in_degree[node] = 0
        
        for node, deps in dependency_graph.items():
            for dep in deps:
                in_degree[node] += 1
        
        order = []
        available = []
        
        for node, degree in in_degree.items():
            if degree == 0:
                available.append(node)
        
        while available:
            available.sort(key=lambda x: complexity_scores.get(x, 0))
            node = available.pop(0)
            order.append(node)
            
            for other, deps in dependency_graph.items():
                if node in deps:
                    in_degree[other] -= 1
                    if in_degree[other] == 0 and other not in order:
                        available.append(other)
        
        remaining = set(dependency_graph.keys()) - set(order)
        if remaining:
            remaining_sorted = sorted(remaining, key=lambda x: complexity_scores.get(x, 0))
            order.extend(remaining_sorted)
        
        return order
    
    def _assess_risks(self, modules: Dict[str, ParsedModule]) -> List[Dict]:
        """Assess migration risks."""
        risks = []
        
        for name, module in modules.items():
            if module.extensions:
                risks.append({
                    "module": name,
                    "type": "high",
                    "category": "extension",
                    "description": f"Module uses {len(module.extensions)} extension(s) - custom .NET code required"
                })
            
            if module.processes:
                risks.append({
                    "module": name,
                    "type": "high",
                    "category": "bpt",
                    "description": f"Module has {len(module.processes)} BPT process(es) - workflow engine needed"
                })
            
            for action in module.server_actions:
                if len(action.get("flow", [])) > 20:
                    risks.append({
                        "module": name,
                        "type": "medium",
                        "category": "complexity",
                        "description": f"Action '{action.get('name')}' has complex flow ({len(action.get('flow', []))} nodes)"
                    })
            
            if len(module.rest_consumes) > 5:
                risks.append({
                    "module": name,
                    "type": "medium",
                    "category": "integration",
                    "description": f"Module consumes {len(module.rest_consumes)} external APIs"
                })
            
            for screen in module.screens:
                if len(screen.get("widgets", [])) > 50:
                    risks.append({
                        "module": name,
                        "type": "medium",
                        "category": "ui_complexity",
                        "description": f"Screen '{screen.get('name')}' has {len(screen.get('widgets', []))} widgets"
                    })
        
        return sorted(risks, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["type"], 3))
    
    def _gather_statistics(self, modules: Dict[str, ParsedModule]) -> Dict[str, int]:
        """Gather overall statistics."""
        stats = {
            "total_modules": len(modules),
            "total_entities": 0,
            "total_attributes": 0,
            "total_static_entities": 0,
            "total_relationships": 0,
            "total_structures": 0,
            "total_server_actions": 0,
            "total_client_actions": 0,
            "total_aggregates": 0,
            "total_screens": 0,
            "total_web_blocks": 0,
            "total_rest_consumes": 0,
            "total_rest_exposes": 0,
            "total_timers": 0,
            "total_processes": 0,
            "total_roles": 0,
            "total_site_properties": 0,
            "total_extensions": 0
        }
        
        for module in modules.values():
            stats["total_entities"] += len(module.entities)
            for entity in module.entities:
                stats["total_attributes"] += len(entity.get("attributes", []))
            stats["total_static_entities"] += len(module.static_entities)
            stats["total_relationships"] += len(module.relationships)
            stats["total_structures"] += len(module.structures)
            stats["total_server_actions"] += len(module.server_actions)
            stats["total_client_actions"] += len(module.client_actions)
            stats["total_aggregates"] += len(module.aggregates)
            stats["total_screens"] += len(module.screens)
            stats["total_web_blocks"] += len(module.web_blocks)
            stats["total_rest_consumes"] += len(module.rest_consumes)
            stats["total_rest_exposes"] += len(module.rest_exposes)
            stats["total_timers"] += len(module.timers)
            stats["total_processes"] += len(module.processes)
            stats["total_roles"] += len(module.roles)
            stats["total_site_properties"] += len(module.site_properties)
            stats["total_extensions"] += len(module.extensions)
        
        return stats
    
    def _get_complexity_level(self, total: float) -> str:
        """Determine overall complexity level."""
        if total < 50:
            return "Low"
        elif total < 150:
            return "Medium"
        elif total < 300:
            return "High"
        else:
            return "Very High"
    
    def save_analysis(self, result: AnalysisResult, output_path: str):
        """Save analysis result to JSON."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze parsed OutSystems modules")
    parser.add_argument("input_dir", help="Directory with parsed JSON files")
    parser.add_argument("-o", "--output", default="./analysis.json", help="Output file")
    args = parser.parse_args()
    
    modules = {}
    for filename in os.listdir(args.input_dir):
        if filename.endswith(".json") and not filename.startswith("_"):
            filepath = os.path.join(args.input_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
                module = ParsedModule(**data)
                modules[module.module_name] = module
    
    agent = AnalyzerAgent()
    result = agent.analyze(modules)
    agent.save_analysis(result, args.output)
    
    print(f"Analysis complete:")
    print(f"  Modules: {len(result.modules)}")
    print(f"  Total Complexity: {result.total_complexity} ({result.complexity_level})")
    print(f"  Migration Order: {' -> '.join(result.migration_order)}")
    print(f"  Risks: {len(result.risk_assessment)}")
