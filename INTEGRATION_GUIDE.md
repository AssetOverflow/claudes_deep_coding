# Integration Guide: ChromaDB with LangChain and Claude

This guide shows how to integrate the ChromaDB memory system with LangChain and Claude agents for enhanced coding capabilities.

## Overview

The ChromaDB setup provides long-term memory that can be used with:
- **Claude API** - Direct interaction with Claude models
- **LangChain** - Building agent workflows with memory
- **RAG (Retrieval-Augmented Generation)** - Enhancing responses with stored knowledge

## Basic Integration with Claude

### Simple Claude Agent with Memory

```python
import anthropic
from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory

# Initialize memory
chroma_manager = ChromaMemoryManager(
    persist_directory=config.chromadb.persist_directory,
    collection_name=config.chromadb.collection_name,
)
coding_memory = CodingMemory(chroma_manager)

# Initialize Claude client
client = anthropic.Anthropic(api_key=config.anthropic.api_key)

def ask_claude_with_memory(question: str, language: str = "python"):
    """Ask Claude a question, using relevant memory as context."""
    
    # Search for relevant code in memory
    relevant_code = coding_memory.find_similar_code(
        query=question,
        language=language,
        n_results=3,
    )
    
    # Search for relevant tasks
    relevant_tasks = coding_memory.find_similar_tasks(
        query=question,
        n_results=2,
    )
    
    # Build context from memory
    context = "# Relevant information from memory:\n\n"
    
    if relevant_code:
        context += "## Similar code snippets:\n"
        for i, code in enumerate(relevant_code, 1):
            context += f"\n### Example {i}:\n"
            context += f"Description: {code['metadata'].get('description', 'N/A')}\n"
            context += f"```{code['metadata'].get('language', 'python')}\n"
            context += f"{code['document']}\n```\n"
    
    if relevant_tasks:
        context += "\n## Similar past tasks:\n"
        for i, task in enumerate(relevant_tasks, 1):
            context += f"\n### Task {i}:\n"
            context += f"{task['document']}\n"
            if task['metadata'].get('outcomes'):
                context += f"Outcome: {task['metadata']['outcomes']}\n"
    
    # Ask Claude with context
    message = client.messages.create(
        model=config.anthropic.model,
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"{context}\n\n# Question:\n{question}"
            }
        ]
    )
    
    response = message.content[0].text
    return response

# Example usage
response = ask_claude_with_memory(
    "How do I implement a binary search algorithm in Python?"
)
print(response)
```

## Integration with LangChain

### LangChain Agent with ChromaDB Memory

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory

# Initialize memory
chroma_manager = ChromaMemoryManager(
    persist_directory=config.chromadb.persist_directory,
    collection_name=config.chromadb.collection_name,
)
coding_memory = CodingMemory(chroma_manager)

# Initialize Claude with LangChain
llm = ChatAnthropic(
    model=config.anthropic.model,
    anthropic_api_key=config.anthropic.api_key,
)

# Create tools for the agent
def search_code_memory(query: str) -> str:
    """Search for relevant code snippets in memory."""
    results = coding_memory.find_similar_code(query=query, n_results=3)
    if not results:
        return "No relevant code found in memory."
    
    output = "Found relevant code snippets:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['metadata'].get('description', 'No description')}\n"
        output += f"   Language: {result['metadata'].get('language', 'unknown')}\n"
        output += f"   Code:\n{result['document']}\n\n"
    return output

def search_task_memory(query: str) -> str:
    """Search for similar tasks in memory."""
    results = coding_memory.find_similar_tasks(query=query, n_results=3)
    if not results:
        return "No relevant tasks found in memory."
    
    output = "Found similar past tasks:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['document']}\n"
        output += f"   Type: {result['metadata'].get('task_type', 'unknown')}\n"
        if result['metadata'].get('outcomes'):
            output += f"   Outcome: {result['metadata']['outcomes']}\n"
        output += "\n"
    return output

def search_error_memory(query: str) -> str:
    """Search for error solutions in memory."""
    results = coding_memory.find_error_solutions(query=query, n_results=3)
    if not results:
        return "No similar errors found in memory."
    
    output = "Found similar error solutions:\n\n"
    for i, result in enumerate(results, 1):
        output += f"{i}. {result['document']}\n\n"
    return output

def store_code_snippet(code_and_metadata: str) -> str:
    """Store a code snippet in memory. Format: code|||language|||description|||tags"""
    try:
        parts = code_and_metadata.split("|||")
        code = parts[0].strip()
        language = parts[1].strip() if len(parts) > 1 else "python"
        description = parts[2].strip() if len(parts) > 2 else "Code snippet"
        tags_str = parts[3].strip() if len(parts) > 3 else ""
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        
        snippet_id = coding_memory.store_code_snippet(
            code=code,
            language=language,
            description=description,
            tags=tags,
        )
        return f"Stored code snippet with ID: {snippet_id}"
    except Exception as e:
        return f"Error storing code snippet: {str(e)}"

# Define tools
tools = [
    Tool(
        name="SearchCode",
        func=search_code_memory,
        description="Search for relevant code snippets in memory. Use this when you need examples or references to similar code.",
    ),
    Tool(
        name="SearchTasks",
        func=search_task_memory,
        description="Search for similar tasks completed in the past. Use this to learn from previous work.",
    ),
    Tool(
        name="SearchErrors",
        func=search_error_memory,
        description="Search for solutions to similar errors. Use this when encountering errors.",
    ),
    Tool(
        name="StoreCode",
        func=store_code_snippet,
        description="Store a code snippet in memory for future reference. Format: code|||language|||description|||tags",
    ),
]

# Create prompt template
template = """You are a helpful coding assistant with access to long-term memory.

You have access to the following tools:
{tools}

Tool names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template)

# Create agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)

# Use the agent
result = agent_executor.invoke({
    "input": "How do I implement authentication in Python? Search for similar code first."
})
print(result["output"])
```

## RAG Pattern Implementation

### Contextual Code Generation with RAG

```python
from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory
from deepagents.utils import format_code_context
import anthropic

class RAGCodingAgent:
    """Coding agent using RAG pattern with ChromaDB."""
    
    def __init__(self):
        # Initialize memory
        self.chroma_manager = ChromaMemoryManager(
            persist_directory=config.chromadb.persist_directory,
            collection_name=config.chromadb.collection_name,
        )
        self.coding_memory = CodingMemory(self.chroma_manager)
        
        # Initialize Claude
        self.client = anthropic.Anthropic(api_key=config.anthropic.api_key)
    
    def generate_code_with_rag(
        self,
        task_description: str,
        language: str = "python",
        n_examples: int = 3,
    ) -> dict:
        """
        Generate code using RAG pattern.
        
        Steps:
        1. Retrieve relevant examples from memory
        2. Augment the prompt with retrieved examples
        3. Generate code using Claude
        4. Optionally store the result
        """
        # Step 1: Retrieve relevant examples
        print(f"🔍 Searching memory for similar code...")
        similar_code = self.coding_memory.find_similar_code(
            query=task_description,
            language=language,
            n_results=n_examples,
        )
        
        similar_tasks = self.coding_memory.find_similar_tasks(
            query=task_description,
            n_results=2,
        )
        
        # Step 2: Build augmented prompt
        context = self._build_context(similar_code, similar_tasks)
        
        prompt = f"""You are a coding expert. Use the following examples and context from previous work to help you.

{context}

Now, please implement the following:

Task: {task_description}
Language: {language}

Provide clean, well-documented code that follows best practices."""
        
        # Step 3: Generate with Claude
        print(f"🤖 Generating code with Claude...")
        message = self.client.messages.create(
            model=config.anthropic.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        generated_code = message.content[0].text
        
        return {
            "code": generated_code,
            "context": context,
            "similar_examples": len(similar_code),
        }
    
    def _build_context(self, similar_code, similar_tasks):
        """Build context from retrieved information."""
        context = ""
        
        if similar_code:
            context += "# Similar code examples from memory:\n\n"
            for i, code in enumerate(similar_code, 1):
                context += f"## Example {i}:\n"
                context += f"Description: {code['metadata'].get('description', 'N/A')}\n"
                context += f"```{code['metadata'].get('language', 'python')}\n"
                context += f"{code['document']}\n```\n\n"
        
        if similar_tasks:
            context += "# Similar tasks completed:\n\n"
            for i, task in enumerate(similar_tasks, 1):
                context += f"{i}. {task['document']}\n"
                if task['metadata'].get('outcomes'):
                    context += f"   Result: {task['metadata']['outcomes']}\n"
                context += "\n"
        
        return context
    
    def learn_from_code(
        self,
        code: str,
        language: str,
        description: str,
        tags: list = None,
    ):
        """Store code in memory for future learning."""
        print(f"💾 Storing code in memory...")
        snippet_id = self.coding_memory.store_code_snippet(
            code=code,
            language=language,
            description=description,
            tags=tags or [],
        )
        print(f"✅ Stored with ID: {snippet_id}")
        return snippet_id

# Example usage
agent = RAGCodingAgent()

# Generate code with RAG
result = agent.generate_code_with_rag(
    task_description="Implement a function to validate email addresses",
    language="python",
    n_examples=3,
)

print("Generated Code:")
print(result["code"])
print(f"\nUsed {result['similar_examples']} examples from memory")

# Learn from the generated code
agent.learn_from_code(
    code=result["code"],
    language="python",
    description="Email validation function",
    tags=["validation", "email", "regex"],
)
```

## Continuous Learning Pattern

### Agent that Learns from Successes and Failures

```python
from deepagents.config import config
from deepagents.memory import ChromaMemoryManager, CodingMemory
import anthropic

class LearningCodingAgent:
    """Agent that learns from both successes and failures."""
    
    def __init__(self):
        self.chroma_manager = ChromaMemoryManager(
            persist_directory=config.chromadb.persist_directory,
            collection_name=config.chromadb.collection_name,
        )
        self.coding_memory = CodingMemory(self.chroma_manager)
        self.client = anthropic.Anthropic(api_key=config.anthropic.api_key)
    
    def complete_task(self, task_description: str, language: str = "python"):
        """Complete a coding task and learn from the experience."""
        print(f"📋 Task: {task_description}")
        
        # Check memory for similar tasks
        similar_tasks = self.coding_memory.find_similar_tasks(
            query=task_description,
            n_results=3,
        )
        
        if similar_tasks:
            print(f"💡 Found {len(similar_tasks)} similar past tasks")
            for task in similar_tasks:
                print(f"  - {task['document'][:100]}...")
        
        # Generate solution
        try:
            solution = self._generate_solution(task_description, language)
            
            # Test the solution (placeholder)
            success = self._test_solution(solution)
            
            if success:
                print("✅ Task completed successfully!")
                self._record_success(task_description, solution, language)
            else:
                print("❌ Task failed")
                self._record_failure(task_description, solution)
            
            return solution
            
        except Exception as e:
            print(f"💥 Error: {e}")
            self._record_error(task_description, str(e))
            raise
    
    def _generate_solution(self, task: str, language: str) -> str:
        """Generate code solution using Claude."""
        message = self.client.messages.create(
            model=config.anthropic.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"Implement the following in {language}:\n\n{task}"
            }]
        )
        return message.content[0].text
    
    def _test_solution(self, solution: str) -> bool:
        """Test the solution (placeholder)."""
        # In a real implementation, this would run tests
        return True
    
    def _record_success(self, task: str, solution: str, language: str):
        """Record successful task completion."""
        # Store the task
        self.coding_memory.store_task_context(
            task_description=task,
            task_type="completed",
            outcomes="Successfully completed",
        )
        
        # Store the code
        self.coding_memory.store_code_snippet(
            code=solution,
            language=language,
            description=task,
            tags=["successful", "completed"],
        )
    
    def _record_failure(self, task: str, attempted_solution: str):
        """Record failed attempt for learning."""
        self.coding_memory.store_task_context(
            task_description=task,
            task_type="failed",
            outcomes="Failed - needs retry",
        )
    
    def _record_error(self, task: str, error: str):
        """Record error for future reference."""
        # Check if we've seen this error before
        similar_errors = self.coding_memory.find_error_solutions(
            error_query=error,
            n_results=1,
        )
        
        if similar_errors:
            print(f"💡 Found similar error in memory!")
            print(f"   Previous solution: {similar_errors[0]['document']}")

# Example usage
agent = LearningCodingAgent()

# Complete a task
agent.complete_task(
    task_description="Create a function to parse JSON and handle errors gracefully",
    language="python",
)
```

## Best Practices

1. **Always search before generating**: Check memory for similar code/tasks
2. **Store both successes and failures**: Learn from everything
3. **Use descriptive metadata**: Better metadata = better retrieval
4. **Regular cleanup**: Periodically review and update stored memories
5. **Context window management**: Don't overload Claude with too many examples

## Advanced Tips

- **Hybrid search**: Combine semantic search with metadata filters
- **Iterative refinement**: Use memory to improve across multiple attempts
- **Domain-specific collections**: Create separate collections for different projects
- **Feedback loops**: Store user corrections to improve future responses

## Next Steps

- Explore the [ChromaDB Setup Documentation](CHROMADB_SETUP.md)
- Check out the [examples](examples/) directory
- Read about [LangChain integrations](https://python.langchain.com/docs/integrations/vectorstores/chroma)
