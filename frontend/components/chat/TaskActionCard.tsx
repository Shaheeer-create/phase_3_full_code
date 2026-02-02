/**
 * TaskActionCard - Display tool execution results
 * Shows when AI executes task management tools
 */
"use client";

interface ToolCall {
  tool: string;
  args: Record<string, any>;
  result: {
    success: boolean;
    message?: string;
    task?: any;
    tasks?: any[];
    count?: number;
    error?: string;
  };
}

interface TaskActionCardProps {
  toolCalls: ToolCall[];
}

export default function TaskActionCard({ toolCalls }: TaskActionCardProps) {
  if (!toolCalls || toolCalls.length === 0) return null;

  const getToolIcon = (toolName: string) => {
    switch (toolName) {
      case "create_task":
        return "➕";
      case "list_tasks":
        return "📋";
      case "update_task":
        return "✏️";
      case "delete_task":
        return "🗑️";
      default:
        return "🔧";
    }
  };

  const getToolLabel = (toolName: string) => {
    switch (toolName) {
      case "create_task":
        return "Created Task";
      case "list_tasks":
        return "Listed Tasks";
      case "update_task":
        return "Updated Task";
      case "delete_task":
        return "Deleted Task";
      default:
        return "Tool Executed";
    }
  };

  return (
    <div className="space-y-2 mt-3 pt-3 border-t border-gray-200">
      {toolCalls.map((toolCall, index) => (
        <div
          key={index}
          className={`rounded-lg p-3 text-sm ${
            toolCall.result.success
              ? "bg-green-50 border border-green-200"
              : "bg-red-50 border border-red-200"
          }`}
        >
          {/* Tool Header */}
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{getToolIcon(toolCall.tool)}</span>
            <span className="font-semibold text-gray-900">
              {getToolLabel(toolCall.tool)}
            </span>
            {toolCall.result.success ? (
              <span className="ml-auto text-green-600 text-xs">✓ Success</span>
            ) : (
              <span className="ml-auto text-red-600 text-xs">✗ Failed</span>
            )}
          </div>

          {/* Tool Details */}
          {toolCall.result.success ? (
            <div className="text-gray-700">
              {/* Create Task Result */}
              {toolCall.tool === "create_task" && toolCall.result.task && (
                <div>
                  <p className="font-medium">{toolCall.result.task.title}</p>
                  {toolCall.result.task.description && (
                    <p className="text-xs text-gray-600 mt-1">
                      {toolCall.result.task.description}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    Task ID: {toolCall.result.task.id}
                  </p>
                </div>
              )}

              {/* List Tasks Result */}
              {toolCall.tool === "list_tasks" && (
                <div>
                  <p className="text-gray-600">
                    Found {toolCall.result.count || 0} task(s)
                  </p>
                  {toolCall.result.tasks && toolCall.result.tasks.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {toolCall.result.tasks.slice(0, 3).map((task: any) => (
                        <div
                          key={task.id}
                          className="text-xs bg-white rounded px-2 py-1 border border-gray-200"
                        >
                          <span className="font-medium">#{task.id}</span> {task.title}
                          {task.completed && (
                            <span className="ml-2 text-green-600">✓</span>
                          )}
                        </div>
                      ))}
                      {toolCall.result.tasks.length > 3 && (
                        <p className="text-xs text-gray-500 italic">
                          +{toolCall.result.tasks.length - 3} more...
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Update Task Result */}
              {toolCall.tool === "update_task" && toolCall.result.task && (
                <div>
                  <p className="font-medium">{toolCall.result.task.title}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Task ID: {toolCall.result.task.id}
                    {toolCall.result.task.completed !== undefined && (
                      <span className="ml-2">
                        Status: {toolCall.result.task.completed ? "Completed ✓" : "Pending"}
                      </span>
                    )}
                  </p>
                </div>
              )}

              {/* Delete Task Result */}
              {toolCall.tool === "delete_task" && (
                <div>
                  <p className="text-gray-600">{toolCall.result.message}</p>
                </div>
              )}

              {/* Generic Success Message */}
              {toolCall.result.message &&
               !["create_task", "list_tasks", "update_task", "delete_task"].includes(toolCall.tool) && (
                <p className="text-gray-600">{toolCall.result.message}</p>
              )}
            </div>
          ) : (
            <div className="text-red-700">
              <p className="font-medium">Error</p>
              <p className="text-xs mt-1">
                {toolCall.result.error || toolCall.result.message || "Unknown error"}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
