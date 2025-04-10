import React from 'react';

const Loading = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-8 flex flex-col items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
      <p className="text-gray-600">Loading your next good day...</p>
    </div>
  );
};

export default Loading;
