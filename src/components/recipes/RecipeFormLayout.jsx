'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const RecipeFormLayout = ({ 
  children, 
  step, 
  title, 
  totalSteps = 3,
  showSaveAsDraft = true,
  recipeData = null,
  onSaveDraft = null
}) => {
  const router = useRouter();
  const [showCancelModal, setShowCancelModal] = useState(false);
  
  const handleCancel = () => {
    setShowCancelModal(true);
  };
  
  const confirmCancel = () => {
    router.push('/dashboard');
  };
  
  const saveDraft = () => {
    if (onSaveDraft && recipeData) {
      // Use the callback if provided
      onSaveDraft(recipeData);
    } else if (recipeData) {
      // Get existing drafts
      const existingDrafts = JSON.parse(localStorage.getItem('recipeDrafts') || '[]');
      
      // Add current recipe with timestamp
      const newDraft = {
        id: Date.now(),
        recipe: recipeData,
        savedAt: new Date().toISOString()
      };
      
      // Save updated drafts
      localStorage.setItem('recipeDrafts', JSON.stringify([...existingDrafts, newDraft]));
      
      alert('Recipe saved as draft');
      router.push('/dashboard');
    } else {
      // No recipe data available
      alert('No recipe data to save');
      router.push('/dashboard');
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-6">
      {/* Top Navigation Bar */}
      <div className="mb-6 flex items-center space-x-6 border-b pb-4 overflow-x-auto">
        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 whitespace-nowrap">
          Dashboard
        </Link>
        <Link href="/recipes/create" className="text-gray-600 hover:text-gray-900 whitespace-nowrap">
          Add Recipe
        </Link>
        <Link href="/dashboard/recipes" className="text-gray-600 hover:text-gray-900 whitespace-nowrap">
          My Recipes
        </Link>
        <Link href="/dashboard/shared" className="text-gray-600 hover:text-gray-900 whitespace-nowrap">
          Shared With Me
        </Link>
        <Link href="/dashboard/family" className="text-gray-600 hover:text-gray-900 whitespace-nowrap">
          Family Members
        </Link>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-xl font-semibold">{title}</h1>
          <div className="text-sm text-gray-500">Step {step} of {totalSteps}</div>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
          <div 
            className="bg-green-500 h-2 rounded-full transition-all duration-300 ease-in-out" 
            style={{ width: `${(step / totalSteps) * 100}%` }}
          ></div>
        </div>
        
        {/* Main content */}
        {children}
      </div>
      
      {/* Cancel confirmation modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-auto">
            <h3 className="text-lg font-semibold mb-4">Discard changes?</h3>
            <p className="text-gray-600 mb-6">Your recipe changes will be lost. Would you like to save as draft instead?</p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowCancelModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md"
              >
                Continue Editing
              </button>
              {showSaveAsDraft && recipeData && (
                <button
                  onClick={saveDraft}
                  className="px-4 py-2 border border-gray-300 rounded-md bg-blue-50 text-blue-600"
                >
                  Save Draft
                </button>
              )}
              <button
                onClick={confirmCancel}
                className="px-4 py-2 bg-red-600 text-white rounded-md"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecipeFormLayout;