"""
Generator Agent - Specialized in code generation and creation.
"""

from typing import Any, Dict
from .base import BaseAgent


class GeneratorAgent(BaseAgent):
    """
    Generator Agent specializes in:
    - Code generation
    - Module creation
    - Template instantiation
    - Boilerplate generation
    """

    def __init__(self):
        super().__init__(
            agent_id="generator",
            name="Generator Agent",
            description="Specializes in code generation and creation"
        )
        self.generation_capabilities = [
            "code_generation",
            "module_creation",
            "template_instantiation",
            "boilerplate_generation",
            "scaffold_creation"
        ]

    async def can_handle_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle the task.
        
        Handles tasks related to:
        - Generation
        - Creation
        - Writing
        - Building
        """
        task_type = task_data.get("type", "").lower()
        task_description = task_data.get("description", "").lower()
        
        generation_keywords = [
            "generate", "create", "write", "build",
            "implement", "develop", "produce", "make"
        ]
        
        return any(keyword in task_type or keyword in task_description 
                   for keyword in generation_keywords)

    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a code generation task.
        
        Args:
            task_data: Task details including generation requirements
            
        Returns:
            Generated code and metadata
        """
        task_id = task_data.get("task_id", "unknown")
        await self.on_task_start(task_id, task_data)
        
        try:
            generation_type = task_data.get("generation_type", "general")
            target = task_data.get("target", "")
            specifications = task_data.get("specifications", {})
            
            # Perform code generation
            result = await self._generate_code(generation_type, target, specifications)
            
            await self.on_task_complete(task_id, result)
            return {
                "success": True,
                "task_id": task_id,
                "agent": self.agent_id,
                "generated_artifacts": result
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

    async def _generate_code(
        self,
        generation_type: str,
        target: str,
        specifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate code based on specifications.
        
        Args:
            generation_type: Type of generation to perform
            target: Target output (module, function, class, etc.)
            specifications: Detailed specifications for generation
            
        Returns:
            Generated code and metadata
        """
        artifacts = {
            "generation_type": generation_type,
            "target": target,
            "timestamp": self.state.get("last_updated"),
        }
        
        if generation_type == "module":
            artifacts.update({
                "files_created": [f"{target}.py"],
                "code_sample": f"# Generated module: {target}\n\nclass {target.capitalize()}:\n    pass",
                "documentation": f"Module {target} generated with specified requirements"
            })
        
        elif generation_type == "function":
            artifacts.update({
                "function_name": target,
                "code_sample": f"def {target}():\n    '''Generated function'''\n    pass",
                "signature": f"{target}()",
                "documentation": "Generated function with placeholder implementation"
            })
        
        elif generation_type == "class":
            artifacts.update({
                "class_name": target,
                "code_sample": f"class {target}:\n    '''Generated class'''\n    def __init__(self):\n        pass",
                "methods": ["__init__"],
                "documentation": "Generated class structure"
            })
        
        elif generation_type == "test":
            artifacts.update({
                "test_file": f"test_{target}.py",
                "code_sample": f"import pytest\n\ndef test_{target}():\n    assert True",
                "test_count": 1,
                "documentation": "Generated test suite"
            })
        
        else:
            artifacts.update({
                "output": f"Generated code for {target}",
                "specifications_used": specifications
            })
        
        return artifacts

    def get_capabilities(self) -> Dict[str, Any]:
        """Get generator-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps["generation_capabilities"] = self.generation_capabilities
        return base_caps
