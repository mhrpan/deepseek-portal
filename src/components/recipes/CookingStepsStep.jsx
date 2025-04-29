// src/components/recipes/CookingStepsStep.jsx
import React, { useState, useRef, useEffect } from 'react';
import ImageUploader from './ImageUploader';
import VoiceInput from './VoiceInput';

// Helper function to generate unique IDs
const generateUniqueId = () => {
  return `id-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

const CookingStepsStep = ({ recipeData, updateRecipeData }) => {
  const [currentStep, setCurrentStep] = useState({
    instruction: '',
    hasImage: false,
    stepImage: null
  });

  // State to trigger image clearing
  const [clearAddImage, setClearAddImage] = useState(false);
  const [clearEditImage, setClearEditImage] = useState(false);

  // New state for editing
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({
    instruction: '',
    hasImage: false,
    stepImage: null
  });

  // Loading states
  const [isProcessingAdd, setIsProcessingAdd] = useState(false);
  const [isProcessingSave, setIsProcessingSave] = useState(false);
  
  // Reset the clear trigger after it's been used
  useEffect(() => {
    if (clearAddImage) {
      setTimeout(() => setClearAddImage(false), 100);
    }
  }, [clearAddImage]);
  
  useEffect(() => {
    if (clearEditImage) {
      setTimeout(() => setClearEditImage(false), 100);
    }
  }, [clearEditImage]);

  const handleAddStep = () => {
    if (currentStep.instruction.trim() === '') return;
    
    try {
      setIsProcessingAdd(true);
      
      const newSteps = [...recipeData.steps, { 
        ...currentStep, 
        id: generateUniqueId()  // Use our guaranteed unique function
      }];
      
      updateRecipeData('steps', newSteps);
      
      // Reset form completely including the image uploader
      setCurrentStep({
        instruction: '',
        hasImage: false,
        stepImage: null
      });
      
      // Trigger image clearing
      setClearAddImage(true);
      
      // Force clear the image uploader component using various methods
      // Method 1: Direct clear via DOM
      const fileInput = document.querySelector('#step-image-uploader');
      if (fileInput) {
        fileInput.value = '';
      }
      
      // Method 2: Clear all file inputs within the uploader container
      const uploadContainer = document.querySelector('[data-uploader-id="step-image-uploader"]');
      if (uploadContainer) {
        const fileInputs = uploadContainer.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
          input.value = '';
        });
      }
      
      // Method 3: Find the clear button and click it programmatically
      const clearButton = document.querySelector('[data-uploader-id="step-image-uploader"] button');
      if (clearButton) {
        clearButton.click();
      }
      
    } catch (error) {
      console.error("Error adding step:", error);
    } finally {
      setIsProcessingAdd(false);
    }
  };

  const handleRemoveStep = (id) => {
    const newSteps = recipeData.steps.filter(step => step.id !== id);
    updateRecipeData('steps', newSteps);
  };

  const handleStepImageUpload = (imagePath) => {
    setCurrentStep({
      ...currentStep,
      stepImage: imagePath,
      hasImage: !!imagePath
    });
  };

  const handleEditStepImageUpload = (imagePath) => {
    setEditForm({
      ...editForm,
      stepImage: imagePath,
      hasImage: !!imagePath
    });
  };

  const handleVoiceCapture = (text) => {
    setCurrentStep({
      ...currentStep,
      instruction: text
    });
  };

  const handleEditVoiceCapture = (text) => {
    setEditForm({
      ...editForm,
      instruction: text
    });
  };

  // Start editing a step
  const startEditing = (step) => {
    console.log("Started editing step:", step);
    setEditingId(step.id);
    setEditForm({
      instruction: step.instruction,
      hasImage: !!step.stepImage,
      stepImage: step.stepImage
    });
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingId(null);
    setClearEditImage(true);
  };

  // Save edits
  const saveEdit = () => {
    if (!editForm.instruction.trim()) {
      return; // Don't save empty instructions
    }
    
    try {
      setIsProcessingSave(true);
      
      const updatedSteps = recipeData.steps.map(step => 
        step.id === editingId ? {
          ...step,
          instruction: editForm.instruction,
          hasImage: editForm.hasImage,
          stepImage: editForm.stepImage
        } : step
      );
      
      updateRecipeData('steps', updatedSteps);
      setEditingId(null);
      
      // Trigger clearing of edit image
      setClearEditImage(true);
      
    } catch (error) {
      console.error("Error saving step edit:", error);
    } finally {
      setIsProcessingSave(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Step input form */}
      <div className="p-4 border border-gray-200 rounded-md bg-gray-50">
        <h3 className="font-medium text-gray-700 mb-3">Add Cooking Step</h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="step-instruction" className="block text-sm font-medium text-gray-700 mb-1">
              Instructions*
            </label>
            <textarea
              id="step-instruction"
              value={currentStep.instruction}
              onChange={(e) => setCurrentStep({ ...currentStep, instruction: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="Describe this step (e.g., 'Mix flour and water until smooth')"
              rows={3}
            />
            <VoiceInput onCapture={handleVoiceCapture} />
          </div>
          
          {/* Image uploader for the step */}
          <div id="step-image-uploader-container">
            <ImageUploader 
              onImageUpload={handleStepImageUpload} 
              currentImage={currentStep.stepImage}
              id="step-image-uploader"
              shouldClear={clearAddImage}
            />
          </div>
        </div>
        
        {/* Add button */}
        <div className="mt-4">
          <button
            type="button"
            onClick={handleAddStep}
            disabled={!currentStep.instruction.trim() || isProcessingAdd}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {isProcessingAdd ? (
              <><span className="inline-block animate-spin mr-2">⟳</span> Adding...</>
            ) : (
              'Add Step'
            )}
          </button>
        </div>
      </div>
      
      {/* List of added steps */}
      <div className="mt-6">
        <h3 className="font-medium text-gray-700 mb-2">Recipe Steps:</h3>
        {recipeData.steps.length === 0 ? (
          <p className="text-gray-500 italic">No steps added yet</p>
        ) : (
          <ol className="space-y-4">
            {recipeData.steps.map((step, index) => (
              <li key={step.id} className="p-4 bg-white border border-gray-200 shadow-sm rounded-md">
                {editingId === step.id ? (
                  // Edit mode
                  <div className="space-y-4">
                    <div className="flex items-start">
                      <span className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center mr-4">
                        {index + 1}
                      </span>
                      <div className="flex-1">
                        <textarea
                          value={editForm.instruction}
                          onChange={(e) => setEditForm({ ...editForm, instruction: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
                          rows={3}
                        />
                        <VoiceInput onCapture={handleEditVoiceCapture} />
                        
                        {/* Image uploader for the step */}
                        <div id="edit-step-image-uploader-container">
                          <ImageUploader 
                            onImageUpload={handleEditStepImageUpload} 
                            currentImage={editForm.stepImage}
                            id="edit-step-image-uploader"
                            shouldClear={clearEditImage}
                          />
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
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
                        disabled={!editForm.instruction.trim() || isProcessingSave}
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
                  <div className="flex items-start">
                    <span className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center mr-4">
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <p className="text-gray-800">{step.instruction}</p>
                      {step.stepImage && (
                        <div className="mt-2">
                          <img 
                            src={step.stepImage} 
                            alt={`Step ${index + 1}`} 
                            className="h-28 object-cover rounded-md border border-gray-200"
                          />
                        </div>
                      )}
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        type="button"
                        onClick={() => startEditing(step)}
                        className="text-blue-500 hover:text-blue-700 p-1 hover:bg-blue-50 rounded-full"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleRemoveStep(step.id)}
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
          </ol>
        )}
      </div>
    </div>
  );
};

export default CookingStepsStep;