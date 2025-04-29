// src/components/ui/Toast.jsx
'use client';

import React, { useState, useEffect } from 'react';

export default function Toast({ message, type = 'success', duration = 3000, onClose }) {
  const [visible, setVisible] = useState(true);
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    // Start the countdown to begin fading
    const displayTimer = setTimeout(() => {
      setIsFading(true);
      
      // After fade animation starts, schedule the removal
      const fadeTimer = setTimeout(() => {
        setVisible(false);
        if (onClose) onClose();
      }, 300); // Animation duration
      
      return () => clearTimeout(fadeTimer);
    }, duration);
    
    return () => clearTimeout(displayTimer);
  }, [duration, onClose]);

  if (!visible) return null;

  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
  const opacityClass = isFading ? 'opacity-0' : 'opacity-100';

  return (
    <div 
      className={`fixed top-4 right-4 z-50 p-4 rounded-md shadow-md text-white ${bgColor} transition-opacity duration-300 ${opacityClass}`}
    >
      {message}
    </div>
  );
}