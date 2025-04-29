// src/components/recipes/RecipeForm.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import BasicDetailsStep from './BasicDetailsStep';
import IngredientsStep from './IngredientsStep';
import CookingStepsStep from './CookingStepsStep';
import { createRecipe, updateRecipe } from '@/lib/api';
import { useToast } from '@/contexts/ToastContext';
import RecipeFormLayout from './RecipeFormLayout';

const RecipeForm = ({ username, editMode = false, initialRecipe = null, recipeId = null }) => {
  const router = useRouter();
  const { showToast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Use a ref to track if we've already initialized the form data
  const dataInitialized = useRef(false);
  
  // Initialize with empty data first
  const [recipeData, setRecipeData] = useState({
    name: '',
    story: '',
    servings: 2,
    image: null,
    ingredients: [],
    steps: []
  });
  
  // Use useEffect to initialize the form data only once
  useEffect(() => {
  // Only initialize if we have initialRecipe and haven't initialized yet
  if (editMode && initialRecipe && !dataInitialized.current) {
    console.log("Initializing recipe form with data:", initialRecipe);
    
    setRecipeData({
      name: initialRecipe.title || '',
      story: initialRecipe.description || '',
      servings: initialRecipe.servings || 2,
      image: initialRecipe.image_url || null,
      ingredients: initialRecipe.ingredients?.map(ing => ({
        id: ing.id || generateUniqueId(),  // Use guaranteed unique function
        name: ing.name,
        quantity: ing.quantity,
        brand: ing.brand !== 'Generic' ? ing.brand : '',
        ingredient_id: ing.branded_ingredient_id || ing.id
      })) || [],
      steps: initialRecipe.steps?.map(step => ({
        id: step.id || generateUniqueId(),  // Use guaranteed unique function
        instruction: step.description || '',
        stepImage: step.media_url || null,
        hasImage: !!step.media_url
      })) || []
    });
    
    // Mark as initialized to prevent re-initializing
    dataInitialized.current = true;
  }
}, [editMode, initialRecipe]);

  // Create a stable updateRecipeData function that preserves step
  const updateRecipeData = (field, value) => {
    console.log(`Updating ${field} with new value`, { field, value });
    
    setRecipeData(prev => {
      // Create a new object to ensure React detects the change
      return { ...prev, [field]: value };
    });
  };

  const handleNext = () => {
    setCurrentStep(prev => Math.min(prev + 1, 3));
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    
    // Basic validation
    if (!recipeData.name.trim()) {
      showToast('Please enter a recipe name', 'error');
      setCurrentStep(1);
      return;
    }
    
    if (recipeData.ingredients.length === 0) {
      showToast('Please add at least one ingredient', 'error');
      setCurrentStep(2);
      return;
    }
    
    if (recipeData.steps.length === 0) {
      showToast('Please add at least one cooking step', 'error');
      return;
    }
    
    console.log('Submitting recipe:', recipeData);
    
    try {
      setIsSubmitting(true);
      
      let result;
      
      if (editMode) {
        // Update existing recipe
        result = await updateRecipe(recipeId, {
          name: recipeData.name,
          story: recipeData.story,
          servings: recipeData.servings,
          image: recipeData.image,
          ingredients: recipeData.ingredients,
          steps: recipeData.steps
        });
        showToast('Recipe updated successfully!', 'success');
      } else {
        // Create new recipe
        result = await createRecipe({
          name: recipeData.name,
          story: recipeData.story,
          servings: recipeData.servings,
          image: recipeData.image,
          ingredients: recipeData.ingredients,
          steps: recipeData.steps
        });
        showToast('Recipe submitted successfully!', 'success');
      }
      
      // Redirect to recipes page
      router.push('/dashboard/recipes');
      
    } catch (error) {
      console.error('Error submitting recipe:', error);
      showToast(`Failed to ${editMode ? 'update' : 'submit'} recipe: ${error.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSaveDraft = () => {
    // Implement draft saving functionality
    const draftData = {
      ...recipeData,
      lastUpdated: new Date().toISOString(),
      isDraft: true
    };
    
    // Save to localStorage
    try {
      const drafts = JSON.parse(localStorage.getItem('recipeDrafts') || '[]');
      const existingDraftIndex = drafts.findIndex(d => 
        editMode && d.id === recipeId || d.tempId === draftData.tempId
      );
      
      if (existingDraftIndex >= 0) {
        // Update existing draft
        drafts[existingDraftIndex] = {
          ...drafts[existingDraftIndex],
          ...draftData
        };
      } else {
        // Add new draft
        drafts.push({
          tempId: Date.now(),
          ...draftData,
          id: editMode ? recipeId : null
        });
      }
      
      localStorage.setItem('recipeDrafts', JSON.stringify(drafts));
      showToast('Recipe saved as draft', 'success');
      router.push('/dashboard/recipes');
    } catch (error) {
      console.error('Error saving draft:', error);
      showToast('Failed to save draft', 'error');
    }
  };

  // Get the title based on current step
  const getStepTitle = () => {
    switch(currentStep) {
      case 1: return "Add Recipe Details";
      case 2: return "Add Ingredients";
      case 3: return "Instructions";
      default: return "Add Recipe";
    }
  };

  return (
    <RecipeFormLayout 
      step={currentStep} 
      title={getStepTitle()} 
      totalSteps={3}
      recipeData={recipeData}
      onSaveDraft={handleSaveDraft}
    >
      {currentStep === 1 && (
        <>
          <BasicDetailsStep 
            recipeData={recipeData} 
            updateRecipeData={updateRecipeData}
            username={username}
          />
          <div className="flex justify-between mt-8">
            <button
              type="button"
              onClick={() => router.push('/dashboard/recipes')}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleNext}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Next
            </button>
          </div>
        </>
      )}
      
      {currentStep === 2 && (
        <>
          <IngredientsStep 
            recipeData={recipeData} 
            updateRecipeData={updateRecipeData}
          />
          <div className="flex justify-between mt-8">
            <button
              type="button"
              onClick={handlePrevious}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              Previous
            </button>
            <button
              type="button"
              onClick={handleNext}
              disabled={recipeData.ingredients.length === 0}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </>
      )}
      
      {currentStep === 3 && (
        <>
          <CookingStepsStep 
            recipeData={recipeData} 
            updateRecipeData={updateRecipeData}
          />
          <div className="flex justify-between mt-8">
            <button
              type="button"
              onClick={handlePrevious}
              className="px-4 py-2 border border-gray-300 rounded-md"
            >
              Previous
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting || recipeData.steps.length === 0}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Submitting...' : editMode ? 'Update Recipe' : 'Submit Recipe'}
            </button>
          </div>
        </>
      )}
    </RecipeFormLayout>
  );
};

export default RecipeForm;