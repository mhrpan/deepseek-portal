'use client';

import React from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';

export default function DashboardLayoutWrapper({ children }) {
  return <DashboardLayout>{children}</DashboardLayout>;
} 
