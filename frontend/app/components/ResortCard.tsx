import React from 'react';

type ResortCardProps = {
  place: string;
  distance: number;
};

const ResortCard: React.FC<ResortCardProps> = ({ place, distance }) => {
  return (
    <>
      <div className="w-[300px] h-24 flex flex-row items-center mx-4 mb-4 border-2 border-sky-300 rounded-lg">
        <img
          src="/resorticons/copper_logo.png"
          alt="SkiWise Logo"
          className="h-20 px-1"
        />
        <div className="flex flex-col justify-center pl-4">
          <p className="font-bold"> {place}</p>
          <p> Distance: {distance.toString()} miles</p>
        </div>
      </div>
    </>
  );
};

export default ResortCard;
