import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';

const MAPBOX_TOKEN = (mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN);
const Map = () => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const [mapbox, setMapbox] = useState<any>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    import('mapbox-gl').then((mapboxModule) => {
      setMapbox(mapboxModule.default);
    });
  }, []);

  useEffect(() => {
    if (!mapbox || !mapContainerRef.current) return;

    mapbox.accessToken = MAPBOX_TOKEN;

    const map = new mapbox.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [-122.4194, 37.7749],
      zoom: 12,
    });

    return () => map.remove();
  }, [mapbox]);

  return <div className="w-full h-[500px]" ref={mapContainerRef} />;
};

export default Map;
