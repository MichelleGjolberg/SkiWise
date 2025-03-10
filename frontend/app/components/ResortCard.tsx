import React from 'react';

type ResortCardProps = {
  place: string;
  distance: number;
  icon: string;
  iconAlt: string;
};

const ResortCard: React.FC<ResortCardProps> = ({
  place,
  distance,
  icon,
  iconAlt,
}) => {
  return (
    <>
      <div className="w-[400px] h-32 flex flex-row items-center mx-4 mb-4 border-2 bg-slate-100 border-slate-300 rounded-lg">
        <img src={icon} alt={iconAlt} className="h-20 px-1 pl-2" />
        <div className="flex flex-col justify-center pl-4">
          <p className="font-bold"> {place}</p>
          <p> Distance: {distance.toString()} miles</p>
        </div>
      </div>
    </>
  );
};

export default ResortCard;
