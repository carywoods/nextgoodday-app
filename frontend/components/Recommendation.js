import React, { useState } from 'react';
import { createInviteEmail } from '../services/api';

const InviteForm = ({ recommendations, onSubmit }) => {
  const [formData, setFormData] = useState({
    recommendationId: '',
    email: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Reset messages
    setSuccess(false);
    setError(null);
  };

  // Format date for display in the dropdown
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.recommendationId || !formData.email) {
      setError('Please select a day and enter an email address.');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // In MVP, we're just storing the invite, not sending it
      const result = await createInviteEmail(
        formData.recommendationId,
        formData.email
      );
      
      setSuccess(true);
      setFormData({
        recommendationId: '',
        email: ''
      });
      
      // Call parent component's onSubmit if provided
      if (onSubmit) {
        onSubmit(formData.recommendationId, formData.email);
      }
    } catch (err) {
      console.error('Error creating invite:', err);
      setError('Unable to create invitation. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Don't show the form if there are no recommendations
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-xl font-bold text-blue-700 mb-4">Invite a Friend</h2>
      
      <p className="text-gray-600 mb-6">
        Share one of your recommended days with a friend!
      </p>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}
      
      {success && (
        <div className="bg-green-100 text-green-700 p-3 rounded mb-4 text-sm">
          Invitation created successfully! (In this MVP version, emails are stored but not sent.)
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        {/* Day Selection Dropdown */}
        <div className="mb-4">
          <label htmlFor="recommendationId" className="block text-gray-700 font-medium mb-2">
            Select a Day
          </label>
          <select
            id="recommendationId"
            name="recommendationId"
            value={formData.recommendationId}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="">Choose a day to share</option>
            {recommendations.map(recommendation => (
              <option key={recommendation.id} value={recommendation.id}>
                {formatDate(recommendation.date)} - {recommendation.weather_summary}
              </option>
            ))}
          </select>
        </div>
        
        {/* Friend's Email */}
        <div className="mb-4">
          <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
            Friend's Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="friend@example.com"
            required
          />
        </div>
        
        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-blue-300"
        >
          {loading ? 'Creating Invitation...' : 'Create Invitation'}
        </button>
        
        <p className="mt-3 text-xs text-gray-500 text-center">
          Note: In this MVP version, invitations are stored but not sent.
        </p>
      </form>
    </div>
  );
};

export default InviteForm;
