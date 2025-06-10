import { useState, useRef } from 'react';
import { Voice, voices } from '@/lib/voices';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Play, Square } from 'lucide-react';

interface VoiceSelectorProps {
  onVoiceSelect?: (voice: Voice) => void;
  selectedVoiceId?: string;
}

export function VoiceSelector({ onVoiceSelect, selectedVoiceId }: VoiceSelectorProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentVoice, setCurrentVoice] = useState<Voice | undefined>(
    voices.find(v => v.id === selectedVoiceId) || voices[0]
  );

  const handleVoiceChange = (voiceId: string) => {
    const voice = voices.find(v => v.id === voiceId);
    if (voice) {
      setCurrentVoice(voice);
      onVoiceSelect?.(voice);
      // Stop any playing audio when changing voice
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setIsPlaying(false);
      }
    }
  };

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleAudioEnd = () => {
    setIsPlaying(false);
  };

  return (
    <div className="flex items-center gap-4">
      <Select value={currentVoice?.id} onValueChange={handleVoiceChange}>
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Select a voice" />
        </SelectTrigger>
        <SelectContent>
          {voices.map((voice) => (
            <SelectItem key={voice.id} value={voice.id}>
              {voice.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        variant="outline"
        size="icon"
        onClick={togglePlay}
        className="w-8 h-8"
      >
        {isPlaying ? (
          <Square className="h-4 w-4" />
        ) : (
          <Play className="h-4 w-4" />
        )}
      </Button>

      <audio
        ref={audioRef}
        src={currentVoice?.audioPath}
        onEnded={handleAudioEnd}
        className="hidden"
      />

      {currentVoice?.description && (
        <p className="text-sm text-muted-foreground">{currentVoice.description}</p>
      )}
    </div>
  );
} 