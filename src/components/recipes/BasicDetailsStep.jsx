// src/components/recipes/BasicDetailsStep.jsx
import React from 'react';
import ImageUploader from './ImageUploader';

const BasicDetailsStep = ({ recipeData, updateRecipeData, username }) => {
  const handleImageUpload = (imagePath) => {
    updateRecipeData('image', imagePath);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {/* Recipe Name */}
        <div>
          <label htmlFor="recipe-name" className="block text-sm font-medium text-gray-700 mb-1">
            Recipe Name*
          </label>
          <input
            type="text"
            id="recipe-name"
            value={recipeData.name}
            onChange={(e) => updateRecipeData('name', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
            placeholder="What do you call this dish?"
            required
          />
        </div>
        
        {/* Recipe Image */}
        <ImageUploader 
          onImageUpload={handleImageUpload} 
          currentImage={recipeData.image}
        />
        
        {/* Emotional Connection/Memory */}
        <div>
          <label htmlFor="recipe-story" className="block text-sm font-medium text-gray-700 mb-1">
            Recipe Story
          </label>
          <textarea
            id="recipe-story"
            value={recipeData.story}
            onChange={(e) => updateRecipeData('story', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
            placeholder="Share a memory or story behind this recipe (e.g., 'I cook this every Diwali' or 'My mother's special Sunday dish')"
            rows={3}
          />
        </div>
        
        {/* Number of Servings */}
        <div>
          <label htmlFor="recipe-servings" className="block text-sm font-medium text-gray-700 mb-1">
            Servings*
          </label>
          <div className="flex items-center">
            <button 
              type="button"
              onClick={() => updateRecipeData('servings', Math.max(1, recipeData.servings - 1))}
              className="px-3 py-2 bg-gray-200 text-gray-700 rounded-l-md hover:bg-gray-300"
            >
              -
            </button>
            <input
              type="number"
              id="recipe-servings"
              value={recipeData.servings}
              onChange={(e) => updateRecipeData('servings', Math.max(1, parseInt(e.target.value) || 1))}
              className="w-16 text-center px-2 py-2 border-y border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              min="1"
            />
            <button 
              type="button"
              onClick={() => updateRecipeData('servings', recipeData.servings + 1)}
              className="px-3 py-2 bg-gray-200 text-gray-700 rounded-r-md hover:bg-gray-300"
            >
              +
            </button>
            <span className="ml-2 text-gray-600">people</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BasicDetailsStep;