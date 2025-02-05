import React from 'react';
import { Link } from '@remix-run/react';

const NavBar: React.FC = () => {
  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container px-10 mx-auto flex justify-between items-center">
        <Link to="/" className="text-xl font-bold flex">
          SkiWise{' '}
          <img
            src="/whiteSnowFlake.png"
            alt="SkiWise Logo"
            className="h-6 px-1"
          />
        </Link>

        <div className="hidden md:flex space-x-6">
          <Link to="/" className="hover:text-gray-300">
            Home
          </Link>
          <Link to="/about" className="hover:text-gray-300">
            About
          </Link>
          <Link to="/contact" className="hover:text-gray-300">
            Contact
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
