/**
 * UsageIndicator - Display usage statistics and limits
 * Shows messages used today and tokens used this month
 */
"use client";

import { UserUsage } from "@/types/chat";

interface UsageIndicatorProps {
  usage: UserUsage | null;
}

export default function UsageIndicator({ usage }: UsageIndicatorProps) {
  if (!usage) return null;

  const messagePercentage = (usage.messages_today / usage.max_messages_per_day) * 100;
  const tokenPercentage = (usage.tokens_this_month / usage.max_tokens_per_month) * 100;

  const isMessageWarning = messagePercentage >= 80;
  const isTokenWarning = tokenPercentage >= 80;

  return (
    <div className="border-b border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Usage Limits</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Messages Today */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600">Messages Today</span>
              <span className={`text-xs font-medium ${isMessageWarning ? "text-red-600" : "text-gray-900"}`}>
                {usage.messages_today} / {usage.max_messages_per_day}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  isMessageWarning ? "bg-red-500" : "bg-indigo-600"
                }`}
                style={{ width: `${Math.min(messagePercentage, 100)}%` }}
              />
            </div>
            {isMessageWarning && (
              <p className="text-xs text-red-600 mt-1">
                ⚠️ Approaching daily limit
              </p>
            )}
          </div>

          {/* Tokens This Month */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600">Tokens This Month</span>
              <span className={`text-xs font-medium ${isTokenWarning ? "text-red-600" : "text-gray-900"}`}>
                {usage.tokens_this_month.toLocaleString()} / {usage.max_tokens_per_month.toLocaleString()}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  isTokenWarning ? "bg-red-500" : "bg-green-600"
                }`}
                style={{ width: `${Math.min(tokenPercentage, 100)}%` }}
              />
            </div>
            {isTokenWarning && (
              <p className="text-xs text-red-600 mt-1">
                ⚠️ Approaching monthly limit
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
