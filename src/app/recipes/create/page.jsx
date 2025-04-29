'use client';

import React from 'react';
import RecipeForm from '@/components/recipes/RecipeForm';

export default function CreateRecipePage() {
  // This would normally come from user authentication
  const username = "Mihir";
  
  return (
    <RecipeForm username={username} />
  );
}