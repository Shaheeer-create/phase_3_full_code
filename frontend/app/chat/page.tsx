/**
 * Chat Page - Main AI chatbot interface
 * Manages conversations, messages, and usage tracking
 */
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Conversation, Message, UserUsage } from "@/types/chat";
import { chatApi } from "@/lib/api";
import ConversationSidebar from "@/components/chat/ConversationSidebar";
import ChatInterface from "@/components/chat/ChatInterface";
import UsageIndicator from "@/components/chat/UsageIndicator";
import AppHeader from "@/components/AppHeader";

export default function ChatPage() {
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentId, setCurrentId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [usage, setUsage] = useState<UserUsage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load conversations and usage on mount
  useEffect(() => {
    loadConversations();
    loadUsage();
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentId) {
      loadMessages(currentId);
    } else {
      setMessages([]);
    }
  }, [currentId]);

  const loadConversations = async () => {
    try {
      const data = await chatApi.listConversations();
      setConversations(data);
      setLoading(false);
    } catch (err) {
      setError("Failed to load conversations");
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId: number) => {
    try {
      const data = await chatApi.getMessages(conversationId);
      setMessages(data);
      setError(null);
    } catch (err: any) {
      console.error("Failed to load messages:", err);
      // If conversation not found (404), clear the selection
      if (err.response?.status === 404) {
        setError("Conversation not found or you don't have access to it");
        setCurrentId(null);
      } else {
        setError("Failed to load messages");
      }
    }
  };

  const loadUsage = async () => {
    try {
      const data = await chatApi.getUsage();
      setUsage(data);
    } catch (err) {
      console.error("Failed to load usage:", err);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await chatApi.createConversation();
      setConversations([newConv, ...conversations]);
      setCurrentId(newConv.id);
    } catch (err) {
      setError("Failed to create conversation");
    }
  };

  const handleDeleteConversation = async (id: number) => {
    try {
      await chatApi.deleteConversation(id);
      setConversations(conversations.filter((c) => c.id !== id));
      if (currentId === id) {
        setCurrentId(null);
      }
    } catch (err) {
      setError("Failed to delete conversation");
    }
  };

  const handleMessagesUpdate = async () => {
    // Reload messages and usage after sending
    if (currentId) {
      await loadMessages(currentId);
      await loadUsage();
      // Reload conversations to update timestamps
      await loadConversations();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
          <p className="text-sm text-foreground-secondary">Loading conversations...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-accent-purple/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <AppHeader currentPage="chat" />

      {/* Usage Indicator */}
      {usage && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <UsageIndicator usage={usage} />
        </motion.div>
      )}

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        <ConversationSidebar
          conversations={conversations}
          currentId={currentId}
          onSelect={setCurrentId}
          onNew={handleNewConversation}
          onDelete={handleDeleteConversation}
        />
        <ChatInterface
          conversationId={currentId}
          messages={messages}
          onMessagesUpdate={handleMessagesUpdate}
        />
      </div>

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-6 right-6 bg-error text-white px-6 py-4 rounded-xl shadow-2xl max-w-md z-50"
          >
            <div className="flex items-start gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-5 h-5 flex-shrink-0 mt-0.5"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                />
              </svg>
              <div className="flex-1">
                <p className="font-medium">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-white/80 hover:text-white transition-colors"
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
    </div>
  );
}
