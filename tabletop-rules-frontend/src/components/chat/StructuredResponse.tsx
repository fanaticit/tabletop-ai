import React from 'react';
import { CollapsibleSection } from './CollapsibleSection';

export interface RuleSection {
  id: string;
  title: string;
  content: string;
  type: 'summary' | 'explanation' | 'examples' | 'edge_cases';
  level: number;
  collapsible: boolean;
  expanded: boolean;
  subsections?: RuleSection[];
}

export interface RuleSource {
  type: 'rulebook' | 'faq' | 'designer_notes' | 'community';
  reference: string;
  url?: string;
  page?: number;
}

export interface StructuredRuleResponse {
  id: string;
  content: {
    summary: {
      text: string;
      confidence: number;
    };
    sections: RuleSection[];
    sources: RuleSource[];
  };
}

interface StructuredResponseProps {
  response: StructuredRuleResponse;
}

const ConfidenceIndicator: React.FC<{ confidence: number }> = ({ confidence }) => {
  const percentage = Math.round(confidence * 100);
  const color = confidence >= 0.8 ? '#10b981' : confidence >= 0.6 ? '#f59e0b' : '#ef4444';
  
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
      <span style={{ fontSize: '12px', color: '#6b7280' }}>Confidence:</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <div
          style={{
            width: '40px',
            height: '4px',
            backgroundColor: '#e5e7eb',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${percentage}%`,
              height: '100%',
              backgroundColor: color,
              transition: 'width 0.3s ease',
            }}
          />
        </div>
        <span style={{ fontSize: '12px', color, fontWeight: '500' }}>
          {percentage}%
        </span>
      </div>
    </div>
  );
};

const RuleSectionComponent: React.FC<{ section: RuleSection }> = ({ section }) => {
  // Format content with basic markdown support
  const formatContent = (content: string) => {
    // Simple markdown parsing for bold text and bullet points
    let formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^• (.+)$/gm, '<li>$1</li>')
      .replace(/\n\n/g, '<br><br>');
    
    // Wrap consecutive list items in ul tags
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    return formatted;
  };

  const sectionStyle = {
    marginBottom: '16px',
    border: section.level === 1 ? '1px solid #e5e7eb' : 'none',
    borderRadius: '8px',
    backgroundColor: section.level === 1 ? '#ffffff' : 'transparent',
  };

  if (!section.collapsible) {
    return (
      <div style={sectionStyle}>
        <div style={{ padding: '16px' }}>
          <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: '600' }}>
            {section.title}
          </h4>
          <div
            style={{ 
              fontSize: '14px', 
              lineHeight: '1.5', 
              color: '#374151' 
            }}
            dangerouslySetInnerHTML={{ __html: formatContent(section.content) }}
          />
        </div>
      </div>
    );
  }

  return (
    <div style={sectionStyle}>
      <CollapsibleSection
        title={section.title}
        initialExpanded={section.expanded}
        level={section.level}
      >
        <div
          style={{ 
            fontSize: '14px', 
            lineHeight: '1.5', 
            color: '#374151' 
          }}
          dangerouslySetInnerHTML={{ __html: formatContent(section.content) }}
        />
        {section.subsections && section.subsections.map(subsection => (
          <RuleSectionComponent key={subsection.id} section={subsection} />
        ))}
      </CollapsibleSection>
    </div>
  );
};

const SourcesSection: React.FC<{ sources: RuleSource[] }> = ({ sources }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'rulebook': return '📚';
      case 'faq': return '❓';
      case 'designer_notes': return '✍️';
      case 'community': return '👥';
      default: return '📄';
    }
  };

  return (
    <CollapsibleSection 
      title="Rule Sources" 
      initialExpanded={false}
      className="sources-section"
    >
      <div style={{ marginTop: '8px' }}>
        {sources.map((source, index) => (
          <div 
            key={index} 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              marginBottom: '8px',
              fontSize: '13px',
              color: '#6b7280'
            }}
          >
            <span style={{ marginRight: '8px', fontSize: '14px' }}>
              {getSourceIcon(source.type)}
            </span>
            <span style={{ fontWeight: '500', textTransform: 'capitalize', marginRight: '8px' }}>
              {source.type.replace('_', ' ')}:
            </span>
            <span>{source.reference}</span>
            {source.page && (
              <span style={{ marginLeft: '4px', fontStyle: 'italic' }}>
                (p. {source.page})
              </span>
            )}
            {source.url && (
              <a 
                href={source.url} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ 
                  marginLeft: '8px', 
                  color: '#3b82f6', 
                  textDecoration: 'none',
                  fontSize: '12px'
                }}
              >
                View Source →
              </a>
            )}
          </div>
        ))}
      </div>
    </CollapsibleSection>
  );
};

export const StructuredResponse: React.FC<StructuredResponseProps> = ({ response }) => {
  return (
    <div 
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: '12px',
        backgroundColor: '#ffffff',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        overflow: 'hidden',
      }}
    >
      {/* Summary - always visible (Level 1) */}
      <div 
        style={{
          padding: '16px',
          backgroundColor: '#f8fafc',
          borderBottom: '1px solid #e5e7eb',
        }}
      >
        <p 
          style={{
            margin: '0 0 8px 0',
            fontSize: '16px',
            fontWeight: '500',
            color: '#1f2937',
            lineHeight: '1.5',
          }}
        >
          {response.content.summary.text}
        </p>
        <ConfidenceIndicator confidence={response.content.summary.confidence} />
      </div>

      {/* Expandable sections (Level 2) */}
      <div style={{ padding: '16px' }}>
        {response.content.sections.map(section => (
          <RuleSectionComponent key={section.id} section={section} />
        ))}

        {/* Sources section (Level 3) */}
        <SourcesSection sources={response.content.sources} />
      </div>
    </div>
  );
};