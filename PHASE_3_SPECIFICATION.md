# Phase 3: AI Chatbot Integration - Specification

## Overview

Phase 3 adds an **AI-powered chatbot** to the Todo App, allowing users to manage tasks through natural language conversations using the OpenAI Agents SDK.

## What Phase 3 Adds

### Core Features

1. **AI Chat Interface**
   - Chat with AI assistant about tasks
   - Natural language task management
   - Conversational UI with message history
   - Real-time streaming responses

2. **Natural Language Task Operations**
   - Create tasks: "Create a task to finish the report by Friday"
   - Update tasks: "Mark the documentation task as complete"
   - Delete tasks: "Delete all completed tasks from last week"
   - Query tasks: "What tasks do I have due this week?"
   - Prioritize: "What should I work on next?"

3. **AI Task Insights**
   - Task suggestions based on patterns
   - Deadline reminders
   - Priority recommendations
   - Productivity insights
   - Task breakdown suggestions

4. **Conversation Management**
   - Multiple conversation threads
   - Conversation history
   - Search conversations
   - Delete conversations

---

## Architecture Changes

### Current (Phase 2)
```
User → Frontend (Next.js) → Backend (FastAPI) → Database (Neon)
                              ↓
                         JWT Auth
```

### Phase 3 Addition
```
User → Frontend (Next.js) → Backend (FastAPI) → Database (Neon)
                              ↓                    ↓
                         JWT Auth          Conversations
                              ↓                    ↓
                         OpenAI Agents SDK    Messages
                              ↓
                         Task Operations
```

---

## Database Schema (Already Provided)

### New Tables

**conversations**
```sql
- id: UUID (PK)
- title: VARCHAR(255)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- user_id: UUID (FK → users.id)
```

**messages**
```sql
- id: UUID (PK)
- content: TEXT
- role: VARCHAR(20) -- 'user', 'assistant', 'system'
- created_at: TIMESTAMP
- conversation_id: UUID (FK → conversations.id)
```

---

## API Endpoints (New)

### Conversation Endpoints

```
POST   /api/conversations              - Create new conversation
GET    /api/conversations              - List user's conversations
GET    /api/conversations/{id}         - Get conversation with messages
PATCH  /api/conversations/{id}         - Update conversation title
DELETE /api/conversations/{id}         - Delete conversation
```

### Message Endpoints

```
POST   /api/conversations/{id}/messages - Send message to AI
GET    /api/conversations/{id}/messages - Get conversation messages
POST   /api/conversations/{id}/stream   - Stream AI response (SSE)
```

### AI Agent Endpoints

```
POST   /api/ai/chat                    - Direct chat with AI (no conversation)
POST   /api/ai/task-suggestions        - Get AI task suggestions
POST   /api/ai/analyze-tasks           - Get productivity insights
```

---

## Frontend Components (New)

### Pages

```
app/
├── chat/
│   ├── page.tsx                       - Chat interface (main)
│   └── [conversationId]/
│       └── page.tsx                   - Specific conversation
└── tasks/
    └── page.tsx                       - Tasks page (existing, enhanced)
```

### Components

```
components/
├── chat/
│   ├── ChatInterface.tsx              - Main chat UI
│   ├── MessageList.tsx                - Display messages
│   ├── MessageInput.tsx               - Input with send button
│   ├── ConversationList.tsx           - Sidebar with conversations
│   ├── ConversationItem.tsx           - Single conversation preview
│   ├── StreamingMessage.tsx           - Animated streaming response
│   └── TaskActionCard.tsx             - Show task created/updated by AI
└── ai/
    ├── TaskSuggestions.tsx            - AI task suggestions widget
    ├── ProductivityInsights.tsx       - AI insights dashboard
    └── QuickActions.tsx               - Quick AI actions
```

---

## Tech Stack Additions

### Backend

```python
# New dependencies
openai>=1.0.0                  # OpenAI SDK
openai-agents-sdk>=0.1.0       # OpenAI Agents SDK
sse-starlette>=1.6.0           # Server-Sent Events for streaming
```

### Frontend

```typescript
// New dependencies
@ai-sdk/openai                 // Vercel AI SDK for OpenAI
ai                             // Vercel AI SDK core
eventsource-parser             // Parse SSE streams
```

---

## OpenAI Agents SDK Integration

### Agent Configuration

```python
# backend/app/services/ai_agent.py
from openai import OpenAI
from openai_agents import Agent, Tool

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Define tools for the agent
tools = [
    Tool(
        name="create_task",
        description="Create a new task for the user",
        parameters={
            "title": "string",
            "description": "string",
            "priority": "low|medium|high",
            "due_date": "ISO 8601 datetime"
        }
    ),
    Tool(
        name="list_tasks",
        description="List user's tasks with optional filters",
        parameters={
            "completed": "boolean",
            "priority": "low|medium|high"
        }
    ),
    Tool(
        name="update_task",
        description="Update an existing task",
        parameters={
            "task_id": "UUID",
            "title": "string",
            "completed": "boolean",
            "priority": "low|medium|high"
        }
    ),
    Tool(
        name="delete_task",
        description="Delete a task",
        parameters={
            "task_id": "UUID"
        }
    )
]

# Create agent
agent = Agent(
    name="TaskAssistant",
    instructions="""
    You are a helpful task management assistant.
    Help users manage their tasks through natural conversation.
    Be concise, friendly, and proactive in suggesting task improvements.
    """,
    tools=tools,
    model="gpt-4-turbo-preview"
)
```

### Agent Execution

```python
# backend/app/routers/ai.py
@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: UUID,
    message: MessageCreate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # Save user message
    user_message = Message(
        content=message.content,
        role="user",
        conversation_id=conversation_id
    )
    session.add(user_message)
    session.commit()

    # Get conversation history
    messages = get_conversation_messages(conversation_id, session)

    # Run agent
    response = await agent.run(
        messages=messages,
        user_id=str(user_id),
        session=session  # Pass session for tool execution
    )

    # Save assistant message
    assistant_message = Message(
        content=response.content,
        role="assistant",
        conversation_id=conversation_id
    )
    session.add(assistant_message)
    session.commit()

    return assistant_message
```

---

## User Flows

### Flow 1: Create Task via Chat

```
User: "Create a task to finish the project report by Friday"
  ↓
AI Agent: Parses intent → Calls create_task tool
  ↓
Backend: Creates task in database
  ↓
AI Agent: "I've created a task 'Finish project report' with a due date of
          Friday, January 31st. Would you like me to set a priority?"
  ↓
User: "Yes, make it high priority"
  ↓
AI Agent: Updates task → "Done! The task is now marked as high priority."
```

### Flow 2: Query Tasks

```
User: "What tasks do I have due this week?"
  ↓
AI Agent: Calls list_tasks tool with date filter
  ↓
Backend: Returns filtered tasks
  ↓
AI Agent: "You have 3 tasks due this week:
          1. Finish project report (High priority, due Friday)
          2. Review pull requests (Medium priority, due Thursday)
          3. Team meeting prep (Low priority, due Wednesday)"
```

### Flow 3: Get AI Suggestions

```
User: "What should I work on next?"
  ↓
AI Agent: Analyzes tasks (priority, due dates, completion status)
  ↓
AI Agent: "Based on your tasks, I recommend:
          1. Start with 'Finish project report' (high priority, due Friday)
          2. Then 'Review pull requests' (due tomorrow)
          3. Consider breaking down the report into smaller tasks"
```

---

## Implementation Plan

### Phase 3A: Basic Chat (Week 1)

**Backend:**
- [ ] Add conversations and messages tables (SQL already provided)
- [ ] Create conversation CRUD endpoints
- [ ] Create message endpoints
- [ ] Integrate OpenAI API (basic chat)

**Frontend:**
- [ ] Create chat page
- [ ] Build ChatInterface component
- [ ] Build MessageList and MessageInput
- [ ] Display conversations sidebar

**Success Criteria:**
- Users can create conversations
- Users can send messages and get AI responses
- Conversation history persists

### Phase 3B: Task Integration (Week 2)

**Backend:**
- [ ] Implement OpenAI Agents SDK
- [ ] Create task operation tools
- [ ] Connect agent to task database
- [ ] Add tool execution logic

**Frontend:**
- [ ] Show task actions in chat (created/updated tasks)
- [ ] Add quick actions (create task from chat)
- [ ] Link tasks mentioned in chat

**Success Criteria:**
- AI can create tasks via natural language
- AI can query and update tasks
- Task operations reflected in UI

### Phase 3C: Streaming & Insights (Week 3)

**Backend:**
- [ ] Implement SSE for streaming responses
- [ ] Add task analysis endpoint
- [ ] Add suggestion generation

**Frontend:**
- [ ] Implement streaming message display
- [ ] Add task suggestions widget
- [ ] Add productivity insights dashboard

**Success Criteria:**
- Responses stream in real-time
- AI provides helpful suggestions
- Users see productivity insights

---

## Success Criteria (Phase 3 Complete)

### Functional Requirements
- [ ] Users can chat with AI assistant
- [ ] AI can create tasks from natural language
- [ ] AI can update and delete tasks
- [ ] AI can query tasks with filters
- [ ] AI provides task suggestions
- [ ] AI provides productivity insights
- [ ] Conversation history persists
- [ ] Multiple conversations supported
- [ ] Responses stream in real-time

### Non-Functional Requirements
- [ ] AI responses < 3 seconds (non-streaming)
- [ ] Streaming starts < 500ms
- [ ] Conversations load < 1 second
- [ ] User data isolation maintained
- [ ] OpenAI API errors handled gracefully
- [ ] Rate limiting implemented

### User Experience
- [ ] Chat interface intuitive
- [ ] Task actions clearly shown
- [ ] Suggestions helpful and relevant
- [ ] Mobile responsive
- [ ] Accessible (WCAG AA)

---

## Cost Considerations

### OpenAI API Costs

**GPT-4 Turbo:**
- Input: $0.01 per 1K tokens
- Output: $0.03 per 1K tokens

**Estimated Monthly Cost (per user):**
- 100 messages/month
- ~500 tokens per message
- ~50K tokens/month
- **Cost: ~$1.50/user/month**

**Optimization Strategies:**
1. Use GPT-3.5-turbo for simple queries ($0.0005/$0.0015 per 1K tokens)
2. Cache conversation context
3. Limit conversation history length
4. Implement rate limiting

---

## Security Considerations

1. **API Key Protection**
   - Store OpenAI API key in environment variables
   - Never expose in frontend
   - Rotate keys regularly

2. **User Data Isolation**
   - Agent can only access user's own tasks
   - Pass user_id to all tool functions
   - Validate permissions in tool execution

3. **Input Validation**
   - Sanitize user messages
   - Validate tool parameters
   - Prevent prompt injection

4. **Rate Limiting**
   - Limit messages per user per hour
   - Limit conversations per user
   - Prevent API abuse

---

## Testing Strategy

### Unit Tests
- Test tool functions (create_task, list_tasks, etc.)
- Test message parsing
- Test conversation CRUD

### Integration Tests
- Test agent with mock OpenAI responses
- Test tool execution with database
- Test streaming responses

### E2E Tests
- Test complete chat flow
- Test task creation via chat
- Test conversation management

---

## Deployment Considerations

### Environment Variables

```bash
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

### Monitoring

- Track OpenAI API usage
- Monitor response times
- Log agent tool calls
- Alert on errors

---

## Future Enhancements (Phase 4+)

1. **Voice Interface**
   - Speech-to-text input
   - Text-to-speech responses

2. **Advanced AI Features**
   - Task auto-scheduling
   - Smart reminders
   - Habit tracking
   - Goal setting

3. **Integrations**
   - Calendar sync
   - Email integration
   - Slack notifications

4. **Collaboration**
   - Shared tasks
   - Team conversations
   - Task assignments

---

## Summary

**Phase 3 transforms the Todo App from a task manager into an AI-powered productivity assistant.**

**Key Additions:**
- ✅ AI chatbot with natural language understanding
- ✅ Conversational task management
- ✅ Task insights and suggestions
- ✅ Streaming responses
- ✅ Conversation history

**Technical Stack:**
- OpenAI Agents SDK
- Server-Sent Events (SSE)
- Vercel AI SDK (frontend)
- New database tables (conversations, messages)

**Timeline:** 3 weeks for full implementation

**Cost:** ~$1.50/user/month for OpenAI API

Ready to start Phase 3? 🚀
