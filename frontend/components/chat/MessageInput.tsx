/**
 * MessageInput - Input form for sending messages
 * Auto-resizing textarea with send button
 */
"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function MessageInput({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message...",
}: MessageInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Enter (without Shift)
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-border bg-background/80 backdrop-blur-xl">
      <form onSubmit={handleSubmit} className="container mx-auto px-6 py-4 max-w-4xl">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className={cn(
                "w-full resize-none rounded-xl border border-border bg-card px-4 py-3 pr-12",
                "text-sm text-foreground placeholder:text-foreground-tertiary",
                "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent",
                "disabled:bg-muted disabled:cursor-not-allowed",
                "max-h-32 overflow-y-auto transition-all"
              )}
            />
            <div className="absolute right-3 bottom-3 text-xs text-foreground-tertiary">
              {message.length}
            </div>
          </div>
          <Button
            type="submit"
            variant="gradient"
            size="lg"
            disabled={disabled || !message.trim()}
            isLoading={disabled}
            className="flex-shrink-0 shadow-lg hover:shadow-xl transition-all hover:scale-105"
          >
            {disabled ? (
              "Sending..."
            ) : (
              <>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
                  />
                </svg>
              </>
            )}
          </Button>
        </div>
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-2 flex items-center justify-between text-xs text-foreground-tertiary"
        >
          <span>Press Enter to send, Shift+Enter for new line</span>
          {message.length > 0 && (
            <span className={cn(message.length > 1000 && "text-warning")}>
              {message.length > 1000 && "⚠ "}
              {message.length}/2000
            </span>
          )}
        </motion.div>
      </form>
    </div>
  );
}
