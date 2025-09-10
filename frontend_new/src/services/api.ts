export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const sendMessage = async (message: string): Promise<string> => {
  try {
    console.log('Sending message to API');

    // Use relative URL for Vercel deployment
    const apiUrl = import.meta.env.VITE_API_URL || '/api/chat';

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        question: message
      }),
    });

    console.log('Response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`Server responded with ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('Response data:', data);
    return data.answer || 'Sorry, I could not process your request.';
  } catch (error) {
    console.error('Error sending message:', error);
    return 'Sorry, there was an error processing your request. Please try again.';
  }
};

export const createNewChat = (): string => {
  return `chat-${Date.now()}`;
};

export const saveMessages = (chatId: string, messages: Message[]) => {
  try {
    localStorage.setItem(`chat_${chatId}`, JSON.stringify(messages));
  } catch (error) {
    console.error('Error saving messages:', error);
  }
};

export const loadMessages = (chatId: string): Message[] => {
  try {
    const saved = localStorage.getItem(`chat_${chatId}`);
    if (saved) {
      const messages = JSON.parse(saved);
      // Convert string timestamps back to Date objects
      return messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));
    }
  } catch (error) {
    console.error('Error loading messages:', error);
  }
  return [];
};
