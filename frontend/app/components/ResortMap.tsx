import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import polyline from '@mapbox/polyline';

type ResortMapProps = {
  startPoint: { lat: number; lng: number };
  endPoint: { lat: number; lng: number };
  encodedPolyline: string;
};

const MAPBOX_TOKEN = (mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN);

const ResortMap: React.FC<ResortMapProps> = ({
  startPoint,
  endPoint,
  encodedPolyline,
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [startPoint.lng, startPoint.lat],
      zoom: 12,
    });

    map.on('load', () => {
      const decodedCoords = polyline
        .decode(encodedPolyline)
        .map(([lat, lng]) => [lng, lat]);

      map.addSource('route', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: decodedCoords,
          },
          properties: {},
        },
      });

      map.addLayer({
        id: 'route',
        type: 'line',
        source: 'route',
        layout: {
          'line-join': 'round',
          'line-cap': 'round',
        },
        paint: {
          'line-color': '#0084e3',
          'line-width': 3,
        },
      });

      new mapboxgl.Marker({ color: '#739feb' })
        .setLngLat([startPoint.lng, startPoint.lat])
        .setPopup(new mapboxgl.Popup().setText('Start'))
        .addTo(map);

      new mapboxgl.Marker({ color: '#739feb' })
        .setLngLat([endPoint.lng, endPoint.lat])
        .setPopup(new mapboxgl.Popup().setText('End'))
        .addTo(map);

      map.fitBounds(
        decodedCoords.reduce(
          (bounds, coord) => bounds.extend(coord),
          new mapboxgl.LngLatBounds(decodedCoords[0], decodedCoords[0])
        ),
        { padding: 30 }
      );
    });

    mapRef.current = map;
    return () => map.remove();
  }, [startPoint, endPoint, encodedPolyline]);

  return (
    <div className="relative w-[500px] h-[500px]">
      <div className="absolute inset-0 w-full h-full" ref={mapContainerRef} />
    </div>
  );
};

export default ResortMap;
