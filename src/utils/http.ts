/**
 * HTTP utilities for CKAN API requests
 */

import axios, { AxiosError } from "axios";

/**
 * Make HTTP request to CKAN API
 */
export async function makeCkanRequest<T>(
  serverUrl: string,
  action: string,
  params: Record<string, any> = {}
): Promise<T> {
  // Normalize server URL
  const baseUrl = serverUrl.replace(/\/$/, '');
  const url = `${baseUrl}/api/3/action/${action}`;

  try {
    const response = await axios.get(url, {
      params,
      timeout: 30000,
      headers: {
        'User-Agent': 'CKAN-MCP-Server/1.0'
      }
    });

    if (response.data && response.data.success === true) {
      return response.data.result as T;
    } else {
      throw new Error(`CKAN API returned success=false: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        const status = axiosError.response.status;
        const data = axiosError.response.data as any;
        const errorMsg = data?.error?.message || data?.error || 'Unknown error';
        throw new Error(`CKAN API error (${status}): ${errorMsg}`);
      } else if (axiosError.code === 'ECONNABORTED') {
        throw new Error(`Request timeout connecting to ${serverUrl}`);
      } else if (axiosError.code === 'ENOTFOUND') {
        throw new Error(`Server not found: ${serverUrl}`);
      } else {
        throw new Error(`Network error: ${axiosError.message}`);
      }
    }
    throw error;
  }
}
