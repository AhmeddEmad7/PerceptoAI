export interface Voice {
  id: string;
  name: string;
  audioPath: string;
  description?: string;
  isArabic?: boolean;
  background: string;
}

export const voices: Voice[] = [
  {
    id: 'Bella',
    name: 'Bella',
    audioPath: '/voices/Bella.mp3',
    description: 'A clear and resonant voice with natural echo characteristics',
    background: 'linear-gradient(to right, #ff758c, #ff7eb3)',
  },
  {
    id: 'Antoni',
    name: 'Antoni',
    audioPath: '/voices/Antoni.mp3',
    description: 'A mysterious and ethereal voice with cosmic undertones',
    background: 'linear-gradient(to right, #6a11cb, #2575fc)',
  },
  {
    id: 'Elli',
    name: 'Elli',
    audioPath: '/voices/Elli.mp3',
    description: 'A bright and celestial voice with stellar qualities',
    background: 'linear-gradient(to right, #00c6ff, #0072ff)',
  },
  {
    id: 'Josh',
    name: 'Josh',
    audioPath: '/voices/Josh.mp3',
    description: 'A bold and powerful voice with cosmic energy',
    background: 'linear-gradient(to right, #ff8c42, #ff5733)',
  },
  {
    id: 'Sarah',
    name: 'Sarah',
    audioPath: '/voices/Sarah.mp3',
    description: 'A dynamic and explosive voice with stellar brilliance',
    isArabic: true,
    background: 'linear-gradient(to right, #6a11cb, #2575fc)',
  },
  {
    id: 'Brian',
    name: 'Brian',
    audioPath: '/voices/Brian.mp3',
    description: 'A precise and calculated voice with Brian properties',
    isArabic: true,
    background: 'linear-gradient(to right, #00c6ff, #0072ff)',
  },
];
