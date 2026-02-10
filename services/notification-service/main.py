"""
Notification Service - Phase V Microservice

Handles task reminders via WebSocket (real-time) and Email (offline fallback).
Consumes reminder events from Kafka via Dapr Pub/Sub.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="1.0.0")


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        """Unregister a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_to_user(self, user_id: str, message: dict) -> bool:
        """
        Send a message to all active connections for a user.

        Returns:
            True if message was sent to at least one connection, False otherwise
        """
        if user_id not in self.active_connections:
            return False

        disconnected = set()
        sent_count = 0

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send message to WebSocket: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(user_id, conn)

        return sent_count > 0

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())


manager = ConnectionManager()


# ============================================================================
# Email Service
# ============================================================================

async def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send email notification using SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (HTML)

    Returns:
        True if email sent successfully, False otherwise
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("FROM_EMAIL", smtp_user)

    if not smtp_user or not smtp_password:
        logger.warning("SMTP credentials not configured, skipping email")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


async def get_user_email(user_id: str) -> str:
    """
    Fetch user email from database.

    TODO: Implement database query to get user email.
    For now, returns None.
    """
    # This would query the database for user email
    # For Phase V, we'll implement this later
    return None


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notifications.

    Clients connect to this endpoint to receive real-time task reminders.
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive by receiving ping messages
            data = await websocket.receive_text()
            # Echo back to confirm connection is alive
            await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(user_id, websocket)


# ============================================================================
# Dapr Subscription Endpoint
# ============================================================================

class ReminderEvent(BaseModel):
    """Reminder event schema from Kafka."""
    event_type: str
    task_id: int
    user_id: str
    reminder_id: int
    task_title: str
    reminder_time: str
    reminder_type: str
    timestamp: str


@app.post("/reminder-events")
async def handle_reminder_event(event: dict):
    """
    Handle reminder events from Kafka via Dapr.

    This endpoint is called by Dapr when a message arrives on the reminder-events topic.
    """
    try:
        # Extract event data
        data = event.get("data", {})

        user_id = data.get("user_id")
        task_title = data.get("task_title")
        reminder_time = data.get("reminder_time")
        reminder_type = data.get("reminder_type", "notification")

        logger.info(f"Processing reminder event for user {user_id}: {task_title}")

        # Create notification message
        notification = {
            "type": "reminder",
            "task_title": task_title,
            "reminder_time": reminder_time,
            "message": f"Reminder: {task_title} is due soon!",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Try WebSocket first (real-time)
        websocket_sent = await manager.send_to_user(user_id, notification)

        # If no active WebSocket connection, send email (fallback)
        if not websocket_sent and reminder_type in ["email", "both"]:
            user_email = await get_user_email(user_id)
            if user_email:
                email_sent = await send_email(
                    to_email=user_email,
                    subject=f"Task Reminder: {task_title}",
                    body=f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #2563eb;">Task Reminder</h2>
                        <p>Your task <strong>{task_title}</strong> is due soon!</p>
                        <p><strong>Due time:</strong> {reminder_time}</p>
                        <p style="margin-top: 20px;">
                            <a href="https://todo-app.example.com/tasks"
                               style="background-color: #2563eb; color: white; padding: 10px 20px;
                                      text-decoration: none; border-radius: 5px;">
                                View Tasks
                            </a>
                        </p>
                        <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                            This is an automated reminder from your Todo App.
                        </p>
                    </body>
                    </html>
                    """
                )
                logger.info(f"Email fallback {'succeeded' if email_sent else 'failed'} for user {user_id}")

        return {
            "status": "processed",
            "websocket_sent": websocket_sent,
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# Dapr Subscription Configuration
# ============================================================================

@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminder-events",
            "route": "/reminder-events"
        }
    ]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "active_connections": manager.get_connection_count(),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Notification Service",
        "version": "1.0.0",
        "description": "Handles task reminders via WebSocket and Email"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
