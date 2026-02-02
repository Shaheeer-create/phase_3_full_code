/**
 * API client with JWT authentication
 *
 * CRITICAL: Automatically adds JWT token to all requests
 * All API calls should use this client to ensure authentication.
 */
import axios, { AxiosError } from "axios";
import { getAccessToken } from "./auth";
import type { Task, TaskCreate, TaskUpdate } from "@/types/task";
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
