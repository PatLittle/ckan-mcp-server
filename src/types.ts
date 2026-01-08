/**
 * Type definitions and schemas for CKAN MCP Server
 */

import { z } from "zod";

export enum ResponseFormat {
  MARKDOWN = "markdown",
  JSON = "json"
}

export const ResponseFormatSchema = z.nativeEnum(ResponseFormat)
  .default(ResponseFormat.MARKDOWN)
  .describe("Output format: 'markdown' for human-readable or 'json' for machine-readable");

export const CHARACTER_LIMIT = 50000;
