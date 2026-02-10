/**
 * API client with JWT authentication
 *
 * CRITICAL: Automatically adds JWT token to all requests
 * All API calls should use this client to ensure authentication.
 */
import axios, { AxiosError } from "axios";
import { getAccessToken } from "./auth";
import type { Task, TaskCreate, TaskUpdate, TaskSearchParams, RecurringPattern, TaskReminder } from "@/types/task";
import type {
  Conversation,
  ConversationWithMessages,
  Message,
  UserUsage,
  SendMessageRequest,
  CreateConversationRequest,
  UpdateConversationRequest,
} from "@/types/chat";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: Add JWT token to all requests
apiClient.interceptors.request.use(
  async (config) => {
    const token = await getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Task API methods
 */
export const taskApi = {
  /**
   * List all tasks for the authenticated user
   * @param status - Filter by status: "all", "pending", or "completed"
   */
  list: async (status: "all" | "pending" | "completed" = "all"): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>(`/api/tasks?status=${status}`);
    return response.data;
  },

  /**
   * Create a new task
   */
  create: async (data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post<Task>("/api/tasks", data);
    return response.data;
  },

  /**
   * Get a specific task by ID
   */
  get: async (id: number): Promise<Task> => {
    const response = await apiClient.get<Task>(`/api/tasks/${id}`);
    return response.data;
  },

  /**
   * Update a task
   */
  update: async (id: number, data: TaskUpdate): Promise<Task> => {
    const response = await apiClient.put<Task>(`/api/tasks/${id}`, data);
    return response.data;
  },

  /**
   * Toggle task completion status
   */
  toggleComplete: async (id: number): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/api/tasks/${id}/complete`);
    return response.data;
  },

  /**
   * Delete a task
   */
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/tasks/${id}`);
  },

  // ============================================================================
  // Phase V: Advanced Features
  // ============================================================================

  /**
   * Advanced search for tasks with multiple filters
   */
  search: async (params: TaskSearchParams): Promise<Task[]> => {
    const queryParams = new URLSearchParams();

    if (params.q) queryParams.append('q', params.q);
    if (params.priority) queryParams.append('priority', params.priority);
    if (params.tags) queryParams.append('tags', params.tags);
    if (params.due_before) queryParams.append('due_before', params.due_before);
    if (params.due_after) queryParams.append('due_after', params.due_after);
    if (params.status) queryParams.append('status', params.status);
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.sort_order) queryParams.append('sort_order', params.sort_order);

    const response = await apiClient.get<Task[]>(`/api/tasks/search?${queryParams.toString()}`);
    return response.data;
  },

  /**
   * Add tags to a task
   */
  addTags: async (id: number, tags: string[]): Promise<Task> => {
    const response = await apiClient.post<Task>(`/api/tasks/${id}/tags`, { tags });
    return response.data;
  },

  /**
   * Create a reminder for a task
   */
  createReminder: async (
    id: number,
    reminder_time: string,
    reminder_type: 'notification' | 'email' | 'both' = 'notification'
  ): Promise<TaskReminder> => {
    const response = await apiClient.post<TaskReminder>(`/api/tasks/${id}/reminders`, {
      reminder_time,
      reminder_type,
    });
    return response.data;
  },

  /**
   * Set up a recurring pattern for a task
   */
  createRecurringPattern: async (
    id: number,
    pattern: RecurringPattern
  ): Promise<any> => {
    const response = await apiClient.post(`/api/tasks/${id}/recurring`, pattern);
    return response.data;
  },

  /**
   * Get all instances of a recurring task (parent + children)
   */
  getRecurringInstances: async (id: number): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>(`/api/tasks/${id}/instances`);
    return response.data;
  },
};

/**
 * Chat API methods
 */
export const chatApi = {
  /**
   * List all conversations for the authenticated user
   */
  listConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get<Conversation[]>("/api/conversations");
    return response.data;
  },

  /**
   * Create a new conversation
   */
  createConversation: async (
    data: CreateConversationRequest = {}
  ): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>("/api/conversations", data);
    return response.data;
  },

  /**
   * Get a specific conversation with all messages
   */
  getConversation: async (id: number): Promise<ConversationWithMessages> => {
    const response = await apiClient.get<ConversationWithMessages>(
      `/api/conversations/${id}`
    );
    return response.data;
  },

  /**
   * Update conversation title
   */
  updateConversation: async (
    id: number,
    data: UpdateConversationRequest
  ): Promise<Conversation> => {
    const response = await apiClient.patch<Conversation>(
      `/api/conversations/${id}`,
      data
    );
    return response.data;
  },

  /**
   * Delete a conversation and all its messages
   */
  deleteConversation: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/conversations/${id}`);
  },

  /**
   * Get all messages in a conversation
   */
  getMessages: async (conversationId: number): Promise<Message[]> => {
    const response = await apiClient.get<Message[]>(
      `/api/conversations/${conversationId}/messages`
    );
    return response.data;
  },

  /**
   * Send a message and get AI response (non-streaming)
   */
  sendMessage: async (
    conversationId: number,
    content: string
  ): Promise<Message> => {
    const response = await apiClient.post<Message>(
      `/api/conversations/${conversationId}/messages`,
      { content }
    );
    return response.data;
  },

  /**
   * Get current usage statistics
   */
  getUsage: async (): Promise<UserUsage> => {
    const response = await apiClient.get<UserUsage>("/api/usage");
    return response.data;
  },
};
