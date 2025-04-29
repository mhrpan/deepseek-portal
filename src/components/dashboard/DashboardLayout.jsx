'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

export default function DashboardLayout({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    // Check for user in localStorage
    const storedUser = localStorage.getItem('user');
    
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing user data:', error);
        setShouldRedirect(true);
      }
    } else {
      setShouldRedirect(true);
    }
    
    // Verify user session with backend
    const verifyUser = async () => {
      try {
        const response = await fetch('http://localhost:5000/auth/api/user', {
          method: 'GET',
          credentials: 'include'
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
          setShouldRedirect(false);
        } else {
          // If the session is invalid, mark for redirection
          localStorage.removeItem('user');
          setShouldRedirect(true);
        }
      } catch (error) {
        console.error('Error verifying user:', error);
        setShouldRedirect(true);
      } finally {
        setIsLoading(false);
      }
    };
    
    verifyUser();
  }, []);
  
  // Handle redirect in an effect, not during render
  useEffect(() => {
    if (shouldRedirect && !isLoading) {
      router.push('/login');
    }
  }, [shouldRedirect, isLoading, router]);
  
  // Handle logout
  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5000/auth/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
      
      // Clear local storage and redirect to login
      localStorage.removeItem('user');
      router.push('/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };
  
  // If still loading, show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }
  
  // If no user after loading and not yet redirecting, return null
  if (!user && !isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
        <p className="ml-2">Redirecting to login...</p>
      </div>
    );
  }

  // Define navigation items
  const navItems = [
    { name: 'Dashboard', href: '/dashboard' },
    { name: 'Add Recipe', href: '/recipes/create' },
    { name: 'My Recipes', href: '/dashboard/recipes' },
    { name: 'Shared With Me', href: '/dashboard/shared' },
    { name: 'Family Members', href: '/dashboard/family' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-green-600">Recipe Keeper</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navItems.map(item => (
                  <Link 
                    key={item.name}
                    href={item.href}
                    className={`${
                      pathname === item.href
                        ? 'border-green-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center">
              <div className="hidden md:ml-4 md:flex-shrink-0 md:flex md:items-center">
                <div className="ml-3 relative flex items-center gap-4">
                  <div className="text-sm font-medium text-gray-700">
                    {user?.first_name} {user?.last_name}
                  </div>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Mobile menu */}
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {navItems.map(item => (
              <Link
                key={item.name}
                href={item.href}
                className={`${
                  pathname === item.href
                    ? 'bg-green-50 border-green-500 text-green-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800'
                } block pl-3 pr-4 py-2 border-l-4 text-base font-medium`}
              >
                {item.name}
              </Link>
            ))}
            <button
              onClick={handleLogout}
              className="block w-full text-left pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {children}
        </div>
      </div>
    </div>
  );
}