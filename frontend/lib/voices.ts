export interface Voice {
  id: string;
  name: string;
  audioPath: string;
  description?: string;
}

export const voices: Voice[] = [
  {
    id: 'echo',
    name: 'ECHO',
    audioPath: '/voices/ECHO.mp3',
    description: 'A clear and resonant voice with natural echo characteristics'
  },
  {
    id: 'nebula',
    name: 'Nebula',
    audioPath: '/voices/Nebula.mp3',
    description: 'A mysterious and ethereal voice with cosmic undertones'
  },
  {
    id: 'astra',
    name: 'ASTRA',
    audioPath: '/voices/ASTRA.mp3',
    description: 'A bright and celestial voice with stellar qualities'
  },
  {
    id: 'orion',
    name: 'Orion',
    audioPath: '/voices/Orion.mp3',
    description: 'A bold and powerful voice with cosmic energy'
  },
  {
    id: 'nova',
    name: 'NOVA',
    audioPath: '/voices/NOVA.mp3',
    description: 'A dynamic and explosive voice with stellar brilliance'
  },
  {
    id: 'quantum',
    name: 'Quantum',
    audioPath: '/voices/Quantum.mp3',
    description: 'A precise and calculated voice with quantum properties'
  }
]; 