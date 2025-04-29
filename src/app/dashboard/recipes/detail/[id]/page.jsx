'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import RecipeDetailPage from '@/components/recipes/RecipeDetailPage';
import { useToast } from '@/contexts/ToastContext';

// You'll need to create this function in your api.js file
import { getRecipeById } from '@/lib/api';

export default function RecipeDetailRoute() {
  const { id } = useParams();
  const [recipe, setRecipe] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { showToast } = useToast();

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const data = await getRecipeById(id);
        setRecipe(data);
      } catch (err) {
        console.error('Error fetching recipe:', err);
        setError('Failed to load recipe. Please try again later.');
        showToast('Failed to load recipe', 'error');
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchRecipe();
    }
  }, [id, showToast]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h2 className="text-xl font-semibold text-red-700 mb-2">Error</h2>
        <p className="text-red-600">{error}</p>
        <button 
          onClick={() => window.history.back()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h2 className="text-xl font-semibold text-yellow-700 mb-2">Recipe Not Found</h2>
        <p className="text-yellow-600">The recipe you're looking for doesn't exist or has been removed.</p>
        <button 
          onClick={() => window.history.back()}
          className="mt-4 px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  return <RecipeDetailPage recipe={recipe} />;
}