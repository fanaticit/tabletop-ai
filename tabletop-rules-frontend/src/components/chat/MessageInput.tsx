// src/components/chat/MessageInput.tsx
import React from 'react';

interface MessageInputProps {
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
  placeholder: string;
}

export const MessageInput: React.FC<MessageInputProps> = () => {
  return <div>MessageInput Placeholder</div>;
};