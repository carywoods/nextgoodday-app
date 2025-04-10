import React, { useState } from 'react';

const Onboarding = ({ onSubmit, error }) => {
  const [formData, setFormData] = useState({
    email: '',
    age_range: '',
    gender: ''
  });
  const [validationErrors, setValidationErrors] = useState({});

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation error when field is modified
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  // Validate the form
  const validateForm = () => {
    const errors = {};
    
    // Validate email
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }
    
    // Validate age range
    if (!formData.age_range) {
      errors.age_range = 'Age range is required';
    }
    
    // Gender is optional, no validation needed
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8 transition-all">
      <h2 className="text-2xl font-bold text-blue-700 mb-6">Welcome to The Next Good Day</h2>
      <p className="text-gray-600 mb-6">
        Tell us a bit about yourself so we can help you find the perfect days for your activities.
      </p>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        {/* Email Input */}
        <div className="mb-4">
          <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validationErrors.email ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="you@example.com"
          />
          {validationErrors.email && (
            <p className="text-red-500 text-xs mt-1">{validationErrors.email}</p>
          )}
        </div>
        
        {/* Age Range Dropdown */}
        <div className="mb-4">
          <label htmlFor="age_range" className="block text-gray-700 font-medium mb-2">
            Age Range
          </label>
          <select
            id="age_range"
            name="age_range"
            value={formData.age_range}
            onChange={handleChange}
            className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validationErrors.age_range ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select your age range</option>
            <option value="18-24">18-24</option>
            <option value="25-34">25-34</option>
            <option value="35-44">35-44</option>
            <option value="45-54">45-54</option>
            <option value="55+">55 and above</option>
          </select>
          {validationErrors.age_range && (
            <p className="text-red-500 text-xs mt-1">{validationErrors.age_range}</p>
          )}
        </div>
        
        {/* Gender Radio Buttons */}
        <div className="mb-6">
          <label className="block text-gray-700 font-medium mb-2">
            Gender (Optional)
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="gender"
                value="male"
                checked={formData.gender === 'male'}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Male</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="gender"
                value="female"
                checked={formData.gender === 'female'}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Female</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="gender"
                value="other"
                checked={formData.gender === 'other'}
                onChange={handleChange}
                className="mr-2"
              />
              <span>Other</span>
            </label>
          </div>
        </div>
        
        {/* Submit Button */}
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Find My Next Good Day
        </button>
      </form>
    </div>
  );
};

export default Onboarding;
