/**
 * Type definitions for chat functionality.
 */

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: "user" | "assistant" | "tool";
  content: string;
  tool_calls?: any;
  tokens_used?: number;
  created_at: string;
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

export interface UserUsage {
  messages_today: number;
  tokens_this_month: number;
  max_messages_per_day: number;
  max_tokens_per_month: number;
  messages_remaining: number;
  tokens_remaining: number;
}

export interface SendMessageRequest {
  content: string;
}

export interface CreateConversationRequest {
  title?: string;
}

export interface UpdateConversationRequest {
  title: string;
}
