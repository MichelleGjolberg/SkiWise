import type { MetaFunction } from '@remix-run/node';
import UserInput from '~/components/UserInput';
import NavBar from '~/components/NavBar';
import { useState, useRef } from 'react';
import Footer from '~/components/Footer';

//This is the main page (all .tsx files under routes are singular pages)
export const meta: MetaFunction = () => {
  return [
    { title: 'SkiWise' },
    { name: 'description', content: 'Find your mountain' },
  ];
};

export default function Index() {
  const [showContent, setShowContent] = useState(false);
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleClick = () => {
    setShowContent(true);
    setIsButtonDisabled(true);

    setTimeout(() => {
      contentRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div
        className="relative h-screen w-full bg-fixed bg-cover bg-top overflow-hidden shadow-lg z-0"
        style={{ backgroundImage: "url('/mountain_range.avif')" }}
      >
        <div className="flex flex-col items-center justify-center h-1/3 ">
          <NavBar />
          <button
            className={`w-1/3 h-[100px] rounded-lg bg-white transition-transform duration-300 transform ${
              isButtonDisabled ? 'cursor-not-allowed' : 'hover:scale-105'
            }`}
            onClick={handleClick}
            disabled={isButtonDisabled} // Disable after first click
          >
            <h1 className="text-2xl font-bold text-gray-600 flex justify-center items-center text-center h-100">
              Welcome to Skiwise - Find your mountain
            </h1>
            {!showContent && (
              <p className="text-md  text-gray-400 flex justify-center items-center text-center ">
                Click here
              </p>
            )}
          </button>
        </div>
      </div>

      <div className="flex-grow z-10" ref={contentRef}>
        {showContent && <UserInput />}
      </div>
      <Footer />
    </div>
  );
}
