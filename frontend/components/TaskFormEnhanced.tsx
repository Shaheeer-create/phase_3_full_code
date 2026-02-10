/**
 * Enhanced TaskForm Component - Phase V
 *
 * Supports priority, due date, tags, and recurring task configuration
 */
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Calendar, Tag, Repeat, X } from "lucide-react";
import type { TaskCreate, RecurringPattern } from "@/types/task";

interface TaskFormEnhancedProps {
  onSubmit: (data: TaskCreate) => Promise<void>;
}

export default function TaskFormEnhanced({ onSubmit }: TaskFormEnhancedProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [dueDate, setDueDate] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState("");
  const [isRecurring, setIsRecurring] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsLoading(true);
    try {
      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate || undefined,
        tags: tags.length > 0 ? tags : undefined,
        is_recurring: isRecurring,
      };

      await onSubmit(taskData);

      // Reset form
      setTitle("");
      setDescription("");
      setPriority('medium');
      setDueDate("");
      setTags([]);
      setTagInput("");
      setIsRecurring(false);
      setIsExpanded(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTag = () => {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag]);
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleTagInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  return (
    <motion.div
      layout
      onClick={() => {
        if (!isExpanded) {
          setIsExpanded(true);
          setTimeout(() => {
            document.querySelector<HTMLInputElement>('input[placeholder="Add a new task..."]')?.focus();
          }, 100);
        }
      }}
      className={cn(
        "group rounded-xl border transition-all duration-200 cursor-pointer",
        isExpanded
          ? "bg-card border-primary/50 shadow-lg"
          : "bg-card/50 border-border hover:border-primary/30 hover:bg-card/80 hover:shadow-md"
      )}
    >
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-3">
            <div className="w-5 h-5 rounded border-2 border-foreground-tertiary transition-colors group-hover:border-primary/50" />
          </div>
          <div className="flex-1 space-y-3">
            <input
              type="text"
              placeholder="Add a new task..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              onFocus={() => setIsExpanded(true)}
              className={cn(
                "w-full border-0 bg-transparent px-0 text-base cursor-text",
                "placeholder:text-foreground-tertiary text-foreground",
                "focus:outline-none focus:ring-0",
                "hover:placeholder:text-foreground-secondary transition-colors"
              )}
            />

            <motion.div
              initial={false}
              animate={{
                height: isExpanded ? "auto" : 0,
                opacity: isExpanded ? 1 : 0,
              }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden space-y-3"
            >
              <textarea
                placeholder="Add description (optional)..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className={cn(
                  "w-full px-0 py-2 text-sm bg-transparent border-0",
                  "placeholder:text-foreground-tertiary text-foreground-secondary",
                  "focus:outline-none focus:ring-0 resize-none"
                )}
              />

              {/* Priority Selector */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-foreground-secondary">Priority:</span>
                <div className="flex gap-1">
                  {(['low', 'medium', 'high'] as const).map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPriority(p)}
                      className={cn(
                        "px-3 py-1 rounded-md text-xs font-medium transition-colors",
                        priority === p
                          ? p === 'low'
                            ? "bg-blue-100 text-blue-800 border border-blue-200"
                            : p === 'medium'
                            ? "bg-yellow-100 text-yellow-800 border border-yellow-200"
                            : "bg-red-100 text-red-800 border border-red-200"
                          : "bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200"
                      )}
                    >
                      {p.charAt(0).toUpperCase() + p.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Due Date Picker */}
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-foreground-tertiary" />
                <input
                  type="datetime-local"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className={cn(
                    "flex-1 px-2 py-1 text-sm bg-transparent border border-border rounded-md",
                    "focus:outline-none focus:ring-2 focus:ring-primary/50"
                  )}
                />
              </div>

              {/* Tags Input */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Tag className="w-4 h-4 text-foreground-tertiary" />
                  <input
                    type="text"
                    placeholder="Add tags (press Enter)..."
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={handleTagInputKeyDown}
                    className={cn(
                      "flex-1 px-2 py-1 text-sm bg-transparent border border-border rounded-md",
                      "focus:outline-none focus:ring-2 focus:ring-primary/50"
                    )}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleAddTag}
                    disabled={!tagInput.trim()}
                  >
                    Add
                  </Button>
                </div>

                {/* Display Tags */}
                {tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pl-6">
                    {tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200"
                      >
                        <span className="text-gray-500">#</span>
                        {tag}
                        <button
                          type="button"
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-0.5 hover:bg-gray-200 rounded-full p-0.5 transition-colors"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Recurring Task Toggle */}
              <div className="flex items-center gap-2">
                <Repeat className="w-4 h-4 text-foreground-tertiary" />
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isRecurring}
                    onChange={(e) => setIsRecurring(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span className="text-sm text-foreground-secondary">
                    Recurring task
                  </span>
                </label>
              </div>
            </motion.div>
          </div>
        </div>

        <motion.div
          initial={false}
          animate={{
            height: isExpanded ? "auto" : 0,
            opacity: isExpanded ? 1 : 0,
          }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
            <div className="flex items-center gap-2 text-xs text-foreground-tertiary">
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
                  d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"
                />
              </svg>
              <span>AI-powered task management</span>
            </div>
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => {
                  setIsExpanded(false);
                  setTitle("");
                  setDescription("");
                  setPriority('medium');
                  setDueDate("");
                  setTags([]);
                  setTagInput("");
                  setIsRecurring(false);
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={!title.trim() || isLoading}
                isLoading={isLoading}
              >
                Add task
              </Button>
            </div>
          </div>
        </motion.div>
      </form>
    </motion.div>
  );
}
