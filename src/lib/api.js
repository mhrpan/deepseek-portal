// src/lib/api.js
const BASE_URL = 'http://localhost:5000/api';

async function fetchApi(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  console.log(`Fetching from: ${url}`);
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      credentials: 'include'  // This is crucial for authentication
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API error (${response.status}): ${errorText}`);
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error(`Fetch error for ${url}:`, error);
    throw error;
  }
}

// Recipe API calls
export async function createRecipe(recipeData) {
  console.log('Creating recipe with data:', recipeData);
  return fetchApi('/recipes', {
    method: 'POST',
    body: JSON.stringify(recipeData),
  });
}

export async function getUserRecipes() {
  return fetchApi('/user/recipes');
}

export async function getRecipeById(id) {
  return fetchApi(`/recipes/${id.toString()}`);
}

export async function deleteRecipe(id) {
  return fetchApi(`/recipes/${id}`, {
    method: 'DELETE',
  });
}

// Ingredients API calls
export async function getIngredients(searchTerm = '') {
  return fetchApi(`/ingredients?search=${encodeURIComponent(searchTerm)}`);
}

export async function addIngredient(ingredientData) {
  return fetchApi('/ingredients', {
    method: 'POST',
    body: JSON.stringify(ingredientData),
  });
}

// Brands API calls
export async function getBrands(ingredientId, searchTerm = '') {
  return fetchApi(`/brands?ingredient_id=${ingredientId}&search=${encodeURIComponent(searchTerm)}`);
}

export async function addBrand(brandData) {
  return fetchApi('/brands', {
    method: 'POST',
    body: JSON.stringify(brandData),
  });
}

// Add to src/lib/api.js
export async function updateRecipe(id, recipeData) {
  return fetchApi(`/recipes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(recipeData),
  });
}

// Family API calls
export async function getFamilies() {
  return fetchApi('/families');
}

export async function createFamily(familyData) {
  return fetchApi('/families', {
    method: 'POST',
    body: JSON.stringify(familyData),
  });
}

export async function getFamilyMembers(familyId) {
  return fetchApi(`/families/${familyId}/members`);
}

export async function addFamilyMember(familyId, memberData) {
  return fetchApi(`/families/${familyId}/members`, {
    method: 'POST',
    body: JSON.stringify(memberData),
  });
}

export async function removeFamilyMember(familyId, memberId) {
  return fetchApi(`/families/${familyId}/members/${memberId}`, {
    method: 'DELETE',
  });
}