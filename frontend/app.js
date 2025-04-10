// API base URL
const API_BASE_URL = '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchApi(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * Create a new user
 */
export async function createUser(userData) {
  return await fetchApi('/users', {
    method: 'POST',
    body: JSON.stringify(userData)
  });
}

/**
 * Get user by ID
 */
export async function getUser(userId) {
  return await fetchApi(`/users/${userId}`);
}

/**
 * Get activities, optionally filtered by demographics
 */
export async function getActivities(ageRange = null, gender = null) {
  let queryParams = '';
  
  if (ageRange || gender) {
    const params = new URLSearchParams();
    if (ageRange) params.append('age_range', ageRange);
    if (gender) params.append('gender', gender);
    queryParams = `?${params.toString()}`;
  }
  
  return await fetchApi(`/activities${queryParams}`);
}

/**
 * Add activity to user profile and get recommendations
 */
export async function addUserActivity(userId, activityData) {
  return await fetchApi(`/users/${userId}/activities`, {
    method: 'POST',
    body: JSON.stringify(activityData)
  });
}

/**
 * Get recommendations for a user, optionally filtered by activity
 */
export async function getUserRecommendations(userId, activityId = null) {
  let queryParams = '';
  
  if (activityId) {
    queryParams = `?activity_id=${activityId}`;
  }
  
  return await fetchApi(`/users/${userId}/recommendations${queryParams}`);
}

/**
 * Create an invitation email for a recommendation
 */
export async function createInviteEmail(recommendationId, recipientEmail) {
  return await fetchApi(`/recommendations/${recommendationId}/invite`, {
    method: 'POST',
    body: JSON.stringify({ 
      recommendation_id: recommendationId,
      recipient_email: recipientEmail
    })
  });
}

/**
 * Get a calendar file for a recommendation
 */
export async function getCalendarFile(recommendationId) {
  return await fetchApi(`/recommendations/${recommendationId}/calendar`);
}

/**
 * Download calendar file
 */
export function downloadCalendarFile(icsContent, filename) {
  const blob = new Blob([icsContent], { type: 'text/calendar' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
