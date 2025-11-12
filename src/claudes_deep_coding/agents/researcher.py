"""
Researcher Agent - Specialized in code discovery and analysis.
"""

from typing import Any, Dict
from .base import BaseAgent


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent specializes in:
    - Code discovery and exploration
    - API and library research
    - Requirements analysis
    - Technology stack investigation
    """

    def __init__(self):
        super().__init__(
            agent_id="researcher",
            name="Researcher Agent",
            description="Specializes in code discovery, analysis, and research"
        )
        self.research_capabilities = [
            "code_analysis",
            "api_discovery",
            "documentation_review",
            "dependency_analysis",
            "architecture_exploration"
        ]

    async def can_handle_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle the task.
        
        Handles tasks related to:
        - Discovery
        - Research
        - Analysis
        - Investigation
        """
        task_type = task_data.get("type", "").lower()
        task_description = task_data.get("description", "").lower()
        
        research_keywords = [
            "research", "discover", "analyze", "investigate",
            "explore", "find", "study", "review", "examine"
        ]
        
        return any(keyword in task_type or keyword in task_description 
                   for keyword in research_keywords)

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a research task.
        
        Args:
            task_data: Task details including research objectives
            
        Returns:
            Research findings and analysis results
        """
        task_id = task_data.get("task_id", "unknown")
        await self.on_task_start(task_id, task_data)
        
        try:
            research_type = task_data.get("research_type", "general")
            target = task_data.get("target", "")
            
            # Simulate research process
            result = await self._perform_research(research_type, target, task_data)
            
            await self.on_task_complete(task_id, result)
            return {
                "success": True,
                "task_id": task_id,
                "agent": self.agent_id,
                "findings": result
            }
        
        except Exception as e:
            error_msg = str(e)
            await self.on_task_fail(task_id, error_msg)
            return {
                "success": False,
                "task_id": task_id,
                "agent": self.agent_id,
                "error": error_msg
            }

    async def _perform_research(
        self,
        research_type: str,
        target: str,
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform the actual research based on type.
        
        Args:
            research_type: Type of research to perform
            target: Target of the research
            task_data: Additional task parameters
            
        Returns:
            Research findings
        """
        findings = {
            "research_type": research_type,
            "target": target,
            "timestamp": self.state.get("last_updated"),
        }
        
        if research_type == "code_analysis":
            findings.update({
                "analysis": "Code structure and patterns analyzed",
                "recommendations": [
                    "Modular design recommended",
                    "Consider adding comprehensive tests",
                    "Documentation could be improved"
                ]
            })
        
        elif research_type == "api_discovery":
            findings.update({
                "discovered_apis": [
                    {"name": "LangChain API", "relevance": "high"},
                    {"name": "Anthropic API", "relevance": "high"}
                ],
                "integration_points": ["Model selection", "Agent orchestration"]
            })
        
        elif research_type == "dependency_analysis":
            findings.update({
                "dependencies_found": ["langchain", "langgraph", "pydantic"],
                "security_notes": "All dependencies from trusted sources",
                "update_recommendations": []
            })
        
        else:
            findings.update({
                "general_findings": f"Research completed for {target}",
                "notes": "Additional context gathered"
            })
        
        return findings

    def get_capabilities(self) -> Dict[str, Any]:
        """Get researcher-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps["research_capabilities"] = self.research_capabilities
        return base_caps
