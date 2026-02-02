/**
 * MessageBubble - Individual message display component
 * Shows user and assistant messages with different styling
 */
"use client";

import { motion } from "framer-motion";
import { Message } from "@/types/chat";
import { formatDistanceToNow } from "date-fns";
import TaskActionCard from "./TaskActionCard";
import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  // Parse tool_calls if it's a string
  let toolCalls = null;
  if (message.tool_calls) {
    if (typeof message.tool_calls === "string") {
      try {
        toolCalls = JSON.parse(message.tool_calls);
      } catch (e) {
        console.error("Failed to parse tool_calls:", e);
      }
    } else {
      toolCalls = message.tool_calls;
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("flex gap-3 mb-6", isUser ? "justify-end" : "justify-start")}
    >
      {/* Avatar */}
      {isAssistant && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent-purple flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-5 h-5 text-white"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
            />
          </svg>
        </div>
      )}

      {/* Message content */}
      <div className={cn("flex flex-col", isUser ? "items-end" : "items-start", "max-w-[75%]")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-3 shadow-sm transition-all duration-200",
            isUser
              ? "bg-gradient-to-br from-primary to-primary/90 text-primary-foreground rounded-br-sm shadow-primary/20 hover:shadow-md hover:shadow-primary/30"
              : "bg-card border border-border rounded-bl-sm hover:shadow-md"
          )}
        >
          {/* Message text */}
          <div
            className={cn(
              "whitespace-pre-wrap break-words text-sm leading-relaxed",
              isUser ? "text-primary-foreground" : "text-foreground"
            )}
          >
            {message.content}
          </div>

          {/* Tool calls display */}
          {isAssistant && toolCalls && Array.isArray(toolCalls) && (
            <div className="mt-3">
              <TaskActionCard toolCalls={toolCalls} />
            </div>
          )}
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-2 mt-1.5 px-1">
          <span className="text-xs text-foreground-tertiary">
            {formatDistanceToNow(new Date(message.created_at + 'Z'), {
              addSuffix: true,
            })}
          </span>
          {message.tokens_used && message.tokens_used > 0 && (
            <>
              <span className="text-xs text-foreground-tertiary">•</span>
              <span className="text-xs text-foreground-tertiary">
                {message.tokens_used} tokens
              </span>
            </>
          )}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-secondary flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-5 h-5 text-foreground-secondary"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
            />
          </svg>
        </div>
      )}
    </motion.div>
  );
}
