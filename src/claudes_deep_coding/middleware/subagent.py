"""
SubAgent Middleware - Manages communication and delegation between agents.
"""

from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import asyncio


class MessageType(str, Enum):
    """Types of messages exchanged between agents."""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    STATUS_UPDATE = "status_update"
    REQUEST_HELP = "request_help"
    DELEGATION = "delegation"
    CANCELLATION = "cancellation"


class AgentMessage(BaseModel):
    """Message structure for inter-agent communication."""
    id: str = Field(description="Unique message identifier")
    from_agent: str = Field(description="Sender agent ID")
    to_agent: str = Field(description="Recipient agent ID")
    message_type: MessageType = Field(description="Type of message")
    payload: Dict[str, Any] = Field(description="Message payload")
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = Field(default=None, description="ID to correlate request/response")


class SubAgentMiddleware:
    """
    Middleware layer for managing subagent communication and delegation.
    Handles message routing, task delegation, and response aggregation.
    """

    def __init__(self):
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.agents: Dict[str, "BaseAgent"] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self._message_counter = 0
        self._running = False

    def register_agent(self, agent_id: str, agent: "BaseAgent"):
        """
        Register an agent with the middleware.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
        """
        self.agents[agent_id] = agent

    def unregister_agent(self, agent_id: str):
        """
        Unregister an agent from the middleware.
        
        Args:
            agent_id: Agent identifier to unregister
        """
        if agent_id in self.agents:
            del self.agents[agent_id]

    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message_type: Type of message
            payload: Message content
            correlation_id: Optional correlation ID for request/response tracking
            
        Returns:
            Message ID
        """
        self._message_counter += 1
        message_id = f"msg_{self._message_counter}"
        
        message = AgentMessage(
            id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id
        )
        
        await self.message_queue.put(message)
        return message_id

    async def delegate_task(
        self,
        orchestrator_id: str,
        agent_id: str,
        task_data: Dict[str, Any]
    ) -> str:
        """
        Delegate a task from the orchestrator to a subagent.
        
        Args:
            orchestrator_id: Orchestrator agent ID
            agent_id: Target subagent ID
            task_data: Task details to delegate
            
        Returns:
            Message ID for the delegation
        """
        return await self.send_message(
            from_agent=orchestrator_id,
            to_agent=agent_id,
            message_type=MessageType.TASK_ASSIGNMENT,
            payload=task_data
        )

    async def report_result(
        self,
        agent_id: str,
        orchestrator_id: str,
        result_data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Report task results from a subagent back to the orchestrator.
        
        Args:
            agent_id: Reporting agent ID
            orchestrator_id: Orchestrator agent ID
            result_data: Results to report
            correlation_id: Correlation ID linking to the original task
            
        Returns:
            Message ID for the result
        """
        return await self.send_message(
            from_agent=agent_id,
            to_agent=orchestrator_id,
            message_type=MessageType.TASK_RESULT,
            payload=result_data,
            correlation_id=correlation_id
        )

    async def broadcast_status(
        self,
        agent_id: str,
        status_data: Dict[str, Any]
    ):
        """
        Broadcast status update to all registered agents.
        
        Args:
            agent_id: Broadcasting agent ID
            status_data: Status information
        """
        for target_id in self.agents.keys():
            if target_id != agent_id:
                await self.send_message(
                    from_agent=agent_id,
                    to_agent=target_id,
                    message_type=MessageType.STATUS_UPDATE,
                    payload=status_data
                )

    def subscribe_to_messages(
        self,
        agent_id: str,
        handler: Callable[[AgentMessage], None]
    ):
        """
        Subscribe an agent to receive messages.
        
        Args:
            agent_id: Agent ID to subscribe
            handler: Callback function to handle messages
        """
        if agent_id not in self.message_handlers:
            self.message_handlers[agent_id] = []
        self.message_handlers[agent_id].append(handler)

    async def start(self):
        """Start the middleware message processing loop."""
        self._running = True
        while self._running:
            try:
                # Wait for message with timeout to allow graceful shutdown
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                await self._process_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")

    async def stop(self):
        """Stop the middleware message processing loop."""
        self._running = False

    async def _process_message(self, message: AgentMessage):
        """
        Process a message by routing it to the appropriate handler.
        
        Args:
            message: Message to process
        """
        handlers = self.message_handlers.get(message.to_agent, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                print(f"Error in message handler: {e}")

    async def request_and_wait(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """
        Send a message and wait for a correlated response.
        
        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message_type: Type of message
            payload: Message content
            timeout: Maximum time to wait for response
            
        Returns:
            Response message or None if timeout
        """
        correlation_id = f"corr_{self._message_counter + 1}"
        response_future = asyncio.Future()
        
        # Set up temporary handler for response
        def response_handler(msg: AgentMessage):
            if msg.correlation_id == correlation_id and msg.from_agent == to_agent:
                if not response_future.done():
                    response_future.set_result(msg)
        
        self.subscribe_to_messages(from_agent, response_handler)
        
        # Send the request
        await self.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id
        )
        
        # Wait for response
        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            return None
