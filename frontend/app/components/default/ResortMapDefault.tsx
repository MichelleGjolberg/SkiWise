import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import polyline from '@mapbox/polyline';

type ResortMapProps = {
  startPoint: { lat: number; lng: number };
};

const MAPBOX_TOKEN = (mapboxgl.accessToken =
  import.meta.env.VITE_MAPBOX_ACCESS_TOKEN);

const ResortMap: React.FC<ResortMapProps> = ({ startPoint }) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: [startPoint.lng, startPoint.lat],
      zoom: 9,
    });

    map.on('load', () => {
      new mapboxgl.Marker({ color: '#739feb' })
        .setLngLat([startPoint.lng, startPoint.lat])
        .setPopup(new mapboxgl.Popup().setText('Start'))
        .addTo(map);
    });

    mapRef.current = map;
    return () => map.remove();
  }, [startPoint]);

  return (
    <div className="relative w-[300px] h-[300px] md:w-[500px] md:h-[500px] py-4">
      <div className="absolute inset-0 w-full h-full" ref={mapContainerRef} />
    </div>
  );
};

export default ResortMap;
