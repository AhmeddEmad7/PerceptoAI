'use client';

import { useEffect, useRef } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { MessageItem } from '@/components/message-item';
import { useRouter } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Conversation } from '@/lib/types';

interface ApiMessage {
  message_id: number;
  conversation_id: number;
  user_input: string;
  ai_response: string;
  image?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  image?: string;
}

async function fetchMessages(conversationId: string): Promise<Message[]> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/conversations/${conversationId}`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  const apiMessages: ApiMessage[] = await response.json();

  const messages: Message[] = [];
  apiMessages.forEach((msg) => {
    messages.push({
      id: `${msg.message_id}-user`,
      role: 'user',
      content: msg.user_input,
      image: msg.image,
    });
    messages.push({
      id: `${msg.message_id}-assistant`,
      role: 'assistant',
      content: msg.ai_response,
    });
  });

  return messages;
}

interface ConversationViewProps {
  id: string;
}

export function ConversationView({ id }: ConversationViewProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const {
    data: messages = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => fetchMessages(id),
  });

  const queryClient = useQueryClient();

  const conversations: Conversation[] | undefined = queryClient.getQueryData([
    'conversations',
  ]);

  useEffect(() => {
    if (messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className='flex h-full flex-col'>
      <div className='flex items-center border-b p-4'>
        <Button
          variant='ghost'
          size='icon'
          className='mr-2 md:hidden'
          onClick={() => router.back()}
        >
          <ArrowLeft className='h-5 w-5' />
        </Button>
        <h2 className='text-lg font-medium'>
          {conversations?.find((c) => Number(c.id) === +id)?.title ||
            'Conversation'}
        </h2>
      </div>

      <div className='flex-1 overflow-y-auto p-4'>
        {isLoading && (
          <div className='text-center text-sm text-muted-foreground'>
            Loading messages...
          </div>
        )}
        {error && (
          <div className='text-center text-sm text-destructive'>
            Error: {error.message}
          </div>
        )}
        {!isLoading && messages.length === 0 && (
          <div className='text-center text-sm text-muted-foreground'>
            No messages yet
          </div>
        )}
        <div className='space-y-6'>
          {messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}
