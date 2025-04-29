// src/components/recipes/ImageUploader.jsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useToast } from '@/contexts/ToastContext';

export default function ImageUploader({ onImageUpload, currentImage = null, id = "image-uploader", shouldClear = false }) {
  const [isUploading, setIsUploading] = useState(false);
  const [preview, setPreview] = useState(currentImage);
  const { showToast } = useToast();
  const fileInputRef = useRef(null);
  
  // This effect watches for external triggers to clear the image
  useEffect(() => {
    if (shouldClear) {
      clearImage();
    }
  }, [shouldClear]);
  
  // Watch currentImage prop changes
  useEffect(() => {
    setPreview(currentImage);
  }, [currentImage]);

  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file type
    if (!file.type.match('image.*')) {
      showToast('Please select an image file', 'error');
      return;
    }

    // Check file size (limit to 5MB)
    if (file.size > 5 * 1024 * 1024) {
      showToast('Image size should be less than 5MB', 'error');
      return;
    }

    setIsUploading(true);

    try {
      // Set up preview immediately
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
        // Safely call the callback function
        if (typeof onImageUpload === 'function') {
          onImageUpload(reader.result);
        }
      };
      reader.readAsDataURL(file);

      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append('image', file);

      // Upload to your local server
      const response = await fetch('/api/upload-image', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to upload image');
      }

      // Call the callback with the image path
      if (typeof onImageUpload === 'function') {
        onImageUpload(data.imagePath);
      }
      
      showToast('Image uploaded successfully', 'success');
      
      console.log('Upload successful, image path:', data.imagePath);
      
    } catch (error) {
      console.error('Error uploading image:', error);
      showToast('Failed to upload image: ' + error.message, 'error');
      // Reset preview on error
      setPreview(currentImage);
    } finally {
      setIsUploading(false);
    }
  };

  // Method to clear the image uploader
  const clearImage = () => {
    console.log('Clearing image uploader');
    setPreview(null);
    if (typeof onImageUpload === 'function') {
      onImageUpload(null);
    }
    // Also reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // This method can be exposed to parent components
  React.useImperativeHandle(
    fileInputRef,
    () => ({
      clearImage,
      fileInput: fileInputRef.current
    }),
    [fileInputRef]
  );

  return (
    <div className="mt-4" data-uploader-id={id}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Recipe Image (Optional)
      </label>
      
      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          {preview ? (
            <div className="relative w-36 h-36 rounded-md overflow-hidden">
              <img 
                src={preview} 
                alt="Recipe preview" 
                className="w-full h-full object-cover"
              />
              <button
                type="button"
                onClick={clearImage}
                className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ) : (
            <div className="w-36 h-36 border-2 border-dashed border-gray-300 rounded-md flex items-center justify-center bg-gray-50">
              <svg className="h-12 w-12 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          )}
        </div>
        
        <div className="flex-1">
          <label className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
            <span>{isUploading ? 'Uploading...' : 'Choose Image'}</span>
            <input 
              type="file" 
              className="sr-only" 
              onChange={handleImageChange} 
              accept="image/*" 
              disabled={isUploading}
              ref={fileInputRef}
              id={id}
            />
          </label>
          <p className="mt-2 text-xs text-gray-500">
            PNG, JPG, or WEBP up to 5MB
          </p>
          
          {/* Debug button - remove in production */}
          <button 
            type="button" 
            onClick={clearImage}
            className="mt-2 text-xs text-blue-500 underline"
          >
            Clear Image
          </button>
        </div>
      </div>
    </div>
  );
}