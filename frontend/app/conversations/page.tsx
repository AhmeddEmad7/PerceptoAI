'use client';

import { useRouter } from 'next/navigation';
import { EmptyState } from "@/components/empty-state"
import { Button } from "@/components/ui/button"
import { Plus } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'; // Import useQueryClient

export default function ConversationsPage() {
  const router = useRouter();
  const queryClient = useQueryClient(); // Initialize useQueryClient

  const handleNewConversation = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      if (!response.ok) throw new Error('Failed to create conversation');
      const newConversation = await response.json();
      queryClient.invalidateQueries({ queryKey: ['conversations'] }); // Invalidate and refetch conversations
      router.push(`/conversations/${newConversation.conversation_id}`);
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  return (
    <div className="flex h-full items-center justify-center">
      <EmptyState
        title="No conversation selected"
        description="Start a new conversation or select one from the sidebar."
        action={
          <Button
            onClick={handleNewConversation}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600"
          >
            <Plus className="mr-2 h-4 w-4" />
            New Conversation
          </Button>
        }
      />
    </div>
  )
}
