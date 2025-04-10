import React from 'react';

const ActivitySelector = ({ activities, onSelectActivity, error }) => {
  // Group activities by category for better organization
  const groupedActivities = activities.reduce((groups, activity) => {
    const category = activity.category || 'other';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(activity);
    return groups;
  }, {});

  // Get category display names
  const getCategoryName = (category) => {
    const categoryNames = {
      'outdoor': 'Outdoor Activities',
      'creative': 'Creative Activities',
      'social': 'Social Activities',
      'other': 'Other Activities'
    };
    return categoryNames[category] || 'Other Activities';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
      <h2 className="text-2xl font-bold text-blue-700 mb-4">Choose an Activity</h2>
      <p className="text-gray-600 mb-6">
        Select an activity you'd like to do, and we'll find the best days for it.
      </p>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      {activities.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading activities...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedActivities).map(([category, categoryActivities]) => (
            <div key={category}>
              <h3 className="text-lg font-medium text-gray-800 mb-3">
                {getCategoryName(category)}
              </h3>
              <div className="grid grid-cols-1 gap-2">
                {categoryActivities.map(activity => (
                  <button
                    key={activity.id}
                    onClick={() => onSelectActivity(activity)}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-center">
                      <div className="ml-3">
                        <div className="font-medium">{activity.name}</div>
                        {activity.description && (
                          <div className="text-sm text-gray-500">{activity.description}</div>
                        )}
                      </div>
                    </div>
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      className="h-5 w-5 text-blue-500" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path 
                        fillRule="evenodd" 
                        d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" 
                        clipRule="evenodd" 
                      />
                    </svg>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActivitySelector;
