export interface AskRequest {
  chatId: string;
  question: string;
}

export interface AskResponse {
  chatId: string;
  question: string;
  answer: string;
  sql?: string;         // pra mostrar transparência
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sql?: string;         // mensagem do assistente pode ter o SQL
  timestamp: Date;
}