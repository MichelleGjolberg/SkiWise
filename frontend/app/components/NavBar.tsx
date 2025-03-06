import React from 'react';
import { Link } from '@remix-run/react';

const NavBar: React.FC = () => {
  return (
    <nav className="absolute top-0 left-0 text-white p-4 z-10">
      <div className="px-4 mx-auto flex items-center">
        <Link to="/" className="text-xl font-bold flex items-center">
          SkiWise
          <img
            src="/whiteSnowFlake.png"
            alt="SkiWise Logo"
            className="h-6 px-1"
          />
        </Link>
      </div>
    </nav>
  );
};
export default NavBar;
