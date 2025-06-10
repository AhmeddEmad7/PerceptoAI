'use client';

import { useRouter } from 'next/navigation';
import { EmptyState } from "@/components/empty-state"
import { Button } from "@/components/ui/button"
import { Plus } from 'lucide-react'

export default function ConversationsPage() {
  const router = useRouter();

  const handleNewConversation = () => {
    // In a real app, this would create a new conversation in the backend
    const newId = 'conv-new';
    router.push(`/conversations/${newId}`);
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
