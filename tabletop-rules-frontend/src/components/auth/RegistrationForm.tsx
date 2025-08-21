import React, { useState } from 'react';

interface RegistrationFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface RegistrationFormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

export const RegistrationForm: React.FC = () => {
  const [formData, setFormData] = useState<RegistrationFormData>({ 
    username: '', 
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState<RegistrationFormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const validateForm = (): boolean => {
    const newErrors: RegistrationFormErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!formData.confirmPassword.trim()) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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
    setErrors({});
    setSuccessMessage('');

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      const data = await response.json();
      setSuccessMessage('Registration successful');
      
      // Reset form
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      });
      
    } catch (error) {
      setErrors({ general: (error as Error).message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof RegistrationFormData) => (
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
          <h2>Create Account</h2>
          
          {errors.general && (
            <div style={{ color: 'red', marginBottom: '10px' }}>
              {errors.general}
            </div>
          )}
          
          {successMessage && (
            <div style={{ color: 'green', marginBottom: '10px' }}>
              {successMessage}
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
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange('email')}
              disabled={isLoading}
              required
              style={{ 
                width: '100%', 
                padding: '8px', 
                marginTop: '5px',
                border: errors.email ? '1px solid red' : '1px solid #ccc'
              }}
            />
            {errors.email && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {errors.email}
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
          
          <div style={{ marginBottom: '15px' }}>
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleInputChange('confirmPassword')}
              disabled={isLoading}
              required
              style={{ 
                width: '100%', 
                padding: '8px', 
                marginTop: '5px',
                border: errors.confirmPassword ? '1px solid red' : '1px solid #ccc'
              }}
            />
            {errors.confirmPassword && (
              <div style={{ color: 'red', fontSize: '14px', marginTop: '5px' }}>
                {errors.confirmPassword}
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
            {isLoading ? 'Creating account...' : 'Create Account'}
          </button>
        </div>
      </form>
    </div>
  );
};