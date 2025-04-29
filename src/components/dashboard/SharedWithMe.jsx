// src/components/dashboard/SharedWithMe.jsx
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useToast } from '@/contexts/ToastContext';

export default function SharedWithMe() {
  const [sharedRecipes, setSharedRecipes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    const fetchSharedRecipes = async () => {
      try {
        setIsLoading(true);
        // TODO: Implement the fetchSharedRecipes API call
        // For now, use mock data
        const mockData = [
          {
            id: '123',
            title: 'Mom\'s Special Curry',
            description: 'A family recipe passed down for generations',
            shared_by: 'Mom Smith',
            shared_at: '2025-04-01T18:25:43.511Z',
            family_name: 'Smith Family'
          },
          {
            id: '456',
            title: 'Dad\'s BBQ Sauce',
            description: 'Perfect for summer cookouts',
            shared_by: 'Dad Johnson',
            shared_at: '2025-03-15T14:30:43.511Z',
            family_name: 'Johnson Family'
          }
        ];

        setTimeout(() => {
          setSharedRecipes(mockData);
          setIsLoading(false);
        }, 800);
      } catch (error) {
        console.error('Error fetching shared recipes:', error);
        showToast('Failed to load shared recipes', 'error');
        setIsLoading(false);
      }
    };

    fetchSharedRecipes();
  }, [showToast]);

  // Format date to readable string
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
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
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Shared With Me</h1>
      
      {sharedRecipes.length === 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-8 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No shared recipes</h3>
            <p className="mt-1 text-sm text-gray-500">
              No one has shared any recipes with you yet.
            </p>
          </div>
        </div>
      ) : (
        <ul className="bg-white shadow overflow-hidden sm:rounded-md divide-y divide-gray-200">
          {sharedRecipes.map((recipe) => (
            <li key={recipe.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-green-600 truncate">
                    {recipe.title}
                  </div>
                  <div className="ml-2 flex-shrink-0 flex">
                    <Link
                      href={`/dashboard/recipes/shared/${recipe.id}`}
                      className="font-medium text-green-600 hover:text-green-500"
                    >
                      View Recipe
                    </Link>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                      </svg>
                      Shared by {recipe.shared_by}
                    </p>
                    <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                      <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                      </svg>
                      {recipe.family_name}
                    </p>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                    </svg>
                    <p>
                      Shared on {formatDate(recipe.shared_at)}
                    </p>
                  </div>
                </div>
                {recipe.description && (
                  <p className="mt-2 text-sm text-gray-500">{recipe.description}</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}