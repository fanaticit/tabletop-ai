import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

interface LoginFormData {
  username: string;
  password: string;
}

interface LoginFormErrors {
  username?: string;
  password?: string;
  general?: string;
}

export const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const { login, setLoading } = useAuthStore();
  
  const [formData, setFormData] = useState<LoginFormData>({ 
    username: '', 
    password: '' 
  });
  const [errors, setErrors] = useState<LoginFormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: LoginFormErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setLoading(true);
    setErrors({});

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      console.log('Login successful:', data);
      
      // Store the token in the auth store
      login(data.access_token);
      
      // Redirect to chat page
      navigate('/chat');
      
    } catch (error) {
      setErrors({ general: (error as Error).message });
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof LoginFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({ 
      ...prev, 
      [field]: e.target.value 
    }));
    
    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <form onSubmit={handleSubmit} role="form">
        <div style={{ marginBottom: '20px' }}>
          <h2>Sign In</h2>
          
          {errors.general && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              {errors.general}
            </div>
          )}
          
          <div style={{ marginBottom: '15px' }}>
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={formData.username}
              onChange={handleInputChange('username')}
              disabled={isLoading}
              required
              style={{ 
                width: '100%', 
                padding: '8px', 
                marginTop: '5px',
                border: errors.username ? '1px solid red' : '1px solid #ccc'
              }}
            />
            {errors.username && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {errors.username}
              </div>
            )}
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange('password')}
              disabled={isLoading}
              required
              style={{ 
                width: '100%', 
                padding: '8px', 
                marginTop: '5px',
                border: errors.password ? '1px solid red' : '1px solid #ccc'
              }}
            />
            {errors.password && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {errors.password}
              </div>
            )}
          </div>
          
          <button 
            type="submit" 
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>
      </form>
    </div>
  );
};