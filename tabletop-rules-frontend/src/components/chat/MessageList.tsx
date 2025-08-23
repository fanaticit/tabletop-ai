import React, { useEffect, useRef } from 'react';
import { Message, RuleChunk } from '../../stores/conversationStore';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageComponent: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px',
      }}
    >
      <div
        style={{
          maxWidth: '70%',
          padding: '12px 16px',
          borderRadius: '12px',
          backgroundColor: isUser ? '#007bff' : '#f1f1f1',
          color: isUser ? 'white' : '#333',
          wordWrap: 'break-word',
        }}
      >
        <div style={{ marginBottom: message.sources ? '8px' : '0' }}>
          {message.content}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div style={{ marginTop: '8px', fontSize: '12px', opacity: 0.8 }}>
            <strong>Sources:</strong>
            {message.sources.map((source, index) => (
              <div key={index} style={{ marginTop: '4px' }}>
                • {source.title} ({source.game_id})
              </div>
            ))}
          </div>
        )}
        <div
          style={{
            fontSize: '11px',
            opacity: 0.7,
            marginTop: '4px',
            textAlign: 'right',
          }}
        >
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

const LoadingIndicator: React.FC = () => (
  <div
    style={{
      display: 'flex',
      justifyContent: 'flex-start',
      marginBottom: '16px',
    }}
  >
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '12px',
        backgroundColor: '#f1f1f1',
        color: '#666',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <span>Thinking</span>
        <span className="loading-dots">...</span>
      </div>
    </div>
  </div>
);

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {messages.length === 0 && !isLoading && (
        <div
          style={{
            textAlign: 'center',
            color: '#666',
            fontSize: '14px',
            padding: '32px',
          }}
        >
          Start a conversation by asking a question about the game rules!
        </div>
      )}
      
      {messages.map((message) => (
        <MessageComponent key={message.id} message={message} />
      ))}
      
      {isLoading && <LoadingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  );
};