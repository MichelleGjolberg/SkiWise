import React from 'react';

type ResortCardProps = {
  place: string;
  icon: string;
  iconAlt: string;
  snow?: number;
};

const ResortCardDefault: React.FC<ResortCardProps> = ({
  place,
  icon,
  iconAlt,
  snow,
}) => {
  return (
    <>
      <div className="w-100 h-32 flex flex-row items-center mx-4 mb-4 border-2 bg-slate-100 border-slate-300 rounded-lg">
        <img src={icon} alt={iconAlt} className="h-20 px-1 pl-2" />
        <div className="flex flex-col justify-center pl-4">
          <p className="font-bold"> {place}</p>
          <div className="flex flex-row">
            <img
              src="/snow.png"
              alt="Snow flake"
              className="h-5 w-fit px-1 pt-1"
            />
            <p>{snow}" last 24h</p>
          </div>
        </div>
      </div>
    </>
  );
};

export default ResortCardDefault;
