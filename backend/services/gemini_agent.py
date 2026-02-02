"""
Gemini AI agent service with function calling for task management.
Uses the new google-genai package with proper function calling API.
"""
from google import genai
from google.genai import types
from typing import List, Dict, Any
from config import settings

# Initialize Gemini client
client = genai.Client(api_key=settings.gemini_api_key)

# Define tools as function declarations
TASK_FUNCTIONS = [
    types.FunctionDeclaration(
        name="create_task",
        description="Create a new task for the user",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "title": types.Schema(
                    type=types.Type.STRING,
                    description="The title of the task"
                ),
                "description": types.Schema(
                    type=types.Type.STRING,
                    description="Optional detailed description of the task"
                )
            },
            required=["title"]
        )
    ),
    types.FunctionDeclaration(
        name="list_tasks",
        description="List the user's tasks, optionally filtered by status",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "status": types.Schema(
                    type=types.Type.STRING,
                    enum=["all", "pending", "completed"],
                    description="Filter tasks by status: 'all', 'pending', or 'completed'"
                )
            }
        )
    ),
    types.FunctionDeclaration(
        name="update_task",
        description="Update an existing task's properties",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "task_id": types.Schema(
                    type=types.Type.INTEGER,
                    description="The ID of the task to update"
                ),
                "title": types.Schema(
                    type=types.Type.STRING,
                    description="New title for the task"
                ),
                "description": types.Schema(
                    type=types.Type.STRING,
                    description="New description for the task"
                ),
                "completed": types.Schema(
                    type=types.Type.BOOLEAN,
                    description="Mark task as completed (true) or pending (false)"
                )
            },
            required=["task_id"]
        )
    ),
    types.FunctionDeclaration(
        name="delete_task",
        description="Delete a task permanently",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "task_id": types.Schema(
                    type=types.Type.INTEGER,
                    description="The ID of the task to delete"
                )
            },
            required=["task_id"]
        )
    )
]


async def generate_response(
    messages: List[Dict[str, str]],
    user_id: str,
    session: Any
) -> Dict[str, Any]:
    """
    Generate a response from the Gemini agent with function calling.

    Args:
        messages: Conversation history
        user_id: Current user ID for tool execution
        session: Database session for tool execution

    Returns:
        Dict with response content and metadata
    """
    from services.task_tools import execute_tool

    # Convert messages to Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    # Generate response with tools
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            tools=[types.Tool(function_declarations=TASK_FUNCTIONS)]
        )
    )

    # Handle function calls
    tool_results = []
    final_response = ""

    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                final_response += part.text
            elif hasattr(part, 'function_call') and part.function_call:
                # Execute the tool
                function_call = part.function_call
                tool_name = function_call.name
                tool_args = dict(function_call.args)

                tool_result = await execute_tool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    user_id=user_id,
                    session=session
                )

                tool_results.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": tool_result
                })

                # Send tool result back to model
                contents.append(response.candidates[0].content)
                contents.append(types.Content(
                    parts=[types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_name,
                            response={"result": tool_result}
                        )
                    )]
                ))

                # Get follow-up response
                follow_up = client.models.generate_content(
                    model=settings.gemini_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=settings.gemini_temperature,
                        max_output_tokens=settings.gemini_max_tokens,
                        tools=[types.Tool(function_declarations=TASK_FUNCTIONS)]
                    )
                )

                if follow_up.candidates and follow_up.candidates[0].content.parts:
                    for follow_part in follow_up.candidates[0].content.parts:
                        if follow_part.text:
                            final_response += follow_part.text

    # Count tokens (approximate)
    tokens_used = len(" ".join([m["content"] for m in messages]).split()) + len(final_response.split())

    return {
        "content": final_response,
        "tool_calls": tool_results if tool_results else None,
        "tokens_used": tokens_used
    }


async def stream_response(
    messages: List[Dict[str, str]],
    user_id: str,
    session: Any
):
    """
    Stream response tokens from Gemini agent with function calling.

    Args:
        messages: Conversation history
        user_id: Current user ID for tool execution
        session: Database session for tool execution

    Yields:
        Dict with token content or tool execution results
    """
    from services.task_tools import execute_tool

    # Convert messages to Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    # Stream response with tools
    full_response = ""
    tool_calls = []

    stream = client.models.generate_content_stream(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            tools=[types.Tool(function_declarations=TASK_FUNCTIONS)]
        )
    )

    for chunk in stream:
        if chunk.candidates and chunk.candidates[0].content.parts:
            for part in chunk.candidates[0].content.parts:
                if part.text:
                    full_response += part.text
                    yield {
                        "type": "token",
                        "content": part.text
                    }
                elif hasattr(part, 'function_call') and part.function_call:
                    # Execute the tool
                    function_call = part.function_call
                    tool_name = function_call.name
                    tool_args = dict(function_call.args)

                    tool_result = await execute_tool(
                        tool_name=tool_name,
                        tool_args=tool_args,
                        user_id=user_id,
                        session=session
                    )

                    tool_calls.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": tool_result
                    })

                    yield {
                        "type": "tool_call",
                        "tool": tool_name,
                        "result": tool_result
                    }

                    # Send tool result back and continue streaming
                    contents.append(chunk.candidates[0].content)
                    contents.append(types.Content(
                        parts=[types.Part(
                            function_response=types.FunctionResponse(
                                name=tool_name,
                                response={"result": tool_result}
                            )
                        )]
                    ))

                    follow_stream = client.models.generate_content_stream(
                        model=settings.gemini_model,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            temperature=settings.gemini_temperature,
                            max_output_tokens=settings.gemini_max_tokens,
                            tools=[types.Tool(function_declarations=TASK_FUNCTIONS)]
                        )
                    )

                    for follow_chunk in follow_stream:
                        if follow_chunk.candidates and follow_chunk.candidates[0].content.parts:
                            for follow_part in follow_chunk.candidates[0].content.parts:
                                if follow_part.text:
                                    full_response += follow_part.text
                                    yield {
                                        "type": "token",
                                        "content": follow_part.text
                                    }

    # Return final metadata
    tokens_used = len(" ".join([m["content"] for m in messages]).split()) + len(full_response.split())
    yield {
        "type": "complete",
        "full_response": full_response,
        "tool_calls": tool_calls if tool_calls else None,
        "tokens_used": tokens_used
    }


async def generate_conversation_title(first_message: str) -> str:
    """
    Generate a short title from the first message in a conversation.

    Args:
        first_message: The first user message

    Returns:
        A short 3-5 word title
    """
    prompt = f"""Generate a short, descriptive title (3-5 words maximum) for a conversation that starts with this message:

"{first_message}"

Respond with ONLY the title, nothing else."""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[types.Content(parts=[types.Part(text=prompt)])],
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=50,
        )
    )

    title = ""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                title += part.text

    title = title.strip().strip('"').strip("'")

    # Ensure title is not too long
    if len(title) > 50:
        title = title[:47] + "..."

    return title if title else "New Conversation"
