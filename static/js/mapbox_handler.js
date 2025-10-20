// Frontend Mapbox handler for interactive flight tracking
class MapboxFlightTracker {
    constructor(containerId, mapboxToken, mapStyle = 'mapbox/streets-v11') {
        this.containerId = containerId;
        this.mapboxToken = mapboxToken;
        this.mapStyle = mapStyle;
        this.map = null;
        this.flights = new Map();
        this.markers = new Map();
        
        this.initMap();
    }
    
    initMap() {
        mapboxgl.accessToken = this.mapboxToken;
        
        this.map = new mapboxgl.Map({
            container: this.containerId,
            style: this.mapStyle,
            center: [0, 30],
            zoom: 2
        });
        
        this.map.on('load', () => {
            this.setupMapLayers();
            this.loadInitialFlights();
        });
    }
    
    setupMapLayers() {
        // Add terrain for 3D effect
        this.map.addSource('mapbox-dem', {
            'type': 'raster-dem',
            'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
            'tileSize': 512,
            'maxzoom': 14
        });
        
        this.map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });
        
        // Add sky layer for atmospheric effect
        this.map.addLayer({
            'id': 'sky',
            'type': 'sky',
            'paint': {
                'sky-type': 'atmosphere',
                'sky-atmosphere-sun': [0.0, 0.0],
                'sky-atmosphere-sun-intensity': 15
            }
        });
    }
    
    async loadInitialFlights() {
        try {
            const response = await fetch('/api/flights?status=active');
            const data = await response.json();
            this.updateFlights(data.flights);
        } catch (error) {
            console.error('Failed to load flights:', error);
        }
    }
    
    updateFlights(flightsData) {
        flightsData.forEach(flight => {
            this.addOrUpdateFlight(flight);
        });
    }
    
    addOrUpdateFlight(flight) {
        const flightId = flight.flight_id;
        
        if (!flight.current_position) return;
        
        const position = flight.current_position;
        const coordinates = [position.longitude, position.latitude];
        
        // Create or update flight marker
        if (this.markers.has(flightId)) {
            // Update existing marker position
            this.markers.get(flightId).setLngLat(coordinates);
        } else {
            // Create new marker with plane icon
            const markerElement = this.createPlaneMarker(position.heading);
            
            const marker = new mapboxgl.Marker({
                element: markerElement,
                rotationAlignment: 'map'
            })
                .setLngLat(coordinates)
                .setRotation(position.heading)
                .addTo(this.map);
            
            // Add popup
            const popup = new mapboxgl.Popup({ offset: 25 })
                .setHTML(this.createPopupContent(flight));
            
            marker.setPopup(popup);
            
            this.markers.set(flightId, marker);
        }
        
        // Store flight data
        this.flights.set(flightId, flight);
    }
    
    createPlaneMarker(heading = 0) {
        const element = document.createElement('div');
        element.className = 'plane-marker';
        element.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="red" stroke="white" stroke-width="2">
                <path d="M22 16v-2l-8.5-5V3.5c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5V9L2 14v2l8.5-2.5V19L8 20.5V22l4-1 4 1v-1.5L13.5 19v-5.5L22 16z"/>
            </svg>
        `;
        element.style.transform = `rotate(${heading}deg)`;
        return element;
    }
    
    createPopupContent(flight) {
        const pos = flight.current_position;
        return `
            <div class="flight-popup">
                <h4>${flight.flight_id}</h4>
                <p><strong>Airline:</strong> ${flight.airline || 'Unknown'}</p>
                <p><strong>From:</strong> ${flight.origin?.code || 'Unknown'} 
                   <strong>To:</strong> ${flight.destination?.code || 'Unknown'}</p>
                <p><strong>Altitude:</strong> ${pos.altitude} ft</p>
                <p><strong>Speed:</strong> ${pos.speed} kts</p>
                <p><strong>Heading:</strong> ${pos.heading}°</p>
                <button onclick="trackFlight('${flight.flight_id}')">Track Flight</button>
            </div>
        `;
    }
    
    removeFlight(flightId) {
        if (this.markers.has(flightId)) {
            this.markers.get(flightId).remove();
            this.markers.delete(flightId);
        }
        this.flights.delete(flightId);
    }
    
    // Animate flight path
    animateFlightPath(flightId, pathCoordinates, duration = 5000) {
        const marker = this.markers.get(flightId);
        if (!marker) return;
        
        const startTime = performance.now();
        const path = pathCoordinates.map(coord => [coord.longitude, coord.latitude]);
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentIndex = Math.floor(progress * (path.length - 1));
            const nextIndex = Math.min(currentIndex + 1, path.length - 1);
            
            if (currentIndex < path.length - 1) {
                const currentPos = path[currentIndex];
                const nextPos = path[nextIndex];
                
                // Interpolate position
                const segmentProgress = (progress * (path.length - 1)) - currentIndex;
                const interpolatedLng = currentPos[0] + (nextPos[0] - currentPos[0]) * segmentProgress;
                const interpolatedLat = currentPos[1] + (nextPos[1] - currentPos[1]) * segmentProgress;
                
                marker.setLngLat([interpolatedLng, interpolatedLat]);
                
                // Calculate and set heading
                const heading = this.calculateHeading(currentPos, nextPos);
                marker.setRotation(heading);
                
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    calculateHeading(pointA, pointB) {
        const [lng1, lat1] = pointA;
        const [lng2, lat2] = pointB;
        
        const y = Math.sin(lng2 - lng1) * Math.cos(lat2);
        const x = Math.cos(lat1) * Math.sin(lat2) -
                 Math.sin(lat1) * Math.cos(lat2) * Math.cos(lng2 - lng1);
        
        let heading = Math.atan2(y, x) * (180 / Math.PI);
        return (heading + 360) % 360;
    }
}

// Global function to track individual flight
function trackFlight(flightId) {
    // Implementation for tracking individual flight
    console.log(`Tracking flight: ${flightId}`);
    window.open(`/flight/${flightId}/map`, '_blank');
}