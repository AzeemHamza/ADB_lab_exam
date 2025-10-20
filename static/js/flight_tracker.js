// Initialize flight tracker when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (typeof MAPBOX_TOKEN !== 'undefined') {
        // Initialize Mapbox flight tracker
        const flightTracker = new MapboxFlightTracker('map', MAPBOX_TOKEN);
        
        // Refresh flights every 10 seconds
        setInterval(() => {
            flightTracker.loadInitialFlights();
        }, 10000);
        
        // Add event listeners for control buttons
        document.getElementById('refresh-btn').addEventListener('click', () => {
            flightTracker.loadInitialFlights();
        });
        
        document.getElementById('toggle-terrain').addEventListener('click', () => {
            // Toggle terrain implementation
            console.log('Toggle terrain feature');
        });
    } else {
        console.log('Mapbox not configured, using fallback mapping');
        // Implement fallback mapping here
    }
});

// Function to update flight count display
function updateFlightCount(count) {
    const flightCountElement = document.getElementById('flight-count');
    if (flightCountElement) {
        flightCountElement.textContent = `Active Flights: ${count}`;
    }
}