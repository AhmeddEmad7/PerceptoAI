'use client';

import { useEffect, useRef, useState } from 'react';
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
  audioUrl?: string; // Add audioUrl to the Message interface
}

interface ProcessedAudioResponse {
  transcription: string;
  prompt_type: string;
  response: string;
  audio_response_base64: string;
  voice: string;
  conversation_id: number;
  message_id: number;
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

async function processAudio(audioBlob: Blob, conversationId: string): Promise<ProcessedAudioResponse> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.webm');
  
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/process_audio?conversation_id=${conversationId}`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to process audio: ${response.status} ${response.statusText} - ${errorText}`);
  }

  const responseJson: ProcessedAudioResponse = await response.json();
  return responseJson;
}

interface ConversationViewProps {
  id: string;
}

export function ConversationView({ id }: ConversationViewProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [rawAudioBlob, setRawAudioBlob] = useState<Blob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
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

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setRawAudioBlob(audioBlob);
        setIsRecording(false);
        
        if (audioBlob) {
          try {
            setIsProcessing(true);
            const processedData = await processAudio(audioBlob, id);
            
            queryClient.setQueryData(['messages', id], (oldMessages: Message[] | undefined) => {
              const audioUrl = `data:audio/mpeg;base64,${processedData.audio_response_base64}`;
              
              const newUserMessage: Message = {
                id: `user-${processedData.message_id}`,
                role: 'user',
                content: processedData.transcription,
              };
              const newAiMessage: Message = {
                id: `assistant-${processedData.message_id}`,
                role: 'assistant',
                content: processedData.response,
                audioUrl: audioUrl,
              };
              
              const updatedMessages = oldMessages ? 
                oldMessages.filter(msg => !(msg.content === 'Processing audio...')).concat([newUserMessage, newAiMessage])
                : [newUserMessage, newAiMessage];

              return updatedMessages;
            });

            queryClient.invalidateQueries({ queryKey: ['conversations'] });
            setRawAudioBlob(null);
            setIsProcessing(false);
          } catch (err) {
            console.error('Error processing audio:', err);
            setIsProcessing(false);
          }
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRawAudioBlob(null);
    } catch (err) {
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

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

      <div className='flex items-center justify-center p-4 border-t'>
        {!isRecording && !isProcessing ? (
          <Button onClick={startRecording} className='bg-green-500 hover:bg-green-600 text-white'>
            Start Recording
          </Button>
        ) : isRecording ? (
          <Button onClick={stopRecording} className='bg-red-500 hover:bg-red-600 text-white'>
            Stop Recording
          </Button>
        ) : isProcessing ? (
          <Button className='ml-4 bg-blue-500 hover:bg-blue-600 text-white' disabled>
            Processing...
          </Button>
        ) : null}
      </div>
    </div>
  );
}
