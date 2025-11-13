"""Deep Agent - LLM-powered agent with dynamic knowledge graph management."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from .config import DeepAgentConfig
from .neo4j_manager import Neo4jManager
from .knowledge_graph import KnowledgeGraphManager

logger = logging.getLogger(__name__)


class DeepAgent:
    """Deep coding agent with dynamic knowledge graph integration.

    This agent uses Claude to understand conversations and code, and dynamically
    builds a knowledge graph using Neo4j and Graphiti to maintain context and
    understanding across conversations.
    """

    SYSTEM_PROMPT = """You are a deep coding agent with access to a dynamic knowledge graph.
Your role is to:
1. Understand and analyze code and projects deeply
2. Maintain a comprehensive knowledge graph of the project structure, patterns, and relationships
3. Build context from conversations to better understand user needs
4. Identify and extract key entities (functions, classes, modules, patterns, concepts)
5. Create relationships between entities to build a rich understanding

When you receive information, extract:
- Code entities (functions, classes, files, modules)
- Relationships (calls, inherits, imports, depends on)
- Concepts and patterns being discussed
- User goals and intentions
- Project structure and architecture

Always think about what should be added to the knowledge graph to improve future understanding.
"""

    def __init__(
        self,
        config: Optional[DeepAgentConfig] = None,
        neo4j_manager: Optional[Neo4jManager] = None,
        knowledge_graph: Optional[KnowledgeGraphManager] = None,
    ):
        """Initialize the deep agent.

        Args:
            config: Configuration object. If None, loads from environment.
            neo4j_manager: Neo4j manager instance. If None, creates a new one.
            knowledge_graph: Knowledge graph manager. If None, creates a new one.
        """
        self.config = config or DeepAgentConfig()
        self.neo4j_manager = neo4j_manager or Neo4jManager(self.config)
        self.knowledge_graph = knowledge_graph or KnowledgeGraphManager(
            self.neo4j_manager, self.config
        )

        # Initialize Claude if API key is available
        self.llm = None
        if self.config.anthropic_api_key:
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                anthropic_api_key=self.config.anthropic_api_key,
                temperature=0.7,
            )

        self.conversation_history: List[Dict[str, str]] = []
        self.current_project: Optional[str] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the agent and knowledge graph."""
        if not self._initialized:
            await self.knowledge_graph.initialize()
            self._initialized = True
            logger.info("Deep agent initialized")

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user message and update the knowledge graph.

        Args:
            message: User message to process.
            context: Additional context (file paths, code snippets, etc.).

        Returns:
            Dictionary with response and extracted knowledge.
        """
        if not self._initialized:
            await self.initialize()

        # Add message to conversation history
        self.conversation_history.append(
            {"role": "user", "content": message, "timestamp": datetime.utcnow().isoformat()}
        )

        # Add to knowledge graph
        await self.knowledge_graph.add_conversation_episode(content=message, metadata=context or {})

        response = {
            "message": message,
            "entities_extracted": [],
            "relationships_created": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # If Claude is available, use it to analyze the message
        if self.llm:
            try:
                analysis = await self._analyze_with_claude(message, context)
                response.update(analysis)

                # Add response to conversation history
                self.conversation_history.append(
                    {
                        "role": "assistant",
                        "content": analysis.get("response", ""),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

                # Add response to knowledge graph
                await self.knowledge_graph.add_conversation_episode(
                    content=analysis.get("response", ""), metadata={"type": "assistant_response"}
                )

            except Exception as e:
                logger.error(f"Failed to analyze with Claude: {e}")
                response["error"] = str(e)

        # Extract and store entities from context if provided
        if context:
            await self._process_context(context)

        return response

    async def _analyze_with_claude(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Use Claude to analyze the message and extract knowledge.

        Args:
            message: User message.
            context: Additional context.

        Returns:
            Analysis results including entities and relationships.
        """
        # Build context for Claude
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{context}"

        # Recent conversation history
        history_str = ""
        if self.conversation_history[-5:]:
            history_str = "\n\nRecent conversation:\n"
            for msg in self.conversation_history[-5:]:
                history_str += f"{msg['role']}: {msg['content']}\n"

        prompt = f"""Analyze this message and extract key information for the knowledge graph.

Message: {message}{context_str}{history_str}

Extract:
1. Code entities (functions, classes, files) mentioned
2. Relationships between entities
3. Concepts or patterns discussed
4. User's intent or goal

Provide a helpful response and structure your findings."""

        messages = [SystemMessage(content=self.SYSTEM_PROMPT), HumanMessage(content=prompt)]

        response = await self.llm.ainvoke(messages)

        return {"response": response.content, "analysis_completed": True}

    async def _process_context(self, context: Dict[str, Any]) -> None:
        """Process context information and update knowledge graph.

        Args:
            context: Context dictionary with file paths, code, etc.
        """
        # Process file paths
        if "file_path" in context:
            await self.knowledge_graph.add_code_entity(
                entity_type="File",
                name=context["file_path"],
                properties={"path": context["file_path"], "project": self.current_project},
            )

        # Process code snippets
        if "code" in context and "language" in context:
            await self.knowledge_graph.add_code_entity(
                entity_type="CodeSnippet",
                name=f"snippet_{datetime.utcnow().timestamp()}",
                properties={
                    "code": context["code"],
                    "language": context["language"],
                    "project": self.current_project,
                },
            )

    async def set_project(self, project_name: str, description: Optional[str] = None) -> str:
        """Set the current project context.

        Args:
            project_name: Name of the project.
            description: Project description.

        Returns:
            Project ID.
        """
        if not self._initialized:
            await self.initialize()

        self.current_project = project_name
        project_id = await self.knowledge_graph.add_project(
            project_name=project_name, description=description
        )

        logger.info(f"Set current project to: {project_name}")
        return project_id

    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the knowledge graph.

        Args:
            query: Search query.
            limit: Maximum results to return.

        Returns:
            Search results.
        """
        if not self._initialized:
            await self.initialize()

        return await self.knowledge_graph.search_knowledge(query, limit)

    async def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of the current project's knowledge graph.

        Returns:
            Project summary with statistics.
        """
        if not self.current_project:
            return {"error": "No project set"}

        context = await self.knowledge_graph.get_project_context(self.current_project)

        stats = self.neo4j_manager.get_stats()

        return {
            "project": self.current_project,
            "context": context,
            "stats": stats,
            "conversation_length": len(self.conversation_history),
        }

    async def close(self) -> None:
        """Close the agent and cleanup resources."""
        await self.knowledge_graph.close()
        logger.info("Deep agent closed")
