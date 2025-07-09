import { VoiceSettings } from '@/components/voice-settings';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function SettingsPage() {
  return (
    <div className='container max-w-4xl py-6 space-y-8'>
      <div className='flex items-center space-x-4'>
        <Link href='/conversations'>
          <Button variant='ghost' size='icon'>
            <ArrowLeft className='h-5 w-5' />
            <span className='sr-only'>Back</span>
          </Button>
        </Link>
        <div className='space-y-1'>
          <h1 className='text-3xl font-bold'>Settings</h1>
          <p className='text-muted-foreground'>
            Customize your PerceptoAI experience
          </p>
        </div>
      </div>

      <VoiceSettings />
    </div>
  );
}
