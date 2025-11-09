import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS classes
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format score to 0-100 range with color
 */
export function getScoreColor(score: number): string {
  if (score >= 90) return "text-green-600";
  if (score >= 75) return "text-blue-600";
  if (score >= 60) return "text-yellow-600";
  if (score >= 40) return "text-orange-600";
  return "text-red-600";
}

/**
 * Format date to relative time
 */
export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return d.toLocaleDateString();
}

/**
 * Format work type to readable label
 */
export function formatWorkType(type: string): string {
  const labels: Record<string, string> = {
    code: "Code",
    research: "Research",
    documentation: "Documentation",
    dashboard: "Dashboard",
    meeting: "Meeting",
    mentoring: "Mentoring",
    code_review: "Code Review",
    operations: "Operations",
    design: "Design",
    testing: "Testing",
    bug_fix: "Bug Fix",
    refactoring: "Refactoring",
    other: "Other",
  };
  return labels[type] || type;
}

/**
 * Get role level color
 */
export function getRoleLevelColor(level: string): string {
  const colors: Record<string, string> = {
    intern: "bg-gray-100 text-gray-800",
    junior: "bg-green-100 text-green-800",
    mid: "bg-blue-100 text-blue-800",
    senior: "bg-purple-100 text-purple-800",
    staff: "bg-orange-100 text-orange-800",
    principal: "bg-red-100 text-red-800",
  };
  return colors[level] || "bg-gray-100 text-gray-800";
}
