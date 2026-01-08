/**
 * Formatting utilities for output
 */

import { CHARACTER_LIMIT } from "../types.js";

/**
 * Truncate text if it exceeds character limit
 */
export function truncateText(text: string, limit: number = CHARACTER_LIMIT): string {
  if (text.length <= limit) {
    return text;
  }
  return text.substring(0, limit) + `\n\n... [Response truncated at ${limit} characters]`;
}

/**
 * Format date for display
 */
export function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString('it-IT');
  } catch {
    return dateStr;
  }
}

/**
 * Format bytes to human readable
 */
export function formatBytes(bytes: number | undefined): string {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
