import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white py-6 min-h-[50px] z-10">
      <div className="text-center text-gray-500 text-sm mt-6 ">
        © {new Date().getFullYear()} SkiWise. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
