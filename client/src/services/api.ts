export const API_BASE_URL = "http://localhost:8000";

export interface Source {
  file_path: string;
  name: string;
  type: string;
  content: string;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

export interface IngestResponse {
  status: string;
  chunks_ingested: number;
  directory: string;
}

export const ingestCodebase = async (directoryPath: string): Promise<IngestResponse> => {
  const response = await fetch(`${API_BASE_URL}/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ directory_path: directoryPath }),
  });
  if (!response.ok) {
    throw new Error("Failed to ingest codebase");
  }
  return response.json();
};

export const queryCodebase = async (question: string): Promise<QueryResponse> => {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error("Failed to query codebase");
  }
  return response.json();
};
