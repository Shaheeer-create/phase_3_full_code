/**
 * ChatInterface - Main chat interface component
 * Manages conversation state, message sending, and streaming
 */
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Message } from "@/types/chat";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import { streamChatResponse } from "@/lib/streaming";

interface ChatInterfaceProps {
  conversationId: number | null;
  messages: Message[];
  onMessagesUpdate: () => void;
}

export default function ChatInterface({
  conversationId,
  messages,
  onMessagesUpdate,
}: ChatInterfaceProps) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = async (content: string) => {
    if (!conversationId) {
      setError("No conversation selected");
      return;
    }

    setError(null);
    setIsStreaming(true);
    setStreamingContent("");

    try {
      await streamChatResponse(
        conversationId,
        content,
        // onToken callback
        (token: string) => {
          setStreamingContent((prev) => prev + token);
        },
        // onComplete callback
        (fullMessage: string) => {
          setIsStreaming(false);
          setStreamingContent("");
          // Refresh messages from server
          onMessagesUpdate();
        },
        // onError callback
        (error: Error) => {
          setIsStreaming(false);
          setStreamingContent("");
          setError(error.message);
        }
      );
    } catch (err) {
      setIsStreaming(false);
      setStreamingContent("");
      setError(err instanceof Error ? err.message : "Failed to send message");
    }
  };

  if (!conversationId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center max-w-md px-6"
        >
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-accent-purple mx-auto mb-6 flex items-center justify-center glow-primary">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-10 h-10 text-white"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"
              />
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-foreground mb-2">
            No conversation selected
          </h3>
          <p className="text-sm text-foreground-secondary">
            Select a conversation from the sidebar or create a new one to start chatting with your AI assistant
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-error/10 border-b border-error/20 p-4"
          >
            <div className="flex items-center justify-between container mx-auto max-w-4xl px-6">
              <div className="flex items-center gap-3 text-error">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-5 h-5 flex-shrink-0"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                  />
                </svg>
                <span className="text-sm font-medium">{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-error hover:text-error/80 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages */}
      <MessageList
        messages={messages}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
      />

      {/* Input */}
      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={isStreaming}
        placeholder={
          isStreaming
            ? "AI is thinking..."
            : "Ask me anything about your tasks..."
        }
      />
    </div>
  );
}
