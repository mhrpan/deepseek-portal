// src/contexts/ToastContext.jsx
'use client';
import React, { createContext, useContext, useState } from 'react';
import Toast from '@/components/ui/Toast';

// Helper function to generate guaranteed unique IDs
const generateUniqueId = () => {
  return `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  
  const showToast = (message, type = 'success', duration = 3000) => {
    const id = generateUniqueId();
    setToasts(prevToasts => [...prevToasts, { id, message, type, duration }]);
    return id;
  };
  
  const hideToast = (id) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  };
  
  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => hideToast(toast.id)}
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}