/**
 * CKAN Quality (MQA) tools for dati.gov.it
 */

import { z } from "zod";
import axios from "axios";
import { ResponseFormat, ResponseFormatSchema } from "../types.js";
import { makeCkanRequest } from "../utils/http.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

const MQA_API_BASE = "https://data.europa.eu/api/mqa/cache/datasets";
const ALLOWED_SERVER_PATTERNS = [
  /^https?:\/\/(www\.)?dati\.gov\.it/i
];

/**
 * Validate server URL is dati.gov.it
 */
export function isValidMqaServer(serverUrl: string): boolean {
  return ALLOWED_SERVER_PATTERNS.some(pattern => pattern.test(serverUrl));
}

function normalizeMqaIdentifier(identifier: string): string {
  return identifier
    .trim()
    .replace(/:/g, "-")
    .replace(/-+/g, "-")
    .toLowerCase();
}

function buildMqaIdCandidates(identifier: string): string[] {
  const base = normalizeMqaIdentifier(identifier);
  if (!base) {
    return [];
  }

  const candidates = [base];
  if (!base.includes("~~")) {
    candidates.push(`${base}~~1`, `${base}~~2`);
  }

  return candidates;
}

/**
 * Get MQA quality metrics from data.europa.eu
 */
export async function getMqaQuality(serverUrl: string, datasetId: string): Promise<any> {
  // Step 1: Get dataset metadata from CKAN to extract identifier
  interface PackageShowResult {
    identifier?: string;
    name: string;
  }

  const dataset = await makeCkanRequest<PackageShowResult>(
    serverUrl,
    "package_show",
    { id: datasetId }
  );

  // Step 2: Use identifier field, fallback to name
  const baseIdentifier = dataset.identifier || dataset.name;
  const candidates = buildMqaIdCandidates(baseIdentifier);

  if (candidates.length === 0) {
    throw new Error("Dataset identifier is empty; cannot query MQA API");
  }

  // Step 3: Query MQA API (try candidates)
  for (const europeanId of candidates) {
    const mqaUrl = `${MQA_API_BASE}/${europeanId}`;

    try {
      const response = await axios.get(mqaUrl, {
        timeout: 30000,
        headers: {
          'User-Agent': 'CKAN-MCP-Server/1.0'
        }
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 404) {
          continue;
        }
        throw new Error(`MQA API error: ${error.message}`);
      }
      throw error;
    }
  }

  throw new Error(
    `Quality metrics not found or identifier not aligned on data.europa.eu. ` +
    `Tried: ${candidates.join(", ")}. ` +
    `Check the dataset quality page on data.europa.eu to confirm the identifier (it may include a '~~1' suffix) ` +
    `or verify alignment on dati.gov.it (quality may be marked as 'Non disponibile o identificativo non allineato').`
  );
}

/**
 * Format MQA quality data as markdown
 */
type Availability = {
  available: boolean;
};

type NormalizedQualityData = {
  id?: string;
  info?: {
    score?: number;
  };
  accessibility?: {
    accessUrl?: Availability;
    downloadUrl?: Availability;
  };
  reusability?: {
    licence?: Availability;
    contactPoint?: Availability;
    publisher?: Availability;
  };
  interoperability?: {
    format?: Availability;
    mediaType?: Availability;
  };
  findability?: {
    keyword?: Availability;
    category?: Availability;
    spatial?: Availability;
    temporal?: Availability;
  };
};

function findSectionMetric(section: unknown, key: string): unknown {
  if (!Array.isArray(section)) {
    return undefined;
  }

  for (const item of section) {
    if (item && typeof item === "object" && key in item) {
      return (item as Record<string, unknown>)[key];
    }
  }

  return undefined;
}

function metricArrayIsAvailable(metric: unknown): boolean | undefined {
  if (!Array.isArray(metric)) {
    return undefined;
  }

  const byName = new Map<string, number>();
  for (const entry of metric) {
    if (!entry || typeof entry !== "object") {
      continue;
    }
    const name = (entry as Record<string, unknown>).name;
    const percentage = (entry as Record<string, unknown>).percentage;
    if (typeof name === "string" && typeof percentage === "number") {
      byName.set(name.toLowerCase(), percentage);
    }
  }

  if (byName.has("yes")) {
    return (byName.get("yes") || 0) > 0;
  }

  if (byName.size > 0) {
    for (const [name, percentage] of byName.entries()) {
      if (name.startsWith("2") && percentage > 0) {
        return true;
      }
    }
    return false;
  }

  return undefined;
}

function metricBoolean(section: unknown, key: string): boolean | undefined {
  const metric = findSectionMetric(section, key);
  if (typeof metric === "boolean") {
    return metric;
  }
  return undefined;
}

function metricAvailability(section: unknown, availabilityKey: string, statusKey?: string): Availability | undefined {
  const availabilityMetric = findSectionMetric(section, availabilityKey);
  const availability = metricArrayIsAvailable(availabilityMetric);
  if (availability !== undefined) {
    return { available: availability };
  }

  if (statusKey) {
    const statusMetric = findSectionMetric(section, statusKey);
    const statusAvailable = metricArrayIsAvailable(statusMetric);
    if (statusAvailable !== undefined) {
      return { available: statusAvailable };
    }
  }

  return undefined;
}

function normalizeQualityData(data: any): NormalizedQualityData {
  const resultEntry = data?.result?.results?.[0];
  if (!resultEntry || typeof resultEntry !== "object") {
    return data;
  }

  return {
    id: resultEntry.info?.["dataset-id"],
    info: { score: resultEntry.info?.score },
    accessibility: {
      accessUrl: metricAvailability(resultEntry.accessibility, "accessUrlAvailability", "accessUrlStatusCode"),
      downloadUrl: metricAvailability(resultEntry.accessibility, "downloadUrlAvailability", "downloadUrlStatusCode")
    },
    reusability: {
      licence: metricAvailability(resultEntry.reusability, "licenceAvailability"),
      contactPoint: metricBoolean(resultEntry.reusability, "contactPointAvailability") !== undefined
        ? { available: metricBoolean(resultEntry.reusability, "contactPointAvailability") as boolean }
        : undefined,
      publisher: metricBoolean(resultEntry.reusability, "publisherAvailability") !== undefined
        ? { available: metricBoolean(resultEntry.reusability, "publisherAvailability") as boolean }
        : undefined
    },
    interoperability: {
      format: metricAvailability(resultEntry.interoperability, "formatAvailability"),
      mediaType: metricAvailability(resultEntry.interoperability, "mediaTypeAvailability")
    },
    findability: {
      keyword: metricBoolean(resultEntry.findability, "keywordAvailability") !== undefined
        ? { available: metricBoolean(resultEntry.findability, "keywordAvailability") as boolean }
        : undefined,
      category: metricBoolean(resultEntry.findability, "categoryAvailability") !== undefined
        ? { available: metricBoolean(resultEntry.findability, "categoryAvailability") as boolean }
        : undefined,
      spatial: metricBoolean(resultEntry.findability, "spatialAvailability") !== undefined
        ? { available: metricBoolean(resultEntry.findability, "spatialAvailability") as boolean }
        : undefined,
      temporal: metricBoolean(resultEntry.findability, "temporalAvailability") !== undefined
        ? { available: metricBoolean(resultEntry.findability, "temporalAvailability") as boolean }
        : undefined
    }
  };
}

export function formatQualityMarkdown(data: any, datasetId: string): string {
  const normalized = normalizeQualityData(data);
  const lines: string[] = [];

  lines.push(`# Quality Metrics for Dataset: ${datasetId}`);
  lines.push("");

  if (normalized.info?.score !== undefined) {
    lines.push(`**Overall Score**: ${normalized.info.score}/405`);
    lines.push("");
  }

  // Accessibility
  if (normalized.accessibility) {
    lines.push("## Accessibility");
    if (normalized.accessibility.accessUrl !== undefined) {
      lines.push(`- Access URL: ${normalized.accessibility.accessUrl.available ? '✓' : '✗'} Available`);
    }
    if (normalized.accessibility.downloadUrl !== undefined) {
      lines.push(`- Download URL: ${normalized.accessibility.downloadUrl.available ? '✓' : '✗'} Available`);
    }
    lines.push("");
  }

  // Reusability
  if (normalized.reusability) {
    lines.push("## Reusability");
    if (normalized.reusability.licence !== undefined) {
      lines.push(`- License: ${normalized.reusability.licence.available ? '✓' : '✗'} Available`);
    }
    if (normalized.reusability.contactPoint !== undefined) {
      lines.push(`- Contact Point: ${normalized.reusability.contactPoint.available ? '✓' : '✗'} Available`);
    }
    if (normalized.reusability.publisher !== undefined) {
      lines.push(`- Publisher: ${normalized.reusability.publisher.available ? '✓' : '✗'} Available`);
    }
    lines.push("");
  }

  // Interoperability
  if (normalized.interoperability) {
    lines.push("## Interoperability");
    if (normalized.interoperability.format !== undefined) {
      lines.push(`- Format: ${normalized.interoperability.format.available ? '✓' : '✗'} Available`);
    }
    if (normalized.interoperability.mediaType !== undefined) {
      lines.push(`- Media Type: ${normalized.interoperability.mediaType.available ? '✓' : '✗'} Available`);
    }
    lines.push("");
  }

  // Findability
  if (normalized.findability) {
    lines.push("## Findability");
    if (normalized.findability.keyword !== undefined) {
      lines.push(`- Keywords: ${normalized.findability.keyword.available ? '✓' : '✗'} Available`);
    }
    if (normalized.findability.category !== undefined) {
      lines.push(`- Category: ${normalized.findability.category.available ? '✓' : '✗'} Available`);
    }
    if (normalized.findability.spatial !== undefined) {
      lines.push(`- Spatial: ${normalized.findability.spatial.available ? '✓' : '✗'} Available`);
    }
    if (normalized.findability.temporal !== undefined) {
      lines.push(`- Temporal: ${normalized.findability.temporal.available ? '✓' : '✗'} Available`);
    }
    lines.push("");
  }

  lines.push("---");
  const portalId = normalized.id || datasetId;
  lines.push(`Portal: https://data.europa.eu/data/datasets/${portalId}/quality?locale=it`);
  lines.push(`Source: ${MQA_API_BASE}/${portalId}`);

  return lines.join("\n");
}

/**
 * Register MQA quality tools
 */
export function registerQualityTools(server: McpServer): void {
  server.tool(
    "ckan_get_mqa_quality",
    "Get MQA (Metadata Quality Assurance) quality metrics for a dataset on dati.gov.it. " +
    "Returns quality score and detailed metrics (accessibility, reusability, interoperability, findability) " +
    "from data.europa.eu. Only works with dati.gov.it server.",
    {
      server_url: z.string().url().describe("Base URL of dati.gov.it (e.g., https://www.dati.gov.it/opendata)"),
      dataset_id: z.string().describe("Dataset ID or name"),
      response_format: ResponseFormatSchema.optional()
    },
    async ({ server_url, dataset_id, response_format }) => {
      // Validate server URL
      if (!isValidMqaServer(server_url)) {
        return {
          content: [{
            type: "text" as const,
            text: `Error: MQA quality metrics are only available for dati.gov.it datasets. ` +
                  `Provided server: ${server_url}\n\n` +
                  `The MQA (Metadata Quality Assurance) system is operated by data.europa.eu ` +
                  `and only evaluates datasets from Italian open data portal.`
          }]
        };
      }

      try {
        const qualityData = await getMqaQuality(server_url, dataset_id);

        const format = response_format || ResponseFormat.MARKDOWN;
        const output = format === ResponseFormat.JSON
          ? JSON.stringify(qualityData, null, 2)
          : formatQualityMarkdown(qualityData, dataset_id);

        return {
          content: [{
            type: "text" as const,
            text: output
          }]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return {
          content: [{
            type: "text" as const,
            text: `Error retrieving quality metrics: ${errorMessage}`
          }]
        };
      }
    }
  );
}
