"""
Example usage of the Deep Agent with knowledge graph integration.

This example demonstrates how to:
1. Initialize a deep agent
2. Set up a project
3. Process conversations
4. Query the knowledge graph
"""

import asyncio
import logging
from deepagents import DeepAgent, DeepAgentConfig

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Main example function."""

    # Initialize the deep agent
    logger.info("Initializing deep agent...")
    config = DeepAgentConfig()
    agent = DeepAgent(config=config)

    try:
        # Initialize the agent
        await agent.initialize()
        logger.info("Agent initialized successfully")

        # Set up a project
        project_id = await agent.set_project(
            project_name="example_project",
            description="An example Python project for testing the deep agent",
        )
        logger.info(f"Project created with ID: {project_id}")

        # Simulate a conversation about code
        conversations = [
            {
                "message": "I'm working on a Python web application using FastAPI",
                "context": {"language": "python", "framework": "fastapi"},
            },
            {
                "message": "I need to create a user authentication system with JWT tokens",
                "context": {"feature": "authentication", "technology": "jwt"},
            },
            {
                "message": "The authentication should support OAuth2 password flow",
                "context": {"auth_type": "oauth2", "flow": "password"},
            },
        ]

        # Process each conversation
        for conv in conversations:
            logger.info(f"Processing message: {conv['message'][:50]}...")
            response = await agent.process_message(
                message=conv["message"], context=conv.get("context")
            )
            logger.info(f"Response received at: {response['timestamp']}")

        # Add some code entities
        logger.info("Adding code entities to knowledge graph...")

        await agent.knowledge_graph.add_code_entity(
            entity_type="File",
            name="main.py",
            properties={
                "path": "/src/main.py",
                "language": "python",
                "description": "Main application entry point",
            },
        )

        await agent.knowledge_graph.add_code_entity(
            entity_type="Class",
            name="UserAuthService",
            properties={
                "file": "main.py",
                "description": "Handles user authentication",
                "methods": ["login", "logout", "refresh_token"],
            },
            relationships=[{"target_name": "main.py", "relationship_type": "DEFINED_IN"}],
        )

        await agent.knowledge_graph.add_code_entity(
            entity_type="Function",
            name="create_access_token",
            properties={
                "file": "main.py",
                "description": "Creates JWT access tokens",
                "parameters": ["user_id", "expires_delta"],
            },
            relationships=[{"target_name": "UserAuthService", "relationship_type": "USED_BY"}],
        )

        # Search the knowledge graph
        logger.info("Searching knowledge graph...")
        search_results = await agent.search_knowledge(query="authentication JWT tokens", limit=5)
        logger.info(f"Found {len(search_results)} results")

        # Get project summary
        logger.info("Getting project summary...")
        summary = await agent.get_project_summary()
        logger.info(f"Project: {summary['project']}")
        logger.info(f"Stats: {summary['stats']}")
        logger.info(f"Conversation messages: {summary['conversation_length']}")

        # Display knowledge graph stats
        stats = agent.neo4j_manager.get_stats()
        logger.info(
            f"Knowledge Graph - Nodes: {stats['nodes']}, Relationships: {stats['relationships']}"
        )

    except Exception as e:
        logger.error(f"Error in example: {e}", exc_info=True)
    finally:
        # Clean up
        await agent.close()
        logger.info("Agent closed")


if __name__ == "__main__":
    asyncio.run(main())
