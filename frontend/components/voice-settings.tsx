'use client';

import { useState, useRef } from 'react';
import { Play, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { voices } from '@/lib/voices';

const voiceStyles = {
  'echo': {
    background: 'linear-gradient(to right, #ff758c, #ff7eb3)',
  },
  'nebula': {
    background: 'linear-gradient(to right, #6a11cb, #2575fc)',
  },
  'astra': {
    background: 'linear-gradient(to right, #00c6ff, #0072ff)',
  },
  'orion': {
    background: 'linear-gradient(to right, #ff8c42, #ff5733)',
  },
  'nova': {
    background: 'linear-gradient(to right, #6a11cb, #2575fc)',
  },
  'quantum': {
    background: 'linear-gradient(to right, #00c6ff, #0072ff)',
  },
};

export function VoiceSettings() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);
  const currentVoice = voices[currentIndex];

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
              style={voiceStyles[currentVoice.id as keyof typeof voiceStyles]}
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
          <Button onClick={handlePlayVoice} className='px-6'>
            <Play className='h-4 w-4 mr-2' />
            Play Sample
          </Button>
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
