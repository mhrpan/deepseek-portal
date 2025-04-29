// src/components/recipes/VoiceInput.jsx
'use client';

import React, { useState, useEffect } from 'react';

export default function VoiceInput({ onCapture }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = React.useRef(null);

  useEffect(() => {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false);
    }
    
    // Clean up on unmount
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startListening = () => {
    // Clear previous transcript when starting a new recording
    setTranscript('');
    setIsListening(true);

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';  // Set language

    recognition.onresult = (event) => {
      let currentTranscript = '';
      
      // Only use the latest results, not cumulative
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcriptText = result[0].transcript;
        
        if (result.isFinal) {
          currentTranscript += transcriptText;
        } else {
          // Update for interim results - replace rather than append
          setTranscript(transcriptText);
        }
      }
      
      // If we have final results, update the transcript
      if (currentTranscript) {
        setTranscript(currentTranscript);
        // Immediately pass it to the parent component
        onCapture(currentTranscript);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      // Make sure we capture any final text
      if (transcript) {
        onCapture(transcript);
      }
    };

    recognition.start();

    // Add a timeout to automatically stop after 15 seconds
    setTimeout(() => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    }, 15000);
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  if (!isSupported) {
    return (
      <div className="mt-2 text-xs text-gray-500">
        Voice input is not supported in your browser.
      </div>
    );
  }

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
          isListening 
            ? 'bg-red-100 text-red-800 animate-pulse' 
            : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
        }`}
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-5 w-5 mr-1" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" 
          />
        </svg>
        {isListening ? 'Stop Listening' : 'Add Step by Voice'}
      </button>
      
      {isListening && (
        <div className="mt-2 p-2 bg-gray-100 rounded-md">
          <p className="text-sm text-gray-600">
            {transcript || "Speak now..."}
          </p>
        </div>
      )}
    </div>
  );
}