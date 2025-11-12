"""
Claude's Deep Coding - Hierarchical AI Agent System
"""

__version__ = "0.1.0"

from .core.orchestrator import CodeOrchestrator
from .agents.researcher import ResearcherAgent
from .agents.generator import GeneratorAgent
from .agents.tester import TesterAgent
from .agents.refiner import RefinerAgent

__all__ = [
    "CodeOrchestrator",
    "ResearcherAgent", 
    "GeneratorAgent",
    "TesterAgent",
    "RefinerAgent",
]
