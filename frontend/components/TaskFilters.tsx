/**
 * TaskFilters Component - Phase V
 *
 * Advanced filtering UI for tasks (priority, tags, due date, search)
 */
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Search, Filter, X, Calendar, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { TaskSearchParams } from "@/types/task";

interface TaskFiltersProps {
  onFilterChange: (filters: TaskSearchParams) => void;
  className?: string;
}

export function TaskFilters({ onFilterChange, className }: TaskFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPriority, setSelectedPriority] = useState<'low' | 'medium' | 'high' | undefined>();
  const [selectedTags, setSelectedTags] = useState<string>("");
  const [dueBefore, setDueBefore] = useState("");
  const [dueAfter, setDueAfter] = useState("");
  const [status, setStatus] = useState<'all' | 'pending' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'due_date' | 'priority'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const hasActiveFilters =
    searchQuery ||
    selectedPriority ||
    selectedTags ||
    dueBefore ||
    dueAfter ||
    status !== 'all' ||
    sortBy !== 'created_at' ||
    sortOrder !== 'desc';

  const handleApplyFilters = () => {
    const filters: TaskSearchParams = {
      q: searchQuery || undefined,
      priority: selectedPriority,
      tags: selectedTags || undefined,
      due_before: dueBefore || undefined,
      due_after: dueAfter || undefined,
      status,
      sort_by: sortBy,
      sort_order: sortOrder,
    };

    onFilterChange(filters);
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setSelectedPriority(undefined);
    setSelectedTags("");
    setDueBefore("");
    setDueAfter("");
    setStatus('all');
    setSortBy('created_at');
    setSortOrder('desc');

    onFilterChange({
      status: 'all',
      sort_by: 'created_at',
      sort_order: 'desc',
    });
  };

  return (
    <div className={cn("space-y-3", className)}>
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-foreground-tertiary" />
        <input
          type="text"
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleApplyFilters();
            }
          }}
          className={cn(
            "w-full pl-10 pr-4 py-2 rounded-lg border border-border",
            "bg-card text-foreground placeholder:text-foreground-tertiary",
            "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary",
            "transition-all duration-200"
          )}
        />
      </div>

      {/* Filter Toggle Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium",
            "transition-colors duration-200",
            hasActiveFilters
              ? "bg-primary text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          )}
        >
          <Filter className="w-4 h-4" />
          Filters
          {hasActiveFilters && (
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-white/20 text-xs">
              Active
            </span>
          )}
        </button>

        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="flex items-center gap-1 px-2 py-1 text-xs text-gray-600 hover:text-gray-900 transition-colors"
          >
            <X className="w-3 h-3" />
            Clear all
          </button>
        )}
      </div>

      {/* Expanded Filters */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4 rounded-lg border border-border bg-card space-y-4">
              {/* Priority Filter */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Priority</label>
                <div className="flex gap-2">
                  {(['low', 'medium', 'high'] as const).map((priority) => (
                    <button
                      key={priority}
                      onClick={() => setSelectedPriority(selectedPriority === priority ? undefined : priority)}
                      className={cn(
                        "px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                        selectedPriority === priority
                          ? priority === 'low'
                            ? "bg-blue-100 text-blue-800 border-2 border-blue-300"
                            : priority === 'medium'
                            ? "bg-yellow-100 text-yellow-800 border-2 border-yellow-300"
                            : "bg-red-100 text-red-800 border-2 border-red-300"
                          : "bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200"
                      )}
                    >
                      {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Status Filter */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Status</label>
                <div className="flex gap-2">
                  {(['all', 'pending', 'completed'] as const).map((s) => (
                    <button
                      key={s}
                      onClick={() => setStatus(s)}
                      className={cn(
                        "px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
                        status === s
                          ? "bg-primary text-white"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      )}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tags Filter */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Tag className="w-4 h-4" />
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="work, urgent, personal..."
                  value={selectedTags}
                  onChange={(e) => setSelectedTags(e.target.value)}
                  className={cn(
                    "w-full px-3 py-2 rounded-md border border-border",
                    "bg-background text-foreground placeholder:text-foreground-tertiary",
                    "focus:outline-none focus:ring-2 focus:ring-primary/50"
                  )}
                />
              </div>

              {/* Due Date Range */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Due Date Range
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-foreground-secondary">After</label>
                    <input
                      type="datetime-local"
                      value={dueAfter}
                      onChange={(e) => setDueAfter(e.target.value)}
                      className={cn(
                        "w-full px-2 py-1.5 text-sm rounded-md border border-border",
                        "bg-background text-foreground",
                        "focus:outline-none focus:ring-2 focus:ring-primary/50"
                      )}
                    />
                  </div>
                  <div>
                    <label className="text-xs text-foreground-secondary">Before</label>
                    <input
                      type="datetime-local"
                      value={dueBefore}
                      onChange={(e) => setDueBefore(e.target.value)}
                      className={cn(
                        "w-full px-2 py-1.5 text-sm rounded-md border border-border",
                        "bg-background text-foreground",
                        "focus:outline-none focus:ring-2 focus:ring-primary/50"
                      )}
                    />
                  </div>
                </div>
              </div>

              {/* Sort Options */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Sort By</label>
                <div className="flex gap-2">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className={cn(
                      "flex-1 px-3 py-2 rounded-md border border-border",
                      "bg-background text-foreground",
                      "focus:outline-none focus:ring-2 focus:ring-primary/50"
                    )}
                  >
                    <option value="created_at">Created Date</option>
                    <option value="due_date">Due Date</option>
                    <option value="priority">Priority</option>
                  </select>
                  <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value as any)}
                    className={cn(
                      "px-3 py-2 rounded-md border border-border",
                      "bg-background text-foreground",
                      "focus:outline-none focus:ring-2 focus:ring-primary/50"
                    )}
                  >
                    <option value="desc">Newest First</option>
                    <option value="asc">Oldest First</option>
                  </select>
                </div>
              </div>

              {/* Apply Button */}
              <div className="pt-2">
                <Button
                  onClick={handleApplyFilters}
                  variant="primary"
                  className="w-full"
                >
                  Apply Filters
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
