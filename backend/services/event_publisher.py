"""
Event Publisher Service for Kafka integration via Dapr.

Publishes task events to Kafka topics for consumption by microservices.
"""
import httpx
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes events to Kafka via Dapr Pub/Sub."""

    def __init__(self):
        self.dapr_http_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.dapr_url = f"http://localhost:{self.dapr_http_port}"
        self.pubsub_name = "kafka-pubsub"

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Publish a task event to the task-events topic.

        Args:
            event_type: Type of event (task.created, task.updated, task.deleted, task.completed)
            task_id: Task ID
            user_id: User ID
            task_data: Task data dictionary

        Returns:
            True if published successfully, False otherwise
        """
        event = {
            "event_type": event_type,
            "task_id": task_id,
            "user_id": user_id,
            "task_data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self._publish("task-events", event)

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: str,
        reminder_id: int,
        task_title: str,
        reminder_time: str,
        reminder_type: str
    ) -> bool:
        """
        Publish a reminder event to the reminder-events topic.

        Args:
            task_id: Task ID
            user_id: User ID
            reminder_id: Reminder ID
            task_title: Task title
            reminder_time: When the reminder is due
            reminder_type: Type of reminder (notification, email, both)

        Returns:
            True if published successfully, False otherwise
        """
        event = {
            "event_type": "reminder.due",
            "task_id": task_id,
            "user_id": user_id,
            "reminder_id": reminder_id,
            "task_title": task_title,
            "reminder_time": reminder_time,
            "reminder_type": reminder_type,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self._publish("reminder-events", event)

    async def publish_recurring_event(
        self,
        parent_task_id: int,
        user_id: str,
        recurring_pattern: Dict[str, Any],
        next_occurrence_date: str
    ) -> bool:
        """
        Publish a recurring task event to the recurring-events topic.

        Args:
            parent_task_id: Parent task ID
            user_id: User ID
            recurring_pattern: Recurring pattern configuration
            next_occurrence_date: When the next instance should be created

        Returns:
            True if published successfully, False otherwise
        """
        event = {
            "event_type": "recurring.generate",
            "parent_task_id": parent_task_id,
            "user_id": user_id,
            "recurring_pattern": recurring_pattern,
            "next_occurrence_date": next_occurrence_date,
            "timestamp": datetime.utcnow().isoformat()
        }

        return await self._publish("recurring-events", event)

    async def _publish(self, topic: str, event: Dict[str, Any]) -> bool:
        """
        Internal method to publish event to Dapr.

        Args:
            topic: Kafka topic name
            event: Event data

        Returns:
            True if published successfully, False otherwise
        """
        url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=event,
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                )

                if response.status_code == 200:
                    logger.info(f"Published event to {topic}: {event['event_type']}")
                    return True
                else:
                    logger.error(f"Failed to publish event to {topic}: {response.status_code} - {response.text}")
                    return False

        except httpx.RequestError as e:
            logger.error(f"Error publishing event to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event to {topic}: {e}")
            return False


# Singleton instance
event_publisher = EventPublisher()
