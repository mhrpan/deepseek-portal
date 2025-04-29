'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useToast } from '@/contexts/ToastContext';

export default function FamilyManagement() {
  const [families, setFamilies] = useState([]);
  const [members, setMembers] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFamily, setSelectedFamily] = useState(null);
  const [showAddFamilyModal, setShowAddFamilyModal] = useState(false);
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [newFamilyName, setNewFamilyName] = useState('');
  const [newMember, setNewMember] = useState({
    email: '',
    name: '',
    phone: '',
    relation: ''
  });
  const { showToast } = useToast();
  const maxFamilyMembers = 4;

  useEffect(() => {
    const fetchFamilies = async () => {
      try {
        setIsLoading(true);
        // In a real app, fetch from API
        const response = await fetch('http://localhost:5000/api/families', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          setFamilies(data);
          if (data.length > 0) {
            setSelectedFamily(data[0].id);
          }
        } else {
          throw new Error('Failed to fetch families');
        }
      } catch (error) {
        console.error('Error fetching families:', error);
        // Use mock data as fallback
        setFamilies([
          {
            id: '1',
            name: 'My Family',
            created_at: '2025-03-10T18:25:43.511Z',
          }
        ]);
        setSelectedFamily('1');
        showToast('Failed to load family data', 'error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchFamilies();
  }, [showToast]);

  useEffect(() => {
    if (selectedFamily) {
      const fetchMembers = async () => {
        try {
          // In a real app, fetch from API
          const response = await fetch(`http://localhost:5000/api/families/${selectedFamily}/members`, {
            credentials: 'include'
          });
          
          if (response.ok) {
            const data = await response.json();
            setMembers(data);
          } else {
            throw new Error('Failed to fetch family members');
          }
        } catch (error) {
          console.error('Error fetching members:', error);
          // Use mock data as fallback
          setMembers([
            {
              id: '1',
              family_id: selectedFamily,
              user_id: '101',
              email: 'mom@example.com',
              first_name: 'Mom',
              last_name: 'Smith',
              role: 'member',
              relationship: 'Mother',
              invitation_status: 'accepted',
              joined_at: '2025-03-15T18:25:43.511Z',
            }
          ]);
        }
      };

      fetchMembers();
    }
  }, [selectedFamily]);

  const handleCreateFamily = async () => {
    if (!newFamilyName.trim()) {
      showToast('Please enter a family name', 'error');
      return;
    }

    try {
      // In a real app, send to API
      const response = await fetch('http://localhost:5000/api/families', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newFamilyName }),
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.family) {
          setFamilies([...families, data.family]);
          setSelectedFamily(data.family.id);
          setNewFamilyName('');
          setShowAddFamilyModal(false);
          showToast('Family created successfully', 'success');
        } else {
          throw new Error(data.message || 'Failed to create family');
        }
      } else {
        throw new Error('Failed to create family');
      }
    } catch (error) {
      console.error('Error creating family:', error);
      showToast(error.message || 'Failed to create family', 'error');
    }
  };

 const handleAddMember = async () => {
  const { email, name, phone, relation } = newMember;
  
  // Validate required fields
  if (!email.trim() || !name.trim() || !selectedFamily) {
    showToast('Please enter name and email address', 'error');
    return;
  }
  
  // Check member limit
  if (members.length >= maxFamilyMembers) {
    showToast(`You can add up to ${maxFamilyMembers} family members`, 'error');
    return;
  }
  
  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showToast('Please enter a valid email address', 'error');
    return;
  }
  
  try {
    console.log('Sending invitation data:', { email, name, phone, relation });
    
    const response = await fetch(`http://localhost:5000/api/families/${selectedFamily}/members`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        email,
        name,
        phone,
        relation
      }),
      credentials: 'include'
    });
    
    // Get full response text for better debugging
    const responseText = await response.text();
    console.log('Response status:', response.status);
    console.log('Response text:', responseText);
    
    // Only try to parse JSON if there's content
    let data;
    if (responseText) {
      try {
        data = JSON.parse(responseText);
      } catch (e) {
        console.error('Failed to parse JSON response:', e);
        throw new Error(`Server returned invalid JSON: ${responseText.substring(0, 100)}...`);
      }
    } else {
      throw new Error('Empty response from server');
    }
    
    // Handle successful response
    if (data && data.status === 'success') {
      if (data.pending) {
        showToast('Invitation sent successfully', 'success');
      } else if (data.member) {
        setMembers([...members, data.member]);
        showToast('Member added successfully', 'success');
      }
      // Reset form and close modal
      setNewMember({ email: '', name: '', phone: '', relation: '' });
      setShowAddMemberModal(false);
    } else {
      throw new Error(data?.message || 'Unknown error occurred');
    }
  } catch (error) {
    console.error('Error adding family member:', error);
    showToast(`Failed to add member: ${error.message}`, 'error');
  }
};

  const handleRemoveMember = async (memberId) => {
    if (!confirm('Are you sure you want to remove this member?')) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:5000/api/families/${selectedFamily}/members/${memberId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setMembers(members.filter(member => member.id !== memberId));
          showToast('Member removed successfully', 'success');
        } else {
          throw new Error(data.message || 'Failed to remove member');
        }
      } else {
        throw new Error('Failed to remove member');
      }
    } catch (error) {
      console.error('Error removing member:', error);
      showToast(error.message || 'Failed to remove member', 'error');
    }
  };

  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const familyMembers = members.filter(member => member.family_id === selectedFamily);
  const memberCount = familyMembers.length;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Family Management</h1>
        <button
          type="button"
          onClick={() => setShowAddFamilyModal(true)}
          className="mt-3 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Create New Family
        </button>
      </div>

      {/* Family management UI... */}
      {families.length === 0 ? (
        <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-8 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No families yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Create a family to share your recipes with loved ones.
            </p>
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setShowAddFamilyModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Create Family
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Family List */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow sm:rounded-md">
              <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  My Families
                </h3>
              </div>
              <ul className="divide-y divide-gray-200">
                {families.map((family) => (
                  <li key={family.id}>
                    <button
                      onClick={() => setSelectedFamily(family.id)}
                      className={`w-full text-left px-4 py-4 flex items-center hover:bg-gray-50 focus:outline-none ${
                        selectedFamily === family.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {family.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          Created on {formatDate(family.created_at)}
                        </p>
                      </div>
                      {selectedFamily === family.id && (
                        <div className="ml-3 flex-shrink-0">
                          <svg className="h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Family Members */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow sm:rounded-md">
              <div className="px-4 py-5 border-b border-gray-200 sm:px-6 flex justify-between items-center">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    {selectedFamily ? 
                      `Members of ${families.find(f => f.id === selectedFamily)?.name}` : 
                      'Select a family to see members'}
                  </h3>
                  {memberCount > 0 && (
                    <p className="mt-1 text-sm text-gray-500">
                      {memberCount} of {maxFamilyMembers} members
                    </p>
                  )}
                </div>
                {selectedFamily && memberCount < maxFamilyMembers && (
                  <button
                    type="button"
                    onClick={() => setShowAddMemberModal(true)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Add Member
                  </button>
                )}
              </div>
              {selectedFamily ? (
                <div>
                  {familyMembers.length === 0 ? (
                    <div className="px-4 py-8 text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No members yet</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Invite family members to share your recipes.
                      </p>
                      <div className="mt-6">
                        <button
                          type="button"
                          onClick={() => setShowAddMemberModal(true)}
                          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                          <svg className="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                          </svg>
                          Add Member
                        </button>
                      </div>
                    </div>
                  ) : (
                    <ul className="divide-y divide-gray-200">
                      {familyMembers.map((member) => (
                        <li key={member.id} className="px-4 py-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                <span className="text-gray-500 font-medium text-sm">
                                  {member.first_name?.[0] || '?'}{member.last_name?.[0] || '?'}
                                </span>
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">
                                  {member.first_name} {member.last_name}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {member.email}
                                </div>
                                {member.relationship && (
                                  <div className="text-xs text-gray-400">
                                    Relation: {member.relationship}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                ${member.invitation_status === 'accepted' 
                                  ? 'bg-green-100 text-green-800' 
                                  : 'bg-yellow-100 text-yellow-800'}`}
                              >
                                {member.invitation_status === 'accepted' ? 'Active' : 'Pending'}
                              </span>
                              <button
                                type="button"
                                onClick={() => handleRemoveMember(member.id)}
                                className="ml-4 text-red-600 hover:text-red-900"
                              >
                                Remove
                              </button>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                <div className="px-4 py-8 text-center">
                  <p className="text-sm text-gray-500">
                    Please select a family from the list to view members.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Family Modal */}
      {showAddFamilyModal && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">Create a new family</h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    Creating a new family allows you to share your recipes with loved ones.
                  </p>
                </div>
              </div>
              <div className="mt-5">
                <label htmlFor="family-name" className="block text-sm font-medium text-gray-700">
                  Family Name
                </label>
                <input
                  type="text"
                  id="family-name"
                  name="family-name"
                  value={newFamilyName}
                  onChange={(e) => setNewFamilyName(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., My Family Cookbook"
                  required
                />
              </div>
              <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                <button
                  type="button"
                  onClick={handleCreateFamily}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:col-start-2 sm:text-sm"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddFamilyModal(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Member Modal - Updated with more fields */}
      {showAddMemberModal && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Add a member to {families.find(f => f.id === selectedFamily)?.name}
                </h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    Enter their information and we'll send them an invitation to join your family.
                  </p>
                </div>
              </div>
              <div className="mt-5 space-y-4">
                <div>
                  <label htmlFor="member-name" className="block text-sm font-medium text-gray-700">
                    Name*
                  </label>
                  <input
                    type="text"
                    id="member-name"
                    name="member-name"
                    value={newMember.name}
                    onChange={(e) => setNewMember({...newMember, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., John Doe"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="member-email" className="block text-sm font-medium text-gray-700">
                    Email Address*
                  </label>
                  <input
                    type="email"
                    id="member-email"
                    name="member-email"
                    value={newMember.email}
                    onChange={(e) => setNewMember({...newMember, email: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., relative@example.com"
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="member-phone" className="block text-sm font-medium text-gray-700">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    id="member-phone"
                    name="member-phone"
                    value={newMember.phone}
                    onChange={(e) => setNewMember({...newMember, phone: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., +1 555-123-4567"
                  />
                </div>
                
                <div>
                  <label htmlFor="member-relation" className="block text-sm font-medium text-gray-700">
                    Relationship
                  </label>
                  <select
                    id="member-relation"
                    name="member-relation"
                    value={newMember.relation}
                    onChange={(e) => setNewMember({...newMember, relation: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select relationship</option>
                    <option value="Spouse">Spouse</option>
                    <option value="Parent">Parent</option>
                    <option value="Child">Child</option>
                    <option value="Sibling">Sibling</option>
                    <option value="Friend">Friend</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
              <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                <button
                  type="button"
                  onClick={handleAddMember}
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:col-start-2 sm:text-sm"
                >
                  Send Invitation
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddMemberModal(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}