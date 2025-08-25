import React, { useState, useCallback } from 'react';

interface CollapsibleSectionProps {
  title: string;
  children: React.ReactNode;
  initialExpanded?: boolean;
  className?: string;
  level?: number;
}

const ChevronIcon: React.FC<{ isExpanded: boolean }> = ({ isExpanded }) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="currentColor"
    style={{
      transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
      transition: 'transform 0.2s ease',
    }}
  >
    <path
      fillRule="evenodd"
      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
      clipRule="evenodd"
    />
  </svg>
);

export const CollapsibleSection: React.FC<CollapsibleSectionProps> = ({
  title,
  children,
  initialExpanded = false,
  className = '',
  level = 1,
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  const toggleExpanded = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleExpanded();
    }
  }, [toggleExpanded]);

  const buttonStyle = {
    display: 'flex',
    alignItems: 'center',
    width: '100%',
    textAlign: 'left' as const,
    padding: '12px',
    border: 'none',
    background: 'none',
    cursor: 'pointer',
    borderRadius: '8px',
    transition: 'background-color 0.2s ease',
    fontSize: level === 1 ? '16px' : '14px',
    fontWeight: level === 1 ? '600' : '500',
    color: '#374151',
  };

  const contentStyle = {
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    maxHeight: isExpanded ? '1000px' : '0',
    opacity: isExpanded ? 1 : 0,
  };

  const innerContentStyle = {
    paddingLeft: level === 1 ? '44px' : '32px',
    paddingRight: '16px',
    paddingBottom: isExpanded ? '12px' : '0',
  };

  return (
    <div className={`collapsible-section ${className}`}>
      <button
        onClick={toggleExpanded}
        onKeyDown={handleKeyDown}
        aria-expanded={isExpanded}
        aria-controls={`section-content-${title.replace(/\s+/g, '-').toLowerCase()}`}
        style={buttonStyle}
        onMouseEnter={(e) => {
          (e.target as HTMLElement).style.backgroundColor = '#f9fafb';
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLElement).style.backgroundColor = 'transparent';
        }}
      >
        <ChevronIcon isExpanded={isExpanded} />
        <span style={{ marginLeft: '8px' }}>{title}</span>
      </button>
      
      <div
        id={`section-content-${title.replace(/\s+/g, '-').toLowerCase()}`}
        style={contentStyle}
        aria-hidden={!isExpanded}
      >
        <div style={innerContentStyle}>
          {children}
        </div>
      </div>
    </div>
  );
};