// src/components/recipes/RecipesList.jsx
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useToast } from '@/contexts/ToastContext';
import { getUserRecipes, deleteRecipe } from '@/lib/api';

export default function RecipesList() {
  const [recipes, setRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all'); // 'all', 'private', 'shared'
  const { showToast } = useToast();
  const router = useRouter();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [recipeToDelete, setRecipeToDelete] = useState(null);

  useEffect(() => {
    // Fetch real user recipes instead of mock data
    const fetchRecipes = async () => {
      try {
        setIsLoading(true);
        const data = await getUserRecipes();
        setRecipes(data);
      } catch (error) {
        console.error('Error fetching recipes:', error);
        showToast('Failed to load recipes', 'error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecipes();
  }, [showToast]);

  // Filter and search recipes
  const filteredRecipes = recipes.filter(recipe => {
    // Apply search term filter
    const matchesSearch = 
      recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (recipe.description && recipe.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (recipe.cuisine && recipe.cuisine.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Apply visibility filter
    if (filter === 'all') return matchesSearch;
    if (filter === 'private') return matchesSearch && recipe.is_private;
    if (filter === 'shared') return matchesSearch && !recipe.is_private;
    
    return matchesSearch;
  });

  // Format date to readable string
  const formatDate = (dateString) => {
    if (!dateString) return "Unknown date";
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Trigger the delete modal
  const handleDeleteConfirmation = (recipeId) => {
    setRecipeToDelete(recipeId);
    setShowDeleteModal(true);
  };

  // Actually delete the recipe when confirmed
  const handleDeleteRecipe = async () => {
    try {
      console.log('Deleting recipe:', recipeToDelete);
      await deleteRecipe(recipeToDelete);
      
      // Update local state
      setRecipes(recipes.filter(recipe => recipe.id !== recipeToDelete));
      showToast('Recipe deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting recipe:', error);
      showToast('Failed to delete recipe', 'error');
    } finally {
      setShowDeleteModal(false);
      setRecipeToDelete(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">My Recipes</h1>
        <Link 
          href="/recipes/create"
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Add New Recipe
        </Link>
      </div>

     {/* Search and Filter */}
<div className="mt-6 sm:flex sm:items-center gap-4">
  <div className="sm:flex-1">
    <div className="flex items-center w-full max-w-lg border border-gray-300 rounded-md overflow-hidden bg-white">
      {/* Search icon */}
      <div className="flex items-center justify-center pl-3">
        <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
        </svg>
      </div>
      
      {/* Input field */}
      <input
        type="text"
        className="flex-1 py-2 px-3 border-0 focus:ring-0 focus:outline-none text-sm"
        placeholder="Search recipes..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      {/* Clear button */}
      <button
        type="button"
        onClick={() => setSearchTerm('')}
        className="px-4 py-2 bg-gray-50 text-gray-700 text-sm font-medium border-l border-gray-300 hover:bg-gray-100"
      >
        Clear
      </button>
    </div>
  </div>
  
  <div className="mt-4 sm:mt-0">
    <select
      id="filter"
      name="filter"
      className="block w-full pl-3 pr-10 py-2 text-sm border-gray-300 rounded-md focus:outline-none focus:ring-green-500 focus:border-green-500"
      value={filter}
      onChange={(e) => setFilter(e.target.value)}
    >
      <option value="all">All Recipes</option>
      <option value="private">Private Only</option>
      <option value="shared">Shared Only</option>
    </select>
  </div>
</div>

      {/* Recipe List */}
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-md">
        {filteredRecipes.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {filteredRecipes.map((recipe) => (
              <li key={recipe.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-green-600 truncate">
                        {recipe.title}
                      </p>
                      <div className="ml-2 flex-shrink-0 flex">
                        <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          recipe.is_private 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {recipe.is_private ? 'Private' : 'Shared'}
                        </p>
                      </div>
                    </div>
                    <div className="ml-2 flex-shrink-0 flex">
                      <Link
                        href={`/dashboard/recipes/detail/${recipe.id}`}
                        className="mr-2 font-medium text-green-600 hover:text-green-500"
                      >
                        View
                      </Link>
                      <Link
                        href={`/dashboard/recipes/edit/${recipe.id}`}
                        className="mr-2 font-medium text-blue-600 hover:text-blue-500"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDeleteConfirmation(recipe.id)}
                        className="font-medium text-red-600 hover:text-red-500"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  <div className="mt-2 sm:flex sm:justify-between">
                    <div className="sm:flex">
                      {recipe.cuisine && (
                        <p className="flex items-center text-sm text-gray-500">
                          <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          {recipe.cuisine}
                        </p>
                      )}
                      {(recipe.prep_time_minutes || recipe.cook_time_minutes) && (
                        <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                          <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                          </svg>
                          {(recipe.prep_time_minutes || 0) + (recipe.cook_time_minutes || 0)} minutes
                        </p>
                      )}
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                      <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                      <p>
                        Added on {formatDate(recipe.created_at)}
                      </p>
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-500 line-clamp-2">{recipe.description}</p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="px-4 py-8 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No recipes found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm 
                ? `No recipes match "${searchTerm}"`
                : 'Get started by creating a new recipe'}
            </p>
            <div className="mt-6">
              <Link
                href="/recipes/create"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                New Recipe
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm mx-auto">
            <h3 className="text-lg font-semibold mb-4">Delete Recipe</h3>
            <p className="text-gray-600 mb-6">Are you sure you want to delete this recipe? This action cannot be undone.</p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteRecipe}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}