// src/app/dashboard/recipes/edit/[id]/page.jsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import RecipeForm from '@/components/recipes/RecipeForm';
import { useToast } from '@/contexts/ToastContext';
import { getRecipeById } from '@/lib/api';

export default function EditRecipePage() {
  const { id } = useParams();
  const [recipe, setRecipe] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();
  const { showToast } = useToast();
  const fetchedRef = useRef(false);

  useEffect(() => {
    // Only fetch once
    if (fetchedRef.current) return;
    
    const fetchRecipe = async () => {
      try {
        setIsLoading(true);
        console.log("Fetching recipe data for ID:", id);
        const data = await getRecipeById(id);
        setRecipe(data);
        fetchedRef.current = true;
      } catch (error) {
        console.error('Error fetching recipe:', error);
        setError(error.message || 'Failed to load recipe');
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
      <div className="text-center py-10">
        <p className="text-red-500">{error}</p>
        <button
          onClick={() => router.push('/dashboard/recipes')}
          className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md"
        >
          Back to Recipes
        </button>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Recipe not found</p>
        <button
          onClick={() => router.push('/dashboard/recipes')}
          className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md"
        >
          Back to Recipes
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Edit Recipe</h1>
      <RecipeForm 
        editMode={true} 
        initialRecipe={recipe} 
        recipeId={id} 
      />
    </div>
  );
}