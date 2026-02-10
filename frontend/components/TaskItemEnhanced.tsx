/**
 * Enhanced TaskItem Component - Phase V
 *
 * Displays task with priority badge, due date, tags, and recurring indicator
 */
"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { PriorityBadge } from "./PriorityBadge";
import { TagList } from "./TagList";
import { Calendar, Repeat, Clock } from "lucide-react";
import type { Task } from "@/types/task";

interface TaskItemEnhancedProps {
  task: Task;
  onToggleComplete: (id: number) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export default function TaskItemEnhanced({ task, onToggleComplete, onDelete }: TaskItemEnhancedProps) {
  const [isHovered, setIsHovered] = React.useState(false);
  const [showActions, setShowActions] = React.useState(false);
  const [loading, setLoading] = React.useState(false);

  const handleToggle = async () => {
    setLoading(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(task.id);
    } finally {
      setLoading(false);
    }
  };

  // Calculate if task is overdue
  const isOverdue = task.due_date && !task.completed && new Date(task.due_date) < new Date();

  // Format due date
  const formatDueDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 0) {
      return 'Overdue';
    } else if (diffHours < 24) {
      return `Due in ${diffHours}h`;
    } else if (diffDays < 7) {
      return `Due in ${diffDays}d`;
    } else {
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      });
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.2 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowActions(false);
      }}
      className={cn(
        "group relative rounded-lg border transition-all duration-200",
        "hover:shadow-md hover:scale-[1.01]",
        task.completed
          ? "bg-muted/50 border-border/50"
          : "bg-card border-border hover:border-primary/30"
      )}
    >
      <div className="flex items-start gap-4 p-4">
        {/* Checkbox */}
        <button
          onClick={handleToggle}
          disabled={loading}
          className={cn(
            "mt-0.5 flex-shrink-0 w-5 h-5 rounded border-2 transition-all duration-200",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            task.completed
              ? "bg-primary border-primary"
              : "border-foreground-tertiary hover:border-primary"
          )}
          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
        >
          <AnimatePresence>
            {task.completed && (
              <motion.svg
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ duration: 0.15 }}
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={3}
                stroke="currentColor"
                className="w-full h-full text-white"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4.5 12.75l6 6 9-13.5"
                />
              </motion.svg>
            )}
          </AnimatePresence>
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-2">
          {/* Title and Priority */}
          <div className="flex items-start gap-2">
            <h3
              className={cn(
                "flex-1 text-sm font-medium transition-all duration-200",
                task.completed
                  ? "text-foreground-tertiary line-through"
                  : "text-foreground"
              )}
            >
              {task.title}
            </h3>
            <PriorityBadge priority={task.priority} />
          </div>

          {/* Description */}
          {task.description && (
            <p
              className={cn(
                "text-sm transition-all duration-200",
                task.completed
                  ? "text-foreground-tertiary/70 line-through"
                  : "text-foreground-secondary"
              )}
            >
              {task.description}
            </p>
          )}

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <TagList tags={task.tags} maxDisplay={5} />
          )}

          {/* Metadata Row */}
          <div className="flex items-center gap-3 text-xs text-foreground-tertiary flex-wrap">
            {/* Created Date */}
            <time dateTime={task.created_at} className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {new Date(task.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              })}
            </time>

            {/* Due Date */}
            {task.due_date && (
              <>
                <span>•</span>
                <span
                  className={cn(
                    "flex items-center gap-1",
                    isOverdue && !task.completed && "text-red-600 font-medium"
                  )}
                >
                  <Calendar className="w-3.5 h-3.5" />
                  {formatDueDate(task.due_date)}
                </span>
              </>
            )}

            {/* Recurring Indicator */}
            {task.is_recurring && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1 text-blue-600">
                  <Repeat className="w-3.5 h-3.5" />
                  Recurring
                </span>
              </>
            )}

            {/* Completed Status */}
            {task.completed && (
              <>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    className="w-3.5 h-3.5 text-success"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Completed
                </span>
              </>
            )}
          </div>
        </div>

        {/* Actions */}
        <AnimatePresence>
          {(isHovered || showActions) && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-1"
            >
              <button
                onClick={handleDelete}
                disabled={loading}
                className={cn(
                  "p-1.5 rounded-md transition-colors",
                  "hover:bg-error/10 text-foreground-tertiary hover:text-error",
                  "focus:outline-none focus:ring-2 focus:ring-error focus:ring-offset-2",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
                aria-label="Delete task"
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
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Hover indicator */}
      <motion.div
        className="absolute left-0 top-0 bottom-0 w-1 bg-primary rounded-l-lg"
        initial={{ scaleY: 0 }}
        animate={{ scaleY: isHovered && !task.completed ? 1 : 0 }}
        transition={{ duration: 0.2 }}
      />

      {/* Overdue indicator */}
      {isOverdue && !task.completed && (
        <div className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full m-2" />
      )}
    </motion.div>
  );
}
