// static/js/location-picker.js

class LocationPicker {
    constructor(options = {}) {
        this.mapId = options.mapId || 'locationMap';
        this.inputLatId = options.inputLatId || 'latitude';
        this.inputLngId = options.inputLngId || 'longitude';
        this.inputAddressId = options.inputAddressId || 'address';
        this.defaultLat = options.defaultLat || 24.7136; // Riyadh
        this.defaultLng = options.defaultLng || 46.6753;
        this.zoom = options.zoom || 10;
        this.searchable = options.searchable !== false;
        
        this.map = null;
        this.marker = null;
        
        this.init();
    }
    
    init() {
        this.createMap();
        this.addSearchControl();
        this.addClickHandler();
        this.loadSavedLocation();
    }
    
    createMap() {
        this.map = L.map(this.mapId).setView([this.defaultLat, this.defaultLng], this.zoom);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Add locate control
        const locateControl = L.control({position: 'topright'});
        locateControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
            div.innerHTML = `
                <a href="#" title="تحديد موقعي الحالي" onclick="locationPicker.getCurrentLocation(); return false;">
                    <i class="fas fa-location-arrow"></i>
                </a>
            `;
            return div;
        };
        locateControl.addTo(this.map);
    }
    
    addSearchControl() {
        if (!this.searchable) return;
        
        const searchControl = L.control({position: 'topleft'});
        searchControl.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-control-search');
            div.innerHTML = `
                <div class="search-container">
                    <input type="text" id="locationSearch" placeholder="ابحث عن موقع..." 
                           class="form-control form-control-sm">
                    <div id="searchResults" class="search-results"></div>
                </div>
            `;
            return div;
        };
        searchControl.addTo(this.map);
        
        // Add search functionality
        document.getElementById('locationSearch').addEventListener('input', (e) => {
            this.searchLocation(e.target.value);
        });
    }
    
    addClickHandler() {
        this.map.on('click', (e) => {
            this.setLocation(e.latlng.lat, e.latlng.lng);
            this.reverseGeocode(e.latlng.lat, e.latlng.lng);
        });
    }
    
    setLocation(lat, lng, address = '') {
        // Remove existing marker
        if (this.marker) {
            this.map.removeLayer(this.marker);
        }
        
        // Add new marker
        this.marker = L.marker([lat, lng], {
            draggable: true
        }).addTo(this.map);
        
        // Handle marker drag
        this.marker.on('dragend', (e) => {
            const position = e.target.getLatLng();
            this.setLocation(position.lat, position.lng);
            this.reverseGeocode(position.lat, position.lng);
        });
        
        // Update inputs
        document.getElementById(this.inputLatId).value = lat.toFixed(6);
        document.getElementById(this.inputLngId).value = lng.toFixed(6);
        
        if (address) {
            document.getElementById(this.inputAddressId).value = address;
        }
        
        // Center map
        this.map.setView([lat, lng], 15);
    }
    
    getCurrentLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    this.setLocation(lat, lng);
                    this.reverseGeocode(lat, lng);
                },
                (error) => {
                    alert('لا يمكن تحديد موقعك الحالي');
                }
            );
        } else {
            alert('المتصفح لا يدعم تحديد الموقع');
        }
    }
    
    searchLocation(query) {
        if (query.length < 3) {
            document.getElementById('searchResults').innerHTML = '';
            return;
        }
        
        // Use Nominatim for geocoding
        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=sa&limit=5`)
            .then(response => response.json())
            .then(data => {
                this.displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
            });
    }
    
    displaySearchResults(results) {
        const resultsContainer = document.getElementById('searchResults');
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="search-result">لا توجد نتائج</div>';
            return;
        }
        
        const html = results.map(result => `
            <div class="search-result" onclick="locationPicker.selectSearchResult(${result.lat}, ${result.lon}, '${result.display_name}')">
                <i class="fas fa-map-marker-alt"></i> ${result.display_name}
            </div>
        `).join('');
        
        resultsContainer.innerHTML = html;
    }
    
    selectSearchResult(lat, lng, address) {
        this.setLocation(lat, lng, address);
        document.getElementById('searchResults').innerHTML = '';
        document.getElementById('locationSearch').value = '';
    }
    
    reverseGeocode(lat, lng) {
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
            .then(response => response.json())
            .then(data => {
                if (data.display_name) {
                    document.getElementById(this.inputAddressId).value = data.display_name;
                }
            })
            .catch(error => {
                console.error('Reverse geocoding error:', error);
            });
    }
    
    loadSavedLocation() {
        const lat = document.getElementById(this.inputLatId).value;
        const lng = document.getElementById(this.inputLngId).value;
        
        if (lat && lng) {
            this.setLocation(parseFloat(lat), parseFloat(lng));
        }
    }
    
    // Public methods
    getLocation() {
        return {
            lat: parseFloat(document.getElementById(this.inputLatId).value),
            lng: parseFloat(document.getElementById(this.inputLngId).value),
            address: document.getElementById(this.inputAddressId).value
        };
    }
    
    clearLocation() {
        if (this.marker) {
            this.map.removeLayer(this.marker);
            this.marker = null;
        }
        
        document.getElementById(this.inputLatId).value = '';
        document.getElementById(this.inputLngId).value = '';
        document.getElementById(this.inputAddressId).value = '';
    }
}

// CSS for location picker
const locationPickerCSS = `
.leaflet-control-search {
    background: white;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    padding: 5px;
}

.search-container {
    position: relative;
    width: 250px;
}

.search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-top: none;
    border-radius: 0 0 5px 5px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 1000;
}

.search-result {
    padding: 8px 12px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
}

.search-result:hover {
    background-color: #f8f9fa;
}

.search-result:last-child {
    border-bottom: none;
}

.search-result i {
    color: #007bff;
    margin-left: 5px;
}

#locationMap {
    height: 400px;
    border-radius: 8px;
    border: 1px solid #ddd;
}
`;

// Add CSS to page
const style = document.createElement('style');
style.textContent = locationPickerCSS;
document.head.appendChild(style);

