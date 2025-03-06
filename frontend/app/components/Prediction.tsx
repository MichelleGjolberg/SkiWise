import React, { useState } from 'react';
import ResortCard from './ResortCard';
import ResortMap from './ResortMap';

{
  /*TODO: A function that gets the predicted mountains, this is hardcoded*/
}

const getPredictedMountains = () => {
  return [
    {
      place: 'Copper Mountain',
      distance: 40,
      icon: '/resorticons/copper_logo.png',
      iconAlt: 'Copper logo',
      lat: 39.47911297352002,
      long: -106.16137643069165,
    },
    {
      place: 'A-Basin',
      distance: 41,
      icon: '/resorticons/Arapahoe-Basin_logo.png',
      iconAlt: 'A-Basin logo',
      lat: 39.634443603707005,
      long: -105.87133882070331,
    },
    {
      place: 'Winter Park',
      distance: 45,
      icon: '/resorticons/winter_park_logo.png',
      iconAlt: 'Winter Park logo',
      lat: 39.88741388659955,
      long: -105.75996471022926,
    },
    {
      place: 'Copper Mountain',
      distance: 40,
      icon: '/resorticons/copper_logo.png',
      iconAlt: 'Copper logo',
      lat: 39.47911297352002,
      long: -106.16137643069165,
    },
    {
      place: 'A-Basin',
      distance: 41,
      icon: '/resorticons/Arapahoe-Basin_logo.png',
      iconAlt: 'A-Basin logo',
      lat: 39.634443603707005,
      long: -105.87133882070331,
    },
    {
      place: 'Winter Park',
      distance: 45,
      icon: '/resorticons/winter_park_logo.png',
      iconAlt: 'Winter Park logo',
      lat: 39.88741388659955,
      long: -105.75996471022926,
    },
  ];
};

const Prediction: React.FC = () => {
  const mountains = getPredictedMountains();

  const [selectedMountain, setSelectedMountain] = useState({
    lat: 39.4791,
    long: -106.1614,
  });

  return (
    <div className="flex flex-row">
      <ResortMap lat={selectedMountain.lat} long={selectedMountain.long} />
      <div className="flex flex-col overflow-y-auto max-h-[500px] w-80 p-2 border-l border-gray-300">
        {mountains.map((mountain, index) => (
          <div
            key={index}
            onClick={() =>
              setSelectedMountain({ lat: mountain.lat, long: mountain.long })
            }
            className="cursor-pointer"
          >
            <ResortCard
              place={mountain.place}
              distance={mountain.distance}
              icon={mountain.icon}
              iconAlt={mountain.iconAlt}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Prediction;
