// src/components/ClientWrapper.jsx or .tsx
'use client';

import React from 'react';
import { ToastProvider } from '@/contexts/ToastContext';

export function ClientWrapper({ children }) {
  return <ToastProvider>{children}</ToastProvider>;
}