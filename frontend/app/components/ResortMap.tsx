import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import polyline from '@mapbox/polyline';

type ResortMapProps = {
  startPoint: any[];
  endPoint: { lat: number; lng: number };
  encodedPolyline: string;
};

const MAPBOX_TOKEN = (mapboxgl.accessToken =
  import.meta.env.VITE_MAPBOX_ACCESS_TOKEN);

const ResortMap: React.FC<ResortMapProps> = ({
  startPoint,
  endPoint,
  encodedPolyline,
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const start = startPoint ? startPoint : [40.0189728, -105.2747406];

  useEffect(() => {
    if (!mapContainerRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: [start[1], start[0]],
      zoom: 9,
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
        .setLngLat([start[1], start[0]])
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
