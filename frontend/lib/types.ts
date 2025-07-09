export interface Message {
  message_id: number;
  conversation_id: number;
  user_input: string;
  ai_response: string;
  image?: string;
  audioUrl?: string;
}

export interface Conversation {
  id: string;
  title: string;
}

export interface Voice {
  id: string;
  name: string;
  description: string;
  gradient: string;
  style?: React.CSSProperties;
}
