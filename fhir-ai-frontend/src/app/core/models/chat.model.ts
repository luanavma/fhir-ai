import { AISummary } from "./ai-summary.model";
import { RegionData } from "./region.model";

export interface AskRequest {
  chatId: string;
  question: string;
}

export interface AskResponse {
  answer: string;
  regions: RegionData[];
  summary: AISummary | null;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  timestamp: Date;
}