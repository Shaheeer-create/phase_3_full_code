/**
 * Task type definitions - Phase V Enhanced
 */
export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;

  // Phase V: Advanced features
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  is_recurring: boolean;
  parent_task_id?: number;
  recurrence_instance_date?: string;
  tags?: string[];

  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  tags?: string[];
  is_recurring?: boolean;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
}

export interface RecurringPattern {
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly';
  interval: number;
  days_of_week?: string; // JSON array: [0,1,2,3,4,5,6]
  day_of_month?: number;
  month_of_year?: number;
  end_date?: string;
}

export interface TaskReminder {
  id: number;
  task_id: number;
  user_id: string;
  reminder_time: string;
  reminder_type: 'notification' | 'email' | 'both';
  is_sent: boolean;
  created_at: string;
}

export interface TaskSearchParams {
  q?: string;
  priority?: 'low' | 'medium' | 'high';
  tags?: string;
  due_before?: string;
  due_after?: string;
  status?: 'all' | 'pending' | 'completed';
  sort_by?: 'created_at' | 'due_date' | 'priority';
  sort_order?: 'asc' | 'desc';
}

