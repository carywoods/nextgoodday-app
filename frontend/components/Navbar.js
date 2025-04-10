import React from 'react';

const Navbar = ({ step }) => {
  // Define steps for progress indicator
  const steps = [
    { id: 1, name: 'Profile' },
    { id: 2, name: 'Activity' },
    { id: 3, name: 'Recommendations' }
  ];

  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col sm:flex-row justify-between items-center">
          {/* App Logo/Name */}
          <div className="flex items-center mb-4 sm:mb-0">
            <h1 className="text-xl font-bold text-blue-700">
              The Next Good Day
            </h1>
          </div>
          
          {/* Progress Steps */}
          <div className="flex items-center space-x-2">
            {steps.map((s, index) => (
              <React.Fragment key={s.id}>
                {/* Progress Step */}
                <div 
                  className={`flex items-center justify-center w-6 h-6 rounded-full ${
                    s.id === step
                      ? 'bg-blue-600 text-white'
                      : s.id < step
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {s.id < step ? (
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" 
                      className="h-4 w-4" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path 
                        fillRule="evenodd" 
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                        clipRule="evenodd" 
                      />
                    </svg>
                  ) : (
                    <span className="text-xs font-medium">{s.id}</span>
                  )}
                </div>
                
                {/* Step Name (visible on larger screens) */}
                <span className="hidden sm:inline-block text-xs text-gray-500">
                  {s.name}
                </span>
                
                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div 
                    className={`w-4 h-0.5 ${
                      step > s.id ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
