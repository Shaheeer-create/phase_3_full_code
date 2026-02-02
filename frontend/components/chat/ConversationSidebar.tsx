/**
 * ConversationSidebar - List of conversations with actions
 * Shows all user conversations with create and delete options
 */
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Conversation } from "@/types/chat";
import { formatDistanceToNow } from "date-fns";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ConversationSidebarProps {
  conversations: Conversation[];
  currentId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
  onDelete: (id: number) => void;
}

export default function ConversationSidebar({
  conversations,
  currentId,
  onSelect,
  onNew,
  onDelete,
}: ConversationSidebarProps) {
  return (
    <div className="w-80 border-r border-border bg-background-secondary/50 backdrop-blur-sm flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-border bg-background/50">
        <Button
          onClick={onNew}
          variant="gradient"
          size="md"
          className="w-full gap-2 shadow-lg hover:shadow-xl transition-shadow"
        >
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
              d="M12 4.5v15m7.5-7.5h-15"
            />
          </svg>
          New Conversation
        </Button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-3">
        {conversations.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12 px-4"
          >
            <div className="w-16 h-16 rounded-full bg-muted mx-auto mb-4 flex items-center justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-8 h-8 text-foreground-tertiary"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"
                />
              </svg>
            </div>
            <p className="text-sm text-foreground-secondary">
              No conversations yet
            </p>
            <p className="text-xs text-foreground-tertiary mt-1">
              Start a new conversation to chat with AI
            </p>
          </motion.div>
        ) : (
          <AnimatePresence mode="popLayout">
            {conversations.map((conversation, index) => (
              <motion.div
                key={conversation.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ delay: index * 0.05 }}
                className={cn(
                  "group relative mb-2 p-3 rounded-lg cursor-pointer transition-all duration-200",
                  "hover:shadow-md hover:scale-[1.02]",
                  currentId === conversation.id
                    ? "bg-primary/10 border-2 border-primary shadow-sm"
                    : "bg-card/50 backdrop-blur-sm border border-border hover:border-primary/30 hover:bg-card"
                )}
                onClick={() => onSelect(conversation.id)}
              >
                {/* Active indicator */}
                {currentId === conversation.id && (
                  <motion.div
                    layoutId="activeConversation"
                    className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-l-lg"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}

                {/* Title */}
                <h4
                  className={cn(
                    "font-medium truncate pr-8 text-sm",
                    currentId === conversation.id
                      ? "text-primary"
                      : "text-foreground group-hover:text-primary"
                  )}
                >
                  {conversation.title}
                </h4>

                {/* Timestamp */}
                <p className="text-xs text-foreground-tertiary mt-1">
                  {formatDistanceToNow(new Date(conversation.updated_at + 'Z'), {
                    addSuffix: true,
                  })}
                </p>

                {/* Delete Button */}
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 0, scale: 0.8 }}
                  whileHover={{ opacity: 1, scale: 1 }}
                  className="absolute top-3 right-3 p-1 rounded-md transition-colors hover:bg-error/10 text-foreground-tertiary hover:text-error group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(conversation.id);
                  }}
                  title="Delete conversation"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-4 h-4"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
                    />
                  </svg>
                </motion.button>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
