import folium
import matplotlib.pyplot as plt
import json
from models.database import db
from config import Config

class VisualizationService:
    def __init__(self):
        self.mapbox_enabled = Config.validate_mapbox_config()

    def create_mapbox_map(self, flight_id: str, path: list, output_dir: str = '.') -> dict:
        """Create interactive Mapbox map for flight path"""
        if not self.mapbox_enabled:
            return self.plot_flight_path(flight_id, output_dir)  # Fallback to OpenStreetMap
        
        try:
            # Extract coordinates and create GeoJSON
            coordinates = [
                [point['longitude'], point['latitude'], point['altitude']] 
                for point in path
            ]
            
            # Create GeoJSON for flight path
            geojson_path = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coordinates
                        },
                        "properties": {
                            "flight_id": flight_id,
                            "stroke": "#3388ff",
                            "stroke-width": 4,
                            "stroke-opacity": 0.8
                        }
                    }
                ]
            }
            
            # Create HTML with Mapbox GL JS
            html_content = self._generate_mapbox_html(flight_id, geojson_path, coordinates)
            
            # Save HTML file
            map_filename = f'{output_dir}/flight_{flight_id}_mapbox.html'
            with open(map_filename, 'w') as f:
                f.write(html_content)
            
            return {
                'map_file': map_filename,
                'map_type': 'mapbox',
                'message': f'Mapbox visualization generated for flight {flight_id}'
            }
            
        except Exception as e:
            print(f"Mapbox generation failed: {e}. Falling back to OpenStreetMap.")
            return self.plot_flight_path(flight_id, output_dir)
    
    def _generate_mapbox_html(self, flight_id: str, geojson_path: dict, coordinates: list) -> str:
        """Generate HTML content with Mapbox GL JS"""
        
        # Calculate bounds for map fitting
        lons = [coord[0] for coord in coordinates]
        lats = [coord[1] for coord in coordinates]
        bounds = [
            [min(lons), min(lats)],  # Southwest
            [max(lons), max(lats)]   # Northeast
        ]
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Flight {flight_id} - Mapbox Visualization</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.js"></script>
            <link href="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css" rel="stylesheet">
            <style>
                body {{ margin: 0; padding: 0; }}
                #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
                .map-overlay {{
                    position: absolute;
                    left: 0;
                    padding: 10px;
                    background: rgba(255, 255, 255, 0.9);
                    margin: 10px;
                    border-radius: 5px;
                    font-family: Arial, sans-serif;
                }}
            </style>
        </head>
        <body>
            <div class="map-overlay">
                <h3>Flight {flight_id}</h3>
                <div id="flight-info">
                    <p>Total Points: {len(coordinates)}</p>
                    <p>Altitude Range: {min([c[2] for c in coordinates])} - {max([c[2] for c in coordinates])} ft</p>
                </div>
            </div>
            <div id="map"></div>
            
            <script>
                // Set your Mapbox access token
                mapboxgl.accessToken = '{Config.MAPBOX_ACCESS_TOKEN}';
                
                // Initialize map
                const map = new mapboxgl.Map({{
                    container: 'map',
                    style: '{Config.MAPBOX_STYLE}',
                    center: [{coordinates[0][0]}, {coordinates[0][1]}],
                    zoom: 6,
                    pitch: 45,  // Tilt for 3D effect
                    bearing: 0
                }});
                
                // Flight path data
                const flightPath = {json.dumps(geojson_path)};
                
                map.on('load', () => {{
                    // Add flight path source and layer
                    map.addSource('flight-path', {{
                        'type': 'geojson',
                        'data': flightPath
                    }});
                    
                    map.addLayer({{
                        'id': 'flight-path',
                        'type': 'line',
                        'source': 'flight-path',
                        'layout': {{
                            'line-join': 'round',
                            'line-cap': 'round'
                        }},
                        'paint': {{
                            'line-color': '#3388ff',
                            'line-width': 4,
                            'line-opacity': 0.8
                        }}
                    }});
                    
                    // Add 3D terrain (optional)
                    map.addSource('mapbox-dem', {{
                        'type': 'raster-dem',
                        'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
                        'tileSize': 512,
                        'maxzoom': 14
                    }});
                    
                    map.setTerrain({{ 'source': 'mapbox-dem', 'exaggeration': 1.5 }});
                    
                    // Fit map to flight path bounds
                    map.fitBounds({json.dumps(bounds)}, {{
                        padding: 50,
                        duration: 2000
                    }});
                    
                    // Add flight animation (optional)
                    animateFlight();
                }});
                
                function animateFlight() {{
                    // Simple animation example - you can enhance this
                    const path = flightPath.features[0].geometry.coordinates;
                    let currentIndex = 0;
                    
                    function addNextPoint() {{
                        if (currentIndex < path.length) {{
                            const coord = path[currentIndex];
                            
                            // Create a marker for current position
                            new mapboxgl.Marker({{ color: '#ff0000' }})
                                .setLngLat([coord[0], coord[1]])
                                .addTo(map);
                            
                            currentIndex++;
                            setTimeout(addNextPoint, 100); // Adjust speed as needed
                        }}
                    }}
                    
                    // Start animation after a delay
                    setTimeout(addNextPoint, 2000);
                }}
            </script>
        </body>
        </html>
        """
        return html_template
    
    def plot_flight_path(self, flight_id: str, output_dir: str = '.') -> dict:
        """Plot flight path on map (OpenStreetMap fallback)"""
        flight_log = db.flight_logs.find_one({'flight_id': flight_id})
        if not flight_log:
            raise ValueError(f"No flight log found for {flight_id}")
        
        path = flight_log['tracking_path']
        if not path:
            raise ValueError(f"No tracking data for {flight_id}")
        
        # Create map with OpenStreetMap as fallback
        start_lat = path[0]['latitude']
        start_lon = path[0]['longitude']
        
        flight_map = folium.Map(
            location=[start_lat, start_lon],
            zoom_start=Config.MAP_ZOOM_START,
            tiles=Config.DEFAULT_MAP_TILES
        )
        
        # Extract coordinates
        coordinates = [(point['latitude'], point['longitude']) for point in path]
        
        # Add flight path
        folium.PolyLine(
            coordinates,
            color='blue',
            weight=3,
            opacity=0.8,
            popup=f"Flight {flight_id}"
        ).add_to(flight_map)
        
        # Add markers
        folium.Marker(
            coordinates[0],
            popup=f"Start: {flight_log['origin']['code']}",
            icon=folium.Icon(color='green', icon='plane')
        ).add_to(flight_map)
        
        folium.Marker(
            coordinates[-1],
            popup=f"End: {flight_log['destination']['code']}",
            icon=folium.Icon(color='red', icon='plane')
        ).add_to(flight_map)
        
        # Save map
        map_filename = f'{output_dir}/flight_{flight_id}_path.html'
        flight_map.save(map_filename)
        
        # Create altitude profile
        self._create_altitude_profile(flight_id, path, output_dir)
        
        return {
            'map_file': map_filename,
            'map_type': 'openstreetmap',
            'message': f'Visualization files generated for flight {flight_id}'
        }
    
    def _create_altitude_profile(self, flight_id: str, path: list, output_dir: str):
        """Create altitude profile chart"""
        altitudes = [point['altitude'] for point in path]
        timestamps = [point['timestamp'] for point in path]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, altitudes, 'b-', linewidth=2)
        plt.title(f'Altitude Profile - Flight {flight_id}')
        plt.xlabel('Time')
        plt.ylabel('Altitude (feet)')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        alt_filename = f'{output_dir}/flight_{flight_id}_altitude.png'
        plt.savefig(alt_filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_real_time_map(self, flights_data: list) -> str:
        """Generate real-time map with multiple flights using Mapbox"""
        if not self.mapbox_enabled:
            return self._generate_fallback_realtime_map(flights_data)
        
        try:
            # Create GeoJSON for all flights
            features = []
            for flight in flights_data:
                if flight.get('current_position'):
                    pos = flight['current_position']
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [pos['longitude'], pos['latitude']]
                        },
                        "properties": {
                            "flight_id": flight['flight_id'],
                            "airline": flight.get('airline', 'Unknown'),
                            "altitude": pos.get('altitude', 0),
                            "heading": pos.get('heading', 0),
                            "speed": pos.get('speed', 0)
                        }
                    })
            
            geojson_data = {
                "type": "FeatureCollection",
                "features": features
            }
            
            return self._generate_realtime_mapbox_html(geojson_data)
            
        except Exception as e:
            print(f"Real-time Mapbox generation failed: {e}")
            return self._generate_fallback_realtime_map(flights_data)
    
    def _generate_realtime_mapbox_html(self, geojson_data: dict) -> str:
        """Generate HTML for real-time flight tracking with Mapbox"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Real-time Flight Tracking</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.js"></script>
            <link href="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css" rel="stylesheet">
            <style>
                body {{ margin: 0; padding: 0; }}
                #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
                .map-overlay {{
                    position: absolute;
                    right: 0;
                    padding: 10px;
                    background: rgba(255, 255, 255, 0.9);
                    margin: 10px;
                    border-radius: 5px;
                    font-family: Arial, sans-serif;
                    max-width: 300px;
                }}
                .flight-info {{
                    margin: 5px 0;
                    padding: 5px;
                    border-bottom: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="map-overlay">
                <h3>Active Flights</h3>
                <div id="flight-list">
                    <!-- Flight list will be populated by JavaScript -->
                </div>
            </div>
            <div id="map"></div>
            
            <script>
                mapboxgl.accessToken = '{Config.MAPBOX_ACCESS_TOKEN}';
                
                const map = new mapboxgl.Map({{
                    container: 'map',
                    style: '{Config.MAPBOX_STYLE}',
                    center: [0, 30],
                    zoom: 2
                }});
                
                const flightsData = {json.dumps(geojson_data)};
                
                map.on('load', () => {{
                    // Add flight positions source
                    map.addSource('flights', {{
                        'type': 'geojson',
                        'data': flightsData
                    }});
                    
                    // Add flight positions layer
                    map.addLayer({{
                        'id': 'flights',
                        'type': 'circle',
                        'source': 'flights',
                        'paint': {{
                            'circle-radius': 6,
                            'circle-color': '#ff0000',
                            'circle-stroke-width': 2,
                            'circle-stroke-color': '#ffffff'
                        }}
                    }});
                    
                    // Add flight labels
                    map.addLayer({{
                        'id': 'flight-labels',
                        'type': 'symbol',
                        'source': 'flights',
                        'layout': {{
                            'text-field': ['get', 'flight_id'],
                            'text-size': 12,
                            'text-offset': [0, 1.5]
                        }},
                        'paint': {{
                            'text-color': '#000000',
                            'text-halo-color': '#ffffff',
                            'text-halo-width': 2
                        }}
                    }});
                    
                    // Update flight list
                    updateFlightList();
                }});
                
                // Click event to show flight details
                map.on('click', 'flights', (e) => {{
                    const flight = e.features[0].properties;
                    new mapboxgl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(`
                            <h4>Flight ${{flight.flight_id}}</h4>
                            <p>Airline: ${{flight.airline}}</p>
                            <p>Altitude: ${{flight.altitude}} ft</p>
                            <p>Speed: ${{flight.speed}} kts</p>
                            <p>Heading: ${{flight.heading}}°</p>
                        `)
                        .addTo(map);
                }});
                
                function updateFlightList() {{
                    const flightList = document.getElementById('flight-list');
                    flightList.innerHTML = '';
                    
                    flightsData.features.forEach(flight => {{
                        const props = flight.properties;
                        const div = document.createElement('div');
                        div.className = 'flight-info';
                        div.innerHTML = `
                            <strong>${{props.flight_id}}</strong><br>
                            ${{props.airline}}<br>
                            Alt: ${{props.altitude}}ft | Spd: ${{props.speed}}kts
                        `;
                        flightList.appendChild(div);
                    }});
                }}
                
                // Auto-refresh every 30 seconds
                setInterval(() => {{
                    // In a real implementation, you'd fetch new data from your API
                    console.log('Refreshing flight data...');
                }}, 30000);
            </script>
        </body>
        </html>
        """
        return html_template
    
    def _generate_fallback_realtime_map(self, flights_data: list) -> str:
        """Generate fallback real-time map with OpenStreetMap"""
        # Center map based on flights or use default
        if flights_data and flights_data[0].get('current_position'):
            center_lat = flights_data[0]['current_position']['latitude']
            center_lon = flights_data[0]['current_position']['longitude']
        else:
            center_lat, center_lon = 0, 0
        
        realtime_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=3,
            tiles=Config.DEFAULT_MAP_TILES
        )
        
        # Add flight markers
        for flight in flights_data:
            if flight.get('current_position'):
                pos = flight['current_position']
                popup_text = f"""
                <b>Flight {flight['flight_id']}</b><br>
                Airline: {flight.get('airline', 'Unknown')}<br>
                Altitude: {pos.get('altitude', 0)} ft<br>
                Speed: {pos.get('speed', 0)} kts<br>
                Heading: {pos.get('heading', 0)}°
                """
                folium.Marker(
                    [pos['latitude'], pos['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='red', icon='plane', prefix='fa')
                ).add_to(realtime_map)
        
        # Convert to HTML string
        return realtime_map._repr_html_()