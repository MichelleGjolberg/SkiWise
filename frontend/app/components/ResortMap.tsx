import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css'; // Ensure Mapbox CSS is imported

type ResortMapProps = {
  long: number;
  lat: number;
};

const MAPBOX_TOKEN =
  'pk.eyJ1IjoibWlnajgzMDciLCJhIjoiY202c2xpd3BnMDh5dzJsb2o3bzFseHpxeSJ9.D6qgWbOTK4KegIH5R-I7Cw';

const ResortMap: React.FC<ResortMapProps> = ({ long, lat }) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [long, lat],
      zoom: 12,
    });

    map.on('load', () => {
      new mapboxgl.Marker({ anchor: 'center' })
        .setLngLat([long, lat])
        .addTo(map);

      map.resize();
    });

    mapRef.current = map;

    return () => map.remove();
  }, [long, lat]);

  return (
    <div className="relative w-[600px] h-[500px] ">
      <div className="absolute inset-0 w-full h-full" ref={mapContainerRef} />
    </div>
  );
};

export default ResortMap;
