// src/components/recipes/IngredientsStep.jsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { getIngredients, addIngredient, getBrands, addBrand } from '@/lib/api';
import { useToast } from '@/contexts/ToastContext';

// Utility function to generate reliable unique IDs
const generateUniqueId = () => {
  return `id-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const IngredientsStep = ({ recipeData, updateRecipeData }) => {
  const { showToast } = useToast();
  
  // State for the current ingredient being added
  const [currentIngredient, setCurrentIngredient] = useState({
    name: '',
    quantity: '',
    brand: ''
  });
  
  // State for the ingredient being edited
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({
    name: '',
    quantity: '',
    brand: ''
  });
  
  // States for auto-suggestions
  const [ingredientSuggestions, setIngredientSuggestions] = useState([]);
  const [brandSuggestions, setBrandSuggestions] = useState([]);
  const [showIngredientSuggestions, setShowIngredientSuggestions] = useState(false);
  const [showBrandSuggestions, setShowBrandSuggestions] = useState(false);
  const [showEditIngredientSuggestions, setShowEditIngredientSuggestions] = useState(false);
  const [showEditBrandSuggestions, setShowEditBrandSuggestions] = useState(false);
  const [editIngredientSuggestions, setEditIngredientSuggestions] = useState([]);
  const [editBrandSuggestions, setEditBrandSuggestions] = useState([]);
  
  // Selected ingredient IDs
  const [selectedIngredientId, setSelectedIngredientId] = useState(null);
  const [editIngredientId, setEditIngredientId] = useState(null);
  
  // Loading states
  const [isLoadingIngredients, setIsLoadingIngredients] = useState(false);
  const [isLoadingBrands, setIsLoadingBrands] = useState(false);
  const [isLoadingEditIngredients, setIsLoadingEditIngredients] = useState(false);
  const [isLoadingEditBrands, setIsLoadingEditBrands] = useState(false);
  const [isProcessingAdd, setIsProcessingAdd] = useState(false);
  const [isProcessingSave, setIsProcessingSave] = useState(false);
  
  // Refs for handling clicks outside suggestion boxes
  const ingredientSuggestionsRef = useRef(null);
  const brandSuggestionsRef = useRef(null);
  const editIngredientSuggestionsRef = useRef(null);
  const editBrandSuggestionsRef = useRef(null);

  // Fetch ingredient suggestions for adding
  useEffect(() => {
    if (!currentIngredient.name || currentIngredient.name.length < 2) {
      setIngredientSuggestions([]);
      return;
    }
    
    const fetchIngredients = async () => {
      try {
        setIsLoadingIngredients(true);
        const data = await getIngredients(currentIngredient.name);
        setIngredientSuggestions(data || []);
      } catch (error) {
        console.error('Error fetching ingredients:', error);
        setIngredientSuggestions([]);
      } finally {
        setIsLoadingIngredients(false);
      }
    };
    
    const timeoutId = setTimeout(fetchIngredients, 300);
    return () => clearTimeout(timeoutId);
  }, [currentIngredient.name]);

  // Fetch brand suggestions for adding
  useEffect(() => {
    if (!currentIngredient.brand || !selectedIngredientId || currentIngredient.brand.length < 2) {
      setBrandSuggestions([]);
      return;
    }
    
    const fetchBrands = async () => {
      try {
        setIsLoadingBrands(true);
        if (selectedIngredientId && 
            /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(selectedIngredientId)) {
          const data = await getBrands(selectedIngredientId, currentIngredient.brand);
          setBrandSuggestions(data || []);
        } else {
          setBrandSuggestions([]);
        }
      } catch (error) {
        console.error('Error fetching brands:', error);
        setBrandSuggestions([]);
      } finally {
        setIsLoadingBrands(false);
      }
    };
    
    const timeoutId = setTimeout(fetchBrands, 300);
    return () => clearTimeout(timeoutId);
  }, [currentIngredient.brand, selectedIngredientId]);

  // Fetch ingredient suggestions for editing
  useEffect(() => {
    if (!editForm.name || editForm.name.length < 2) {
      setEditIngredientSuggestions([]);
      return;
    }
    
    const fetchIngredients = async () => {
      try {
        setIsLoadingEditIngredients(true);
        const data = await getIngredients(editForm.name);
        setEditIngredientSuggestions(data || []);
      } catch (error) {
        console.error('Error fetching ingredients for edit:', error);
        setEditIngredientSuggestions([]);
      } finally {
        setIsLoadingEditIngredients(false);
      }
    };
    
    const timeoutId = setTimeout(fetchIngredients, 300);
    return () => clearTimeout(timeoutId);
  }, [editForm.name]);

  // Fetch brand suggestions for editing
  useEffect(() => {
    if (!editForm.brand || !editIngredientId || editForm.brand.length < 2) {
      setEditBrandSuggestions([]);
      return;
    }
    
    const fetchBrands = async () => {
      try {
        setIsLoadingEditBrands(true);
        if (editIngredientId && 
            /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(editIngredientId)) {
          const data = await getBrands(editIngredientId, editForm.brand);
          setEditBrandSuggestions(data || []);
        } else {
          setEditBrandSuggestions([]);
        }
      } catch (error) {
        console.error('Error fetching brands for edit:', error);
        setEditBrandSuggestions([]);
      } finally {
        setIsLoadingEditBrands(false);
      }
    };
    
    const timeoutId = setTimeout(fetchBrands, 300);
    return () => clearTimeout(timeoutId);
  }, [editForm.brand, editIngredientId]);

  // Handle click outside suggestions
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleClickOutside = (event) => {
      if (ingredientSuggestionsRef.current && !ingredientSuggestionsRef.current.contains(event.target)) {
        setShowIngredientSuggestions(false);
      }
      if (brandSuggestionsRef.current && !brandSuggestionsRef.current.contains(event.target)) {
        setShowBrandSuggestions(false);
      }
      if (editIngredientSuggestionsRef.current && !editIngredientSuggestionsRef.current.contains(event.target)) {
        setShowEditIngredientSuggestions(false);
      }
      if (editBrandSuggestionsRef.current && !editBrandSuggestionsRef.current.contains(event.target)) {
        setShowEditBrandSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Function to start editing an ingredient
  const startEditing = (ingredient) => {
    setEditingId(ingredient.id);
    setEditForm({
      name: ingredient.name,
      quantity: ingredient.quantity,
      brand: ingredient.brand || '',
    });
    setEditIngredientId(ingredient.ingredient_id);
    
    console.log("Started editing ingredient:", ingredient);
  };
  
  // Function to cancel editing
  const cancelEditing = () => {
    setEditingId(null);
    setEditForm({
      name: '',
      quantity: '',
      brand: ''
    });
    setEditIngredientId(null);
    setShowEditIngredientSuggestions(false);
    setShowEditBrandSuggestions(false);
  };
  
  // Function to save edits
  const saveEdit = async () => {
    if (!editForm.name || !editForm.quantity) {
      showToast('Name and quantity are required', 'error');
      return;
    }
    
    try {
      setIsProcessingSave(true);
      
      // If no ingredient ID was selected but we have a name, create the ingredient
      if (!editIngredientId && editForm.name.trim()) {
        await handleAddNewEditIngredient();
      } else {
        // Otherwise proceed with the update
        updateIngredients();
      }
    } catch (error) {
      console.error("Error during save edit:", error);
      showToast(`Error updating ingredient: ${error.message || 'Unknown error'}`, 'error');
    } finally {
      setIsProcessingSave(false);
    }
  };
  
  // Update ingredients in the recipe data
  const updateIngredients = () => {
    const updatedIngredients = recipeData.ingredients.map(ing => 
      ing.id === editingId ? {
        ...ing,
        name: editForm.name,
        quantity: editForm.quantity,
        brand: editForm.brand,
        ingredient_id: editIngredientId || ing.ingredient_id
      } : ing
    );
    
    updateRecipeData('ingredients', updatedIngredients);
    showToast(`Updated ${editForm.name}`, 'success');
    cancelEditing();
  };

  // Add ingredient to the recipe
  const addIngredientToRecipe = async () => {
    if (!currentIngredient.name || !currentIngredient.quantity) {
      showToast('Name and quantity are required', 'error');
      return;
    }
    
    try {
      setIsProcessingAdd(true);
      
      // If no ingredient ID was selected but we have a name, create the ingredient
      if (!selectedIngredientId && currentIngredient.name.trim()) {
        const success = await addNewIngredient();
        if (success) {
          // Now that we've added the ingredient, add it to the recipe
          addIngredientToRecipeInternal();
        }
      } else {
        // Otherwise proceed with adding directly
        addIngredientToRecipeInternal();
      }
    } catch (error) {
      console.error("Error adding ingredient to recipe:", error);
      showToast(`Error adding ingredient: ${error.message || 'Unknown error'}`, 'error');
    } finally {
      setIsProcessingAdd(false);
    }
  };
  
  // Internal function to add ingredient to recipe data
  const addIngredientToRecipeInternal = () => {
    console.log("Adding ingredient with data:", currentIngredient, "Selected ID:", selectedIngredientId);
    
    const newIngredients = [...recipeData.ingredients, { 
      ...currentIngredient, 
      id: generateUniqueId(),
      ingredient_id: selectedIngredientId
    }];
    
    updateRecipeData('ingredients', newIngredients);
    showToast(`Added ${currentIngredient.name} to recipe`, 'success');
    
    // Clear the form
    setCurrentIngredient({ name: '', quantity: '', brand: '' });
    setSelectedIngredientId(null);
    setShowIngredientSuggestions(false);
    setShowBrandSuggestions(false);
  };

  // Remove ingredient from the recipe
  const removeIngredient = (id) => {
    const ingredientToRemove = recipeData.ingredients.find(ing => ing.id === id);
    const newIngredients = recipeData.ingredients.filter(ing => ing.id !== id);
    updateRecipeData('ingredients', newIngredients);
    
    if (ingredientToRemove) {
      showToast(`Removed ${ingredientToRemove.name} from recipe`, 'success');
    }
  };

  // Select ingredient from suggestions for adding
  const selectIngredient = (ingredient) => {
    console.log("Selected ingredient:", ingredient);
    
    if (typeof ingredient === 'object' && ingredient.id) {
      setCurrentIngredient({ ...currentIngredient, name: ingredient.name });
      setSelectedIngredientId(ingredient.id);
    } else {
      setCurrentIngredient({ ...currentIngredient, name: ingredient });
      setSelectedIngredientId(null);
    }
    setShowIngredientSuggestions(false);
  };

  // Select brand from suggestions for adding
  const selectBrand = (brand) => {
    console.log("Selected brand:", brand);
    
    setCurrentIngredient({ 
      ...currentIngredient, 
      brand: typeof brand === 'object' ? brand.name : brand 
    });
    setShowBrandSuggestions(false);
  };
  
  // Select ingredient from suggestions for editing
  const selectEditIngredient = (ingredient) => {
    console.log("Selected edit ingredient:", ingredient);
    
    if (typeof ingredient === 'object' && ingredient.id) {
      setEditForm({ ...editForm, name: ingredient.name });
      setEditIngredientId(ingredient.id);
    } else {
      setEditForm({ ...editForm, name: ingredient });
      setEditIngredientId(null);
    }
    setShowEditIngredientSuggestions(false);
  };

  // Select brand from suggestions for editing
  const selectEditBrand = (brand) => {
    console.log("Selected edit brand:", brand);
    
    setEditForm({ 
      ...editForm, 
      brand: typeof brand === 'object' ? brand.name : brand 
    });
    setShowEditBrandSuggestions(false);
  };

  // Add new ingredient to database when adding
  const addNewIngredient = async () => {
    try {
      console.log("Adding new ingredient:", currentIngredient.name);
      
      // Make API call
      const result = await addIngredient({ 
        name: currentIngredient.name
      });
      
      console.log("API response for adding ingredient:", result);
      
      if (result && result.status === 'success' && result.id) {
        // Create a new ingredient with the returned ID
        const newIngredient = { 
          id: result.id, 
          name: currentIngredient.name 
        };
        
        // Add to suggestions list
        setIngredientSuggestions(prev => 
          prev.some(i => i.id === newIngredient.id) 
            ? prev 
            : [newIngredient, ...prev]
        );
        
        // Set the selected ID and name
        setSelectedIngredientId(newIngredient.id);
        
        // DON'T automatically add to recipe yet - just show success
        // so user can complete the quantity field
        showToast(`Added "${newIngredient.name}" to ingredients database`, 'success');
        return true;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error adding ingredient:', error);
      showToast(`Failed to add ingredient: ${error.message || 'Unknown error'}`, 'error');
      throw error;
    }
  };
  
  // Add new ingredient to database when editing
  const handleAddNewEditIngredient = async () => {
    try {
      console.log("Adding new ingredient during edit:", editForm.name);
      
      // Make API call
      const result = await addIngredient({ 
        name: editForm.name
      });
      
      console.log("API response for adding ingredient during edit:", result);
      
      if (result && result.status === 'success' && result.id) {
        // Create a new ingredient with the returned ID
        const newIngredient = { 
          id: result.id, 
          name: editForm.name 
        };
        
        // Add to suggestions list
        setEditIngredientSuggestions(prev => 
          prev.some(i => i.id === newIngredient.id) 
            ? prev 
            : [newIngredient, ...prev]
        );
        
        // Set the selected ID and name
        setEditIngredientId(newIngredient.id);
        
        // Now update the ingredient list
        updateIngredients();
        
        showToast(`Added "${newIngredient.name}" to ingredients database`, 'success');
        return true;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error adding ingredient during edit:', error);
      showToast(`Failed to add ingredient: ${error.message || 'Unknown error'}`, 'error');
      return false;
    }
  };

  // Add new brand to database
  const addNewBrand = async () => {
    try {
      if (!selectedIngredientId) {
        showToast('Please select a valid ingredient first', 'error');
        return;
      }
      
      // Validate UUID format
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(selectedIngredientId)) {
        showToast('Invalid ingredient ID format', 'error');
        console.error("Invalid ingredient ID format:", selectedIngredientId);
        return;
      }
      
      console.log("Adding new brand:", currentIngredient.brand, "for ingredient ID:", selectedIngredientId);
      
      try {
        // First verify that the base ingredient exists
        const ingredientsResponse = await getIngredients("");
        const ingredientExists = ingredientsResponse.some(ing => ing.id === selectedIngredientId);
        
        if (!ingredientExists) {
          showToast("Ingredient not found in database. Please try again.", "error");
          return;
        }
        
        const result = await addBrand({ 
          name: currentIngredient.brand,
          ingredient_id: selectedIngredientId,
          is_verified: false
        });
        
        console.log("API response for adding brand:", result);
        
        if (result && result.status === 'success') {
          const newBrand = { 
            id: result.brand_id || result.id, 
            name: currentIngredient.brand 
          };
          
          setBrandSuggestions(prev => 
            prev.some(b => b.id === newBrand.id) 
              ? prev 
              : [newBrand, ...prev]
          );
          
          setCurrentIngredient({
            ...currentIngredient,
            brand: newBrand.name
          });
          
          setShowBrandSuggestions(false);
          
          showToast(`Added "${newBrand.name}" as a brand for ${currentIngredient.name}`, 'success');
        } else {
          throw new Error(result?.message || 'Invalid response from server');
        }
      } catch (error) {
        console.error('Error in brand API call:', error);
        showToast(`Server error: ${error.message || 'Database constraint error - ingredient may not exist'}`, 'error');
      }
    } catch (error) {
      console.error('Error adding brand:', error);
      showToast(`Failed to add brand: ${error.message || 'Unknown error'}`, 'error');
    }
  };
  
  // Add new brand to database when editing
  const addNewEditBrand = async () => {
    try {
      if (!editIngredientId) {
        showToast('Please select a valid ingredient first', 'error');
        return;
      }
      
      // Validate UUID format
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(editIngredientId)) {
        showToast('Invalid ingredient ID format', 'error');
        console.error("Invalid ingredient ID format:", editIngredientId);
        return;
      }
      
      console.log("Adding new brand during edit:", editForm.brand, "for ingredient ID:", editIngredientId);
      
      try {
        // First verify that the base ingredient exists
        const ingredientsResponse = await getIngredients("");
        const ingredientExists = ingredientsResponse.some(ing => ing.id === editIngredientId);
        
        if (!ingredientExists) {
          showToast("Ingredient not found in database. Please try again.", "error");
          return;
        }
        
        // Make API call with proper error handling
        const result = await addBrand({ 
          name: editForm.brand,
          ingredient_id: editIngredientId,
          is_verified: false
        });
        
        console.log("API response for adding brand during edit:", result);
        
        if (result && result.status === 'success') {
          // Process successful result
          const newBrand = { 
            id: result.brand_id || result.id, 
            name: editForm.brand 
          };
          
          setEditBrandSuggestions(prev => 
            prev.some(b => b.id === newBrand.id) 
              ? prev 
              : [newBrand, ...prev]
          );
          
          setEditForm({
            ...editForm,
            brand: newBrand.name
          });
          
          setShowEditBrandSuggestions(false);
          
          showToast(`Added "${newBrand.name}" as a brand for ${editForm.name}`, 'success');
        } else {
          throw new Error(result?.message || 'Invalid response from server');
        }
      } catch (error) {
        console.error('Error in brand API call:', error);
        showToast(`Server error: ${error.message || 'Database constraint error - ingredient may not exist'}`, 'error');
      }
    } catch (error) {
      console.error('Error adding brand during edit:', error);
      showToast(`Failed to add brand: ${error.message || 'Unknown error'}`, 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Ingredient input form */}
      <div className="p-4 border border-gray-200 rounded-md bg-gray-50">
        <h3 className="font-medium text-gray-700 mb-3">New Ingredient</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
          {/* Ingredient name with auto-suggestion */}
          <div className="md:col-span-5 relative">
            <label htmlFor="ingredient-name" className="block text-sm font-medium text-gray-700 mb-1">
              Ingredient*
            </label>
            <input
              type="text"
              id="ingredient-name"
              value={currentIngredient.name}
              onChange={(e) => {
                setCurrentIngredient({ ...currentIngredient, name: e.target.value });
                setSelectedIngredientId(null);
                setShowIngredientSuggestions(true);
              }}
              onFocus={() => setShowIngredientSuggestions(true)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="e.g., Salt, Sugar"
            />
            
            {/* Ingredient Suggestions */}
            {showIngredientSuggestions && currentIngredient.name && (
              <div 
                ref={ingredientSuggestionsRef}
                className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-auto"
              >
                {isLoadingIngredients ? (
                  <div className="p-4 text-center">
                    <span className="inline-block animate-spin mr-2">⟳</span> Loading...
                  </div>
                ) : ingredientSuggestions.length > 0 ? (
                  <ul className="py-1">
                    {ingredientSuggestions.map((suggestion, index) => (
                      <li 
                        key={suggestion.id || `ing-${index}-${generateUniqueId()}`} 
                        className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                        onClick={() => selectIngredient(suggestion)}
                      >
                        {suggestion.name || suggestion}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-4 text-center">
                    <p className="text-gray-500 mb-2">No ingredients found</p>
                    <button
                      type="button"
                      onClick={() => {
                        // Add to database but don't add to recipe yet
                        addNewIngredient();
                        // Don't clear the name field so user can continue with quantity
                      }}
                      className="text-sm px-3 py-1 bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                      disabled={isProcessingAdd}
                    >
                      + Add "{currentIngredient.name}" to database
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Quantity input */}
          <div className="md:col-span-4">
            <label htmlFor="ingredient-quantity" className="block text-sm font-medium text-gray-700 mb-1">
              Quantity*
            </label>
            <input
              type="text"
              id="ingredient-quantity"
              value={currentIngredient.quantity}
              onChange={(e) => setCurrentIngredient({ ...currentIngredient, quantity: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="e.g., 2 tbsp, 1 cup"
            />
          </div>
          
          {/* Brand input with auto-suggestion */}
          <div className="md:col-span-3 relative">
            <label htmlFor="ingredient-brand" className="block text-sm font-medium text-gray-700 mb-1">
              Brand (optional)
            </label>
            <input
              type="text"
              id="ingredient-brand"
              value={currentIngredient.brand}
              onChange={(e) => {
                setCurrentIngredient({ ...currentIngredient, brand: e.target.value });
                setShowBrandSuggestions(true);
              }}
              onFocus={() => selectedIngredientId && setShowBrandSuggestions(true)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="e.g., Tata, MDH"
              disabled={!selectedIngredientId}
            />
            
            {/* Brand Suggestions */}
            {showBrandSuggestions && currentIngredient.brand && selectedIngredientId && (
              <div 
                ref={brandSuggestionsRef}
                className="absolute z-10 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-auto"
              >
                {isLoadingBrands ? (
                  <div className="p-4 text-center">
                    <span className="inline-block animate-spin mr-2">⟳</span> Loading...
                  </div>
                ) : brandSuggestions.length > 0 ? (
                  <ul className="py-1">
                    {brandSuggestions.map((suggestion, index) => (
                      <li 
                        key={suggestion.id || `brand-${index}-${generateUniqueId()}`} 
                        className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                        onClick={() => selectBrand(suggestion)}
                      >
                        {suggestion.name || suggestion}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="p-4 text-center">
                    <p className="text-gray-500 mb-2">No brands found</p>
                    <button
                      type="button"
                      onClick={addNewBrand}
                      className="text-sm px-3 py-1 bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                      disabled={isLoadingBrands}
                    >
                      + Add "{currentIngredient.brand}" to database
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Add button */}
        <div className="mt-4">
          <button
            type="button"
            onClick={addIngredientToRecipe}
            disabled={!currentIngredient.name || !currentIngredient.quantity || isProcessingAdd}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isProcessingAdd ? (
              <><span className="inline-block animate-spin mr-2">⟳</span> Processing...</>
            ) : (
              'Add Ingredient'
            )}
          </button>
        </div>
      </div>
      
      {/* List of added ingredients */}
      <div className="mt-6">
        <h3 className="font-medium text-gray-700 mb-2">Added Ingredients:</h3>
        {recipeData.ingredients.length === 0 ? (
          <p className="text-gray-500 italic">No ingredients added yet</p>
        ) : (
          <ul className="space-y-2">
            {recipeData.ingredients.map((ing, index) => (
              <li key={ing.id} className="relative p-3 bg-white border border-gray-200 shadow-sm rounded-md">
                {editingId === ing.id ? (
                  // Edit form
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
                    <div className="md:col-span-5 relative">
                      <input
                        type="text"
                        value={editForm.name}
                        onChange={(e) => {
                          setEditForm({ ...editForm, name: e.target.value });
                          setEditIngredientId(null);
                          setShowEditIngredientSuggestions(true);
                        }}
                        onFocus={() => setShowEditIngredientSuggestions(true)}
                        className="w-full px-3 py-1 border border-gray-300 rounded-md"
                        placeholder="Ingredient name"
                      />
                      
                      {/* Ingredient Suggestions for Edit */}
                      {showEditIngredientSuggestions && editForm.name && (
                        <div 
                          ref={editIngredientSuggestionsRef}
                          className="absolute z-20 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-auto"
                        >
                          {isLoadingEditIngredients ? (
                            <div className="p-4 text-center">
                              <span className="inline-block animate-spin mr-2">⟳</span> Loading...
                            </div>
                          ) : editIngredientSuggestions.length > 0 ? (
                            <ul className="py-1">
                              {editIngredientSuggestions.map((suggestion, index) => (
                                <li 
                                  key={suggestion.id || `edit-ing-${index}-${generateUniqueId()}`} 
                                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                                  onClick={() => selectEditIngredient(suggestion)}
                                >
                                  {suggestion.name || suggestion}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="p-4 text-center">
                              <p className="text-gray-500 mb-2">No ingredients found</p>
                              <button
                                type="button"
                                onClick={async () => {
                                  // Just add to database but stay in edit mode
                                  const success = await handleAddNewEditIngredient();
                                  if (success) {
                                    // Don't call updateIngredients here, let the user save manually
                                  }
                                }}
                                className="text-sm px-3 py-1 bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                                disabled={isLoadingEditIngredients}
                              >
                                + Add "{editForm.name}" to database
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="md:col-span-4">
                      <input
                        type="text"
                        value={editForm.quantity}
                        onChange={(e) => setEditForm({ ...editForm, quantity: e.target.value })}
                        className="w-full px-3 py-1 border border-gray-300 rounded-md"
                        placeholder="Quantity"
                      />
                    </div>
                    
                    <div className="md:col-span-3 relative">
                      <input
                        type="text"
                        value={editForm.brand}
                        onChange={(e) => {
                          setEditForm({ ...editForm, brand: e.target.value });
                          setShowEditBrandSuggestions(true);
                        }}
                        onFocus={() => editIngredientId && setShowEditBrandSuggestions(true)}
                        className="w-full px-3 py-1 border border-gray-300 rounded-md"
                        placeholder="Brand (optional)"
                        disabled={!editIngredientId}
                      />
                      
                      {/* Brand Suggestions for Edit */}
                      {showEditBrandSuggestions && editForm.brand && editIngredientId && (
                        <div 
                          ref={editBrandSuggestionsRef}
                          className="absolute z-20 mt-1 w-full bg-white shadow-lg rounded-md border border-gray-200 max-h-60 overflow-auto"
                        >
                          {isLoadingEditBrands ? (
                            <div className="p-4 text-center">
                              <span className="inline-block animate-spin mr-2">⟳</span> Loading...
                            </div>
                          ) : editBrandSuggestions.length > 0 ? (
                            <ul className="py-1">
                              {editBrandSuggestions.map((suggestion, index) => (
                                <li 
                                  key={suggestion.id || `edit-brand-${index}-${generateUniqueId()}`} 
                                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                                  onClick={() => selectEditBrand(suggestion)}
                                >
                                  {suggestion.name || suggestion}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="p-4 text-center">
                              <p className="text-gray-500 mb-2">No brands found</p>
                              <button
                                type="button"
                                onClick={addNewEditBrand}
                                className="text-sm px-3 py-1 bg-green-100 text-green-800 rounded-md hover:bg-green-200"
                                disabled={isLoadingEditBrands}
                              >
                                + Add "{editForm.brand}" to database
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    
                    <div className="md:col-span-12 flex justify-end space-x-2">
                      <button
                        type="button"
                        onClick={cancelEditing}
                        className="px-3 py-1 border border-gray-300 text-gray-600 rounded-md hover:bg-gray-50"
                        disabled={isProcessingSave}
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        onClick={saveEdit}
                        className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700"
                        disabled={!editForm.name || !editForm.quantity || isProcessingSave}
                      >
                        {isProcessingSave ? (
                          <><span className="inline-block animate-spin mr-2">⟳</span> Saving...</>
                        ) : (
                          'Save'
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  // Display mode
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center mr-3">
                        {index + 1}
                      </span>
                      <div>
                        <span className="font-medium">{ing.quantity}</span> {ing.name}
                        {ing.brand && <span className="text-gray-500 text-sm ml-2">({ing.brand})</span>}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        type="button"
                        onClick={() => startEditing(ing)}
                        className="text-blue-500 hover:text-blue-700 p-1 hover:bg-blue-50 rounded-full"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        onClick={() => removeIngredient(ing.id)}
                        className="text-red-500 hover:text-red-700 p-1 hover:bg-red-50 rounded-full"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default IngredientsStep;