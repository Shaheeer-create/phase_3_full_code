/**
 * TagList Component - Phase V
 *
 * Displays a list of tags with optional remove functionality
 */
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface TagListProps {
  tags: string[];
  onRemove?: (tag: string) => void;
  className?: string;
  maxDisplay?: number;
}

export function TagList({ tags, onRemove, className, maxDisplay }: TagListProps) {
  if (!tags || tags.length === 0) {
    return null;
  }

  const displayTags = maxDisplay ? tags.slice(0, maxDisplay) : tags;
  const remainingCount = maxDisplay && tags.length > maxDisplay ? tags.length - maxDisplay : 0;

  return (
    <div className={cn("flex flex-wrap gap-1.5", className)}>
      {displayTags.map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-700 border border-gray-200"
        >
          <span className="text-gray-500">#</span>
          {tag}
          {onRemove && (
            <button
              onClick={() => onRemove(tag)}
              className="ml-0.5 hover:bg-gray-200 rounded-full p-0.5 transition-colors"
              aria-label={`Remove tag ${tag}`}
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </span>
      ))}
      {remainingCount > 0 && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-500">
          +{remainingCount} more
        </span>
      )}
    </div>
  );
}
