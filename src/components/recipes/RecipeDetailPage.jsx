// src/components/recipes/RecipeDetailPage.jsx
import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RecipeDetailPage({ recipe }) {
  const router = useRouter();
  
  const handleEdit = () => {
    router.push(`/dashboard/recipes/edit/${recipe.id}`);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {/* Recipe Header with Image */}
        <div className="relative">
          {recipe.image_url ? (
            <div className="w-full h-64 relative">
              <img 
                src={recipe.image_url} 
                alt={recipe.title} 
                className="w-full h-full object-cover" 
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/60"></div>
              <div className="absolute bottom-0 left-0 p-6">
                <h1 className="text-2xl font-bold text-white">{recipe.title}</h1>
                {recipe.cuisine && (
                  <span className="inline-block px-2 py-1 mt-2 text-xs font-semibold rounded-full bg-white text-green-800">
                    {recipe.cuisine}
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gradient-to-r from-green-500 to-teal-500 px-6 py-6">
              <h1 className="text-2xl font-bold text-white">{recipe.title}</h1>
              {recipe.cuisine && (
                <span className="inline-block px-2 py-1 mt-2 text-xs font-semibold rounded-full bg-white text-green-800">
                  {recipe.cuisine}
                </span>
              )}
            </div>
          )}
        </div>
        
        {/* Recipe Meta */}
        <div className="flex flex-wrap border-b border-gray-200 text-sm">
          <div className="px-6 py-3 flex items-center border-r border-gray-200">
            <svg className="h-5 w-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>
            <span>Serves: {recipe.servings}</span>
          </div>
          {recipe.prep_time_minutes && (
            <div className="px-6 py-3 flex items-center border-r border-gray-200">
              <svg className="h-5 w-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Prep: {recipe.prep_time_minutes} mins</span>
            </div>
          )}
          {recipe.cook_time_minutes && (
            <div className="px-6 py-3 flex items-center">
              <svg className="h-5 w-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
              </svg>
              <span>Cook: {recipe.cook_time_minutes} mins</span>
            </div>
          )}
        </div>
        
        {/* Description */}
        {recipe.description && (
          <div className="px-6 py-4 border-b border-gray-200">
            <p className="text-gray-700">{recipe.description}</p>
          </div>
        )}
        
        {/* Ingredients and Instructions in two columns on desktop, stacked on mobile */}
        <div className="px-6 py-6 md:flex">
          <div className="md:w-1/3 mb-6 md:mb-0 md:pr-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ingredients</h2>
            <ul className="space-y-2">
              {recipe.ingredients && recipe.ingredients.map((ingredient, idx) => (
                <li key={idx} className="flex items-baseline">
                  <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                  <span>
                    <span className="font-medium">{ingredient.quantity}</span> {ingredient.name}
                    {ingredient.brand && ingredient.brand !== 'Generic' && (
                      <span className="text-gray-500 text-sm"> ({ingredient.brand})</span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          
          <div className="md:w-2/3 md:pl-6 md:border-l md:border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Instructions</h2>
            <ol className="space-y-6">
              {recipe.steps && recipe.steps.map((step, idx) => (
                <li key={idx} className="flex">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 text-green-800 font-medium flex items-center justify-center mr-3 mt-1">
                    {idx + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-gray-700">{step.description}</p>
                    {step.media_url && step.media_type === 'image' && (
                      <div className="mt-3">
                        <img 
                          src={step.media_url} 
                          alt={`Step ${idx + 1}`} 
                          className="rounded-md border border-gray-200 max-h-48 object-cover" 
                        />
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
        
        {/* Action buttons */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
          <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
            <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Print
          </button>
          <button className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
            <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            Share
          </button>
          <button 
            onClick={handleEdit}
            className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
          >
            <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
            Edit
          </button>
        </div>
      </div>
    </div>
  );
}