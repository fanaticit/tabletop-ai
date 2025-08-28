// src/components/dashboard/QuickActions.tsx - Quick action buttons and shortcuts
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const QuickActions: React.FC = () => {
  const navigate = useNavigate();
  const [showActions, setShowActions] = useState(false);

  const actions = [
    {
      id: 'random-game',
      label: 'Random Game',
      icon: '🎲',
      description: 'Start a chat with a random game',
      onClick: () => {
        // TODO: Implement random game selection
        console.log('Random game selected');
      }
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      description: 'User preferences and settings',
      onClick: () => {
        navigate('/settings');
      }
    },
    {
      id: 'help',
      label: 'Help',
      icon: '❓',
      description: 'How to use the AI rule assistant',
      onClick: () => {
        // TODO: Implement help modal or page
        console.log('Help requested');
      }
    }
  ];

  return (
    <div className="relative">
      <button
        onClick={() => setShowActions(!showActions)}
        className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <span className="mr-2">⚡</span>
        Quick Actions
        <span className={`ml-2 transform transition-transform duration-200 ${showActions ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {showActions && (
        <>
          {/* Overlay */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowActions(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-20">
            <div className="py-1" role="menu" aria-orientation="vertical">
              {actions.map((action) => (
                <button
                  key={action.id}
                  onClick={() => {
                    action.onClick();
                    setShowActions(false);
                  }}
                  className="group flex items-start px-4 py-3 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 w-full text-left"
                  role="menuitem"
                >
                  <span className="mr-3 text-lg">{action.icon}</span>
                  <div>
                    <div className="font-medium">{action.label}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {action.description}
                    </div>
                  </div>
                </button>
              ))}
              
              {/* Separator */}
              <div className="border-t border-gray-100 my-1" />
              
              {/* Additional Actions */}
              <div className="px-4 py-2">
                <div className="text-xs text-gray-500 font-medium mb-2">
                  KEYBOARD SHORTCUTS
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>New Chat</span>
                    <span className="font-mono bg-gray-100 px-1 rounded">Ctrl+N</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-600">
                    <span>Search Games</span>
                    <span className="font-mono bg-gray-100 px-1 rounded">Ctrl+K</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default QuickActions;