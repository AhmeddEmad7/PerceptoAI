'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Play,
  ChevronLeft,
  ChevronRight,
  CheckCircle2Icon,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { voices } from '@/lib/voices';
import { Badge } from './ui/badge';
import { useMutation, useQuery } from '@tanstack/react-query';
import { toast } from './ui/use-toast';

interface ApiVoice {
  voice: string;
}

export function VoiceSettings() {
  const { data: voice = '', refetch } = useQuery({
    queryKey: ['voice'],
    queryFn: async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/voice`);
      if (!response.ok) {
        throw new Error('Failed to fetch voice');
      }

      const data = (await response.json()) as ApiVoice;
      return data.voice;
    },
  });

  const { mutate: updateVoice, isPending: isUpdatingVoice } = useMutation({
    mutationFn: async (voice: string) => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/voice?voice=${voice}`,
        {
          method: 'PUT',
        }
      );
      if (!response.ok) {
        throw new Error('Failed to update voice');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Voice updated successfully',
        description: 'Your AI assistant voice has been updated.',
      });
      refetch();
    },
    onError: (error) => {
      toast({
        title: 'Error updating voice',
        description: 'Failed to update the voice. Please try again.',
        variant: 'destructive',
      });
    },
  });

  const [currentIndex, setCurrentIndex] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);
  const currentVoice = voices[currentIndex];

  useEffect(() => {
    setCurrentIndex(
      voices.findIndex((v) => v.id === voice) !== -1
        ? voices.findIndex((v) => v.id === voice)
        : 0
    );
    if (audioRef.current) {
      audioRef.current.src = currentVoice.audioPath;
    }
  }, [voice]);

  const handlePlayVoice = () => {
    if (audioRef.current) {
      audioRef.current.src = currentVoice.audioPath;
      audioRef.current.play().catch((error) => {
        console.error('Error playing audio:', error);
      });
    }
  };

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : prev));
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev < voices.length - 1 ? prev + 1 : prev));
  };

  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold mb-4'>AI Voice</h2>
        <p className='text-muted-foreground mb-6'>
          Choose a voice for your AI assistant
        </p>
      </div>

      <div className='flex flex-col items-center space-y-6'>
        <div className='flex items-center justify-center w-full'>
          <Button
            variant='ghost'
            size='icon'
            onClick={goToPrevious}
            disabled={currentIndex === 0}
            className='mr-4'
          >
            <ChevronLeft className='h-6 w-6' />
            <span className='sr-only'>Previous voice</span>
          </Button>

          <div className='relative'>
            <div
              className={cn(
                'w-[200px] h-[200px] rounded-full animate-gradient-x flex items-center justify-center'
              )}
              style={{
                background: currentVoice.background,
              }}
            >
              <div className='absolute inset-0 rounded-full animate-pulse opacity-20 bg-white'></div>
              <div className='z-10 bg-background/10 backdrop-blur-sm rounded-full w-[180px] h-[180px] flex items-center justify-center'>
                <div className='text-center text-white'>
                  <h3 className='text-2xl font-bold mb-2'>
                    {currentVoice.name}
                  </h3>
                </div>
              </div>
            </div>
          </div>

          <Button
            variant='ghost'
            size='icon'
            onClick={goToNext}
            disabled={currentIndex === voices.length - 1}
            className='ml-4'
          >
            <ChevronRight className='h-6 w-6' />
            <span className='sr-only'>Next voice</span>
          </Button>
        </div>

        <div className='text-center'>
          <p className='text-muted-foreground mb-4'>
            {currentVoice.description}
          </p>
          <div className='flex flex-col gap-2 items-center'>
            {currentVoice.isArabic && <Badge>Supports Arabic</Badge>}
            <Button onClick={handlePlayVoice} className='px-6'>
              <Play className='h-4 w-4 mr-2' />
              Play Sample
            </Button>
            {voice !== currentVoice.id && (
              <Button
                onClick={() => updateVoice(currentVoice.id)}
                disabled={isUpdatingVoice}
                className='px-6'
              >
                <CheckCircle2Icon />
                {isUpdatingVoice ? 'Updating...' : 'Select'}
              </Button>
            )}
            {voice === currentVoice.id && (
              <Badge className='bg-green-500 text-white hover:bg-green-500/80'>
                Selected
              </Badge>
            )}
          </div>
        </div>

        <div className='flex justify-center mt-6'>
          {voices.map((_, index) => (
            <button
              key={index}
              className={cn(
                'w-2 h-2 mx-1 rounded-full transition-all',
                index === currentIndex ? 'bg-primary w-4' : 'bg-muted'
              )}
              onClick={() => setCurrentIndex(index)}
              aria-label={`Go to voice ${index + 1}`}
            />
          ))}
        </div>
      </div>

      <audio ref={audioRef} className='hidden' />
    </div>
  );
}
