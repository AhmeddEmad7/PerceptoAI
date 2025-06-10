'use client';

import { useState, useRef } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { MessageSquare, Settings, ChevronLeft, Menu, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useQuery } from '@tanstack/react-query';
import type { Conversation } from '@/lib/types';

async function fetchConversations(): Promise<Conversation[]> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/conversations`
  );
  if (!response.ok) {
    throw new Error('Failed to fetch conversations');
  }
  return response.json();
}

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const pathname = usePathname();
  const router = useRouter();
  const sidebarRef = useRef<HTMLDivElement>(null);

  // Fetch conversations using TanStack Query
  const {
    data: conversations = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['conversations'],
    queryFn: fetchConversations,
  });

  const handleNewConversation = async () => {
    try {
      // Example: Create new conversation via API
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'New Conversation' }),
        }
      );
      if (!response.ok) throw new Error('Failed to create conversation');
      const newConversation = await response.json();
      router.push(`/conversations/${newConversation.id}`);
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  return (
    <>
      {/* Mobile menu button */}
      {!isOpen && (
        <Button
          variant='ghost'
          size='icon'
          className='fixed left-4 top-4 z-50 md:hidden'
          onClick={() => setIsOpen(!isOpen)}
        >
          <Menu className='h-5 w-5' />
        </Button>
      )}

      {/* Sidebar */}
      <div
        ref={sidebarRef}
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-background/80 backdrop-blur-md transition-transform duration-300 ease-in-out md:relative md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className='flex h-14 items-center justify-between border-b px-4'>
          <h1 className='text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-500 to-pink-500'>
            Percepton.AI
          </h1>
          <Button
            variant='ghost'
            size='icon'
            onClick={() => setIsOpen(false)}
            className='md:hidden'
          >
            <ChevronLeft className='h-5 w-5' />
          </Button>
        </div>

        <ScrollArea className='flex-1 px-2 py-4'>
          <div className='space-y-4'>
            <Button
              onClick={handleNewConversation}
              className='w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600'
              disabled={isLoading}
            >
              <Plus className='mr-2 h-4 w-4' />
              New Conversation
            </Button>

            {isLoading && (
              <div className='px-3 text-sm text-muted-foreground'>
                Loading...
              </div>
            )}
            {error && (
              <div className='px-3 text-sm text-destructive'>
                Error: {error.message}
              </div>
            )}

            <div className='space-y-1'>
              <TooltipProvider>
                {conversations.map((conversation) => (
                  <Link
                    key={conversation.id}
                    href={`/conversations/${conversation.id}`}
                    onClick={() => setIsOpen(false)}
                    className='block'
                  >
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div
                          className={cn(
                            'flex items-center rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent/50',
                            pathname === `/conversations/${conversation.id}`
                              ? 'bg-accent text-accent-foreground'
                              : 'text-muted-foreground'
                          )}
                        >
                          <MessageSquare className='mr-2 h-4 w-4 shrink-0' />
                          <span className='truncate'>{conversation.title}</span>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent side='right' align='start'>
                        {conversation.title}
                      </TooltipContent>
                    </Tooltip>
                  </Link>
                ))}
              </TooltipProvider>
            </div>
          </div>
        </ScrollArea>

        <div className='border-t p-4'>
          <Link href='/settings' onClick={() => setIsOpen(false)}>
            <div
              className={cn(
                'flex items-center rounded-md px-3 py-2 text-sm transition-colors hover:bg-accent/50',
                pathname === '/settings'
                  ? 'bg-accent text-accent-foreground'
                  : 'text-muted-foreground'
              )}
            >
              <Settings className='mr-2 h-4 w-4 shrink-0' />
              <span>Settings</span>
            </div>
          </Link>
        </div>
      </div>

      {/* Overlay */}
      {isOpen && (
        <div
          className='fixed inset-0 z-30 bg-background/80 backdrop-blur-sm md:hidden'
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
