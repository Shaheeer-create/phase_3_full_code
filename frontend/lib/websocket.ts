/**
 * WebSocket Client for Real-Time Notifications - Phase V
 *
 * Connects to the Notification Service to receive real-time task reminders.
 */

interface NotificationMessage {
  type: 'reminder' | 'pong';
  task_title?: string;
  reminder_time?: string;
  message?: string;
  timestamp: string;
}

type NotificationHandler = (notification: NotificationMessage) => void;

export class NotificationWebSocket {
  private ws: WebSocket | null = null;
  private userId: string;
  private wsUrl: string;
  private handlers: Set<NotificationHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 5000; // 5 seconds
  private pingInterval: NodeJS.Timeout | null = null;

  constructor(userId: string) {
    this.userId = userId;
    // Use environment variable or default to localhost
    const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002';
    this.wsUrl = `${wsBaseUrl}/ws/${userId}`;
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;

        // Start ping interval to keep connection alive
        this.startPingInterval();

        // Request browser notification permission
        this.requestNotificationPermission();
      };

      this.ws.onmessage = (event) => {
        try {
          const notification: NotificationMessage = JSON.parse(event.data);

          // Handle different message types
          if (notification.type === 'reminder') {
            this.handleReminder(notification);
          } else if (notification.type === 'pong') {
            // Connection is alive
            console.log('Received pong from server');
          }

          // Notify all registered handlers
          this.handlers.forEach(handler => handler(notification));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.stopPingInterval();

        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
          console.error('Max reconnection attempts reached');
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    this.stopPingInterval();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Register a notification handler
   */
  onNotification(handler: NotificationHandler): () => void {
    this.handlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.handlers.delete(handler);
    };
  }

  /**
   * Handle reminder notification
   */
  private handleReminder(notification: NotificationMessage): void {
    const { task_title, message } = notification;

    // Show browser notification if permission granted
    if (Notification.permission === 'granted' && task_title) {
      new Notification('Task Reminder', {
        body: message || `Reminder: ${task_title} is due soon!`,
        icon: '/icon.png',
        badge: '/badge.png',
        tag: `reminder-${task_title}`,
        requireInteraction: false,
      });
    }

    // Play notification sound (optional)
    this.playNotificationSound();
  }

  /**
   * Request browser notification permission
   */
  private async requestNotificationPermission(): Promise<void> {
    if (!('Notification' in window)) {
      console.warn('Browser does not support notifications');
      return;
    }

    if (Notification.permission === 'default') {
      try {
        const permission = await Notification.requestPermission();
        console.log('Notification permission:', permission);
      } catch (error) {
        console.error('Failed to request notification permission:', error);
      }
    }
  }

  /**
   * Play notification sound
   */
  private playNotificationSound(): void {
    try {
      const audio = new Audio('/notification.mp3');
      audio.volume = 0.5;
      audio.play().catch(error => {
        console.warn('Failed to play notification sound:', error);
      });
    } catch (error) {
      console.warn('Notification sound not available:', error);
    }
  }

  /**
   * Start ping interval to keep connection alive
   */
  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send('ping');
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping interval
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton instance management
let notificationClient: NotificationWebSocket | null = null;

/**
 * Get or create the notification WebSocket client
 */
export function getNotificationClient(userId: string): NotificationWebSocket {
  if (!notificationClient || notificationClient['userId'] !== userId) {
    // Disconnect old client if exists
    if (notificationClient) {
      notificationClient.disconnect();
    }

    // Create new client
    notificationClient = new NotificationWebSocket(userId);
  }

  return notificationClient;
}

/**
 * Disconnect and cleanup the notification client
 */
export function disconnectNotificationClient(): void {
  if (notificationClient) {
    notificationClient.disconnect();
    notificationClient = null;
  }
}
