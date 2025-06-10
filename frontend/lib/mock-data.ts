import type { Conversation, Voice } from './types';

const mockConversations: Conversation[] = [
  {
    id: 'conv-1',
    title: 'Understanding Quantum Computing',
    lastUpdated: new Date('2023-05-15T14:30:00'),
    messages: [
      {
        id: 'msg-1-1',
        role: 'user',
        content: 'Can you explain quantum computing in simple terms?',
        timestamp: new Date('2023-05-15T14:30:00'),
        image: '/images/PHOTO-2025-05-19-22-18-41.jpg'
      },
      {
        id: 'msg-1-2',
        role: 'assistant',
        content:
          "Quantum computing uses quantum bits or 'qubits' that can exist in multiple states simultaneously, unlike classical bits that are either 0 or 1. This allows quantum computers to process certain types of problems much faster than traditional computers. Think of it like being able to try many solutions at once instead of one at a time.",
        timestamp: new Date('2023-05-15T14:31:00'),
      },
      {
        id: 'msg-1-3',
        role: 'user',
        content: 'What are some practical applications of quantum computing?',
        timestamp: new Date('2023-05-15T14:32:00'),
      },
      {
        id: 'msg-1-4',
        role: 'assistant',
        content:
          'Quantum computing has several promising applications:\n\n1. **Cryptography**: Breaking and creating more secure encryption methods\n2. **Drug discovery**: Simulating molecular structures to develop new medicines faster\n3. **Optimization problems**: Solving complex logistics and supply chain challenges\n4. **Material science**: Designing new materials with specific properties\n5. **AI and machine learning**: Processing complex datasets more efficiently\n\nHowever, practical quantum computers with enough qubits to outperform classical computers for these tasks are still being developed.',
        timestamp: new Date('2023-05-15T14:33:00'),
      },
    ],
  },
  {
    id: 'conv-2',
    title: 'Climate Change Solutions',
    lastUpdated: new Date('2023-05-20T09:15:00'),
    messages: [
      {
        id: 'msg-2-1',
        role: 'user',
        content:
          'What are the most promising technologies to combat climate change?',
        timestamp: new Date('2023-05-20T09:15:00'),
        image: '/images/WhatsApp Image 2025-04-06 at 00.33.44.jpeg'
      },
      {
        id: 'msg-2-2',
        role: 'assistant',
        content:
          'Several promising technologies are being developed to address climate change:\n\n1. **Renewable energy**: Solar, wind, hydro, and geothermal power are becoming increasingly efficient and affordable.\n\n2. **Energy storage**: Advanced battery technologies and other storage solutions help address intermittency issues with renewables.\n\n3. **Carbon capture and storage (CCS)**: Technologies that capture CO₂ from power plants or directly from the air and store it underground.\n\n4. **Green hydrogen**: Using renewable electricity to produce hydrogen for energy storage or as a clean fuel.\n\n5. **Electric vehicles and sustainable transportation**: Reducing emissions from the transportation sector.\n\n6. **Smart grids and energy efficiency**: Optimizing energy use and reducing waste.\n\n7. **Plant-based and lab-grown alternatives**: Reducing emissions from agriculture and food production.\n\nThe most effective approach will likely involve a combination of these technologies alongside policy changes and behavioral shifts.',
        timestamp: new Date('2023-05-20T09:16:00'),
      },
      {
        id: 'msg-2-3',
        role: 'user',
        content:
          'Which of these technologies is closest to widespread adoption?',
        timestamp: new Date('2023-05-20T09:17:00'),
      },
      {
        id: 'msg-2-4',
        role: 'assistant',
        content:
          'Renewable energy technologies, particularly solar and wind power, are already being widely adopted globally. Their costs have fallen dramatically over the past decade, making them competitive with or cheaper than fossil fuels in many regions. Electric vehicles are also gaining significant market share, with many major automakers committing to phase out internal combustion engines in the coming decades. Energy efficiency measures and smart grid technologies are also being implemented in many developed countries. These technologies are not only technically mature but also economically viable, which accelerates their adoption compared to newer approaches like direct air capture or green hydrogen that are still scaling up.',
        timestamp: new Date('2023-05-20T09:18:00'),
      },
    ],
  },
  {
    id: 'conv-3',
    title: 'Future of AI',
    lastUpdated: new Date('2023-06-01T16:45:00'),
    messages: [
      {
        id: 'msg-3-1',
        role: 'user',
        content: 'How will AI change society in the next 10 years?',
        timestamp: new Date('2023-06-01T16:45:00'),
      },
      {
        id: 'msg-3-2',
        role: 'assistant',
        content:
          'In the next decade, AI is likely to transform society in several significant ways:\n\n**Work and Employment**:\n- Automation of routine cognitive and physical tasks\n- New job categories emerging around AI management and oversight\n- Shift toward more creative, strategic, and interpersonal roles\n- Potential for shorter work weeks as productivity increases\n\n**Healthcare**:\n- More accurate diagnostics and personalized treatment plans\n- AI-assisted surgery and care\n- Accelerated drug discovery and development\n- Preventative health monitoring through wearables and smart devices\n\n**Education**:\n- Personalized learning experiences tailored to individual students\n- AI tutors available 24/7\n- Transformation of teacher roles to focus more on mentorship\n\n**Transportation**:\n- Increased adoption of autonomous vehicles\n- Optimized traffic flow and public transportation\n- New models of vehicle ownership and use\n\n**Home and Daily Life**:\n- More capable smart homes and personal assistants\n- AI-curated entertainment and information\n- Enhanced accessibility tools for aging and disabled populations\n\nThese changes will bring both opportunities and challenges, including privacy concerns, potential inequality in access to AI benefits, and the need for new regulatory frameworks.',
        timestamp: new Date('2023-06-01T16:46:00'),
      },
      {
        id: 'msg-3-3',
        role: 'user',
        content: 'What are the biggest risks we should be concerned about?',
        timestamp: new Date('2023-06-01T16:47:00'),
      },
      {
        id: 'msg-3-4',
        role: 'assistant',
        content:
          "The biggest risks associated with AI advancement include:\n\n**Economic Disruption and Inequality**:\n- Job displacement occurring faster than new job creation\n- Concentration of AI benefits among tech companies and highly skilled workers\n- Widening economic inequality if transition policies aren't implemented\n\n**Privacy and Surveillance**:\n- Unprecedented capabilities for monitoring and analyzing human behavior\n- Potential misuse by governments or corporations\n- Erosion of privacy as AI systems process more personal data\n\n**Security and Autonomous Weapons**:\n- New forms of cyberattacks powered by AI\n- Potential development of lethal autonomous weapons\n- Security vulnerabilities in critical AI systems\n\n**Algorithmic Bias and Discrimination**:\n- Perpetuation or amplification of existing societal biases\n- Discriminatory outcomes in areas like hiring, lending, and criminal justice\n- Lack of transparency in how AI makes decisions\n\n**Concentration of Power**:\n- Control of advanced AI by a small number of companies or countries\n- Dependency on AI systems controlled by others\n\n**Alignment and Control**:\n- Ensuring AI systems reliably pursue intended goals\n- Managing increasingly autonomous systems\n- Long-term risks from more advanced systems\n\nAddressing these risks requires technical research, thoughtful policy, corporate responsibility, and international cooperation.",
        timestamp: new Date('2023-06-01T16:48:00'),
      },
    ],
  },
  {
    id: 'conv-4',
    title: 'Space Exploration',
    lastUpdated: new Date('2023-06-10T11:20:00'),
    messages: [
      {
        id: 'msg-4-1',
        role: 'user',
        content: "What's the current status of Mars exploration?",
        timestamp: new Date('2023-06-10T11:20:00'),
      },
      {
        id: 'msg-4-2',
        role: 'assistant',
        content:
          "Mars exploration is currently in an exciting phase with several active missions:\n\n**Active Rovers**:\n- NASA's Perseverance (landed February 2021) is exploring Jezero Crater, collecting samples for future return to Earth, and studying the planet's geology and past habitability.\n- NASA's Curiosity (landed 2012) continues to operate in Gale Crater, analyzing Martian soil and rocks.\n- China's Zhurong rover (landed May 2021) explored Utopia Planitia until it entered hibernation.\n\n**Orbiters**:\n- Several spacecraft are orbiting Mars, including NASA's MAVEN and Mars Reconnaissance Orbiter, ESA's Mars Express and Trace Gas Orbiter, India's Mars Orbiter Mission, and UAE's Hope orbiter.\n- These orbiters study Mars' atmosphere, surface, and provide communication relay for surface missions.\n\n**Future Missions**:\n- NASA and ESA are planning a Mars Sample Return mission to retrieve the samples collected by Perseverance.\n- Several space agencies and private companies have proposed human missions to Mars in the 2030s and beyond.\n\nThe focus of current Mars exploration is on understanding the planet's past habitability, searching for signs of ancient microbial life, characterizing the climate and geology, and preparing for eventual human exploration.",
        timestamp: new Date('2023-06-10T11:21:00'),
      },
      {
        id: 'msg-4-3',
        role: 'user',
        content: 'When do you think humans will actually land on Mars?',
        timestamp: new Date('2023-06-10T11:22:00'),
      },
      {
        id: 'msg-4-4',
        role: 'assistant',
        content:
          "A human Mars landing is likely to occur between the mid-2030s and 2040s, though timelines remain uncertain. NASA has set goals for missions in the late 2030s or early 2040s, while SpaceX has more ambitious timelines but faces significant technical challenges. The mission requires solving critical issues like radiation protection, long-duration life support, landing heavy payloads safely, and developing reliable propulsion systems. International cooperation could accelerate progress, but funding stability and political support are essential factors that could either advance or delay these missions. The first human Mars mission will represent one of humanity's greatest technological achievements, requiring solutions to challenges beyond those faced during the Apollo program.",
        timestamp: new Date('2023-06-10T11:23:00'),
      },
    ],
  },
  {
    id: 'conv-5',
    title: 'Nutrition and Diet',
    lastUpdated: new Date('2023-06-15T08:30:00'),
    messages: [
      {
        id: 'msg-5-1',
        role: 'user',
        content: "What's the scientific consensus on the healthiest diet?",
        timestamp: new Date('2023-06-15T08:30:00'),
      },
      {
        id: 'msg-5-2',
        role: 'assistant',
        content:
          'The scientific consensus on the healthiest diet centers around patterns rather than a single "perfect" diet. Research consistently supports diets rich in minimally processed plant foods, with limited ultra-processed foods and added sugars. The Mediterranean diet has the strongest evidence base for long-term health benefits, featuring vegetables, fruits, whole grains, legumes, nuts, olive oil, moderate fish, and limited red meat. Other beneficial patterns include the traditional Okinawan diet, the DASH diet, and plant-forward approaches.\n\nNutrition science recognizes individual variation in responses to foods based on genetics, gut microbiome, lifestyle, and health status. This supports personalized approaches rather than one-size-fits-all recommendations. Common principles across healthy dietary patterns include emphasizing whole foods, plant predominance, healthy fats, fiber-rich carbohydrates, and adequate protein while limiting ultra-processed foods, added sugars, and excessive salt.',
        timestamp: new Date('2023-06-15T08:31:00'),
      },
      {
        id: 'msg-5-3',
        role: 'user',
        content:
          'What about intermittent fasting? Is there good evidence for it?',
        timestamp: new Date('2023-06-15T08:32:00'),
      },
      {
        id: 'msg-5-4',
        role: 'assistant',
        content:
          "Intermittent fasting (IF) has shown promising results in research, but the evidence is still evolving. Here's what the current science suggests:\n\n**Evidence for benefits**:\n- Weight management: IF can help reduce caloric intake and may aid weight loss comparable to continuous calorie restriction.\n- Metabolic health: Some studies show improvements in insulin sensitivity, blood sugar control, and lipid profiles.\n- Cellular repair: Fasting periods may trigger autophagy (cellular cleaning processes) and reduce oxidative stress.\n- Longevity: Animal studies show lifespan extension, though human evidence is limited.\n\n**Limitations of current evidence**:\n- Many studies are short-term, small-scale, or conducted in animals.\n- Long-term adherence and effects remain understudied.\n- Results vary by IF protocol (time-restricted eating, alternate-day fasting, 5:2 method, etc.).\n- Individual responses differ based on age, sex, health status, and genetics.\n\n**Practical considerations**:\n- IF isn't suitable for everyone, particularly pregnant women, those with a history of eating disorders, people with diabetes on medication, or individuals with increased caloric needs.\n- The quality of food consumed during eating windows remains important.\n- Benefits may come partly from overall calorie reduction rather than fasting itself.\n\nWhile IF shows promise as a flexible approach to improving health for some individuals, it's not a one-size-fits-all solution, and more research is needed on long-term effects.",
        timestamp: new Date('2023-06-15T08:33:00'),
      },
    ],
  },
];

const mockVoices: Voice[] = [
  {
    id: 'voice-1',
    name: 'Nova',
    description: 'A clear, professional female voice',
    gradient: 'bg-gradient-to-br from-purple-500 to-pink-500',
    style: {
      background: 'linear-gradient(to right, #6a11cb, #2575fc)',
    },
  },
  {
    id: 'voice-2',
    name: 'Quantum',
    description: 'A deep, authoritative male voice',
    gradient: 'bg-gradient-to-br from-blue-500 to-teal-400',
    style: {
      background: 'linear-gradient(to right, #00c6ff, #0072ff)',
    },
  },
  {
    id: 'voice-3',
    name: 'Echo',
    description: 'A warm, friendly gender-neutral voice',
    gradient: 'bg-gradient-to-br from-amber-500 to-red-500',
    style: {
      background: 'linear-gradient(to right, #ff758c, #ff7eb3)',
    },
  },
  {
    id: 'voice-4',
    name: 'Nebula',
    description: 'A soft, calming female voice',
    gradient: 'bg-gradient-to-br from-indigo-500 to-purple-500',
    style: {
      background: 'linear-gradient(to right, #ff6a00, #ee0979)',
    },
  },
  {
    id: 'voice-5',
    name: 'Orion',
    description: 'An energetic, youthful male voice',
    gradient: 'bg-gradient-to-br from-green-500 to-teal-400',
    style: {
      background: 'linear-gradient(to right, #00c6ff, #0072ff)',
    },
  },
  {
    id: 'voice-6',
    name: 'Astra',
    description: 'A sophisticated, elegant female voice',
    gradient: 'bg-gradient-to-br from-rose-500 to-orange-400',
    style: {
      background: 'linear-gradient(to right, #ff758c, #ff7eb3)',
    },
  },
];

let dynamicConversations: Conversation[] = [];

export function createNewConversation(id: string): Conversation {
  const newConversation: Conversation = {
    id,
    title: 'New Conversation',
    lastUpdated: new Date(),
    messages: [
      {
        id: `${id}-msg-1`,
        role: 'assistant',
        content: 'How can I help you today?',
        timestamp: new Date(),
      },
    ],
  };

  dynamicConversations.push(newConversation);
  return newConversation;
}

export function getMockConversations(): Conversation[] {
  return [...mockConversations, ...dynamicConversations];
}

export function getMockConversation(id: string): Conversation {
  // First check dynamic conversations
  const dynamicConversation = dynamicConversations.find((conv) => conv.id === id);
  if (dynamicConversation) {
    return dynamicConversation;
  }

  // Then check mock conversations
  const mockConversation = mockConversations.find((conv) => conv.id === id);
  if (mockConversation) {
    return mockConversation;
  }

  // If not found, create a new conversation
  if (id.startsWith('conv-new')) {
    return createNewConversation(id);
  }

  throw new Error(`Conversation with id ${id} not found`);
}

export function getMockVoices(): Voice[] {
  return mockVoices;
}
