import "@fortawesome/fontawesome-free/js/all";
import L from "leaflet";
import "leaflet-ajax";
import "leaflet-geosearch/assets/css/leaflet.css";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import "leaflet/dist/leaflet.css";
import "./css/main.css";
import { createJourneyForm } from "./utils/form";
import { populateDropdown } from "./utils/helpers";

// Configure default icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow
});

const body = document.getElementById("content");

let map = L.map("map", {
    center: [40.723782, -73.98031],
    zoom: 10});

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    subdomains: "abcd",
    attribution: "&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>"
}).addTo(map);

// Load shapefile data
const nycTaxiZoneLayer = new L.GeoJSON.AJAX("../../data/NYCTaxiZones.geojson", {
    style: function (feature) {
        return {
            color: "black",
            fillColor: "yellow",
            weight: 0.5,
            opacity: 0.9,
            fillOpacity: 0.05,
        };
    },
    onEachFeature: function (feature, layer) {
        layer.bindPopup(`Name: ${feature.properties.zone} ID: ${feature.properties.location_id}`);
    }
});  
nycTaxiZoneLayer.addTo(map);
let markerList = []; // List of active markers

function dynamicEventListeners() {
    const addressForm = document.querySelector("#new-address-entry-cntr");
    const startPoint = document.querySelector("#start-address");
    const startDropdown = document.querySelector("#start-address-dropdown");
    const endPoint = document.querySelector("#end-address");
    const endDropdown = document.querySelector("#end-address-dropdown");


    function checkMarkers() {
        const startX = parseFloat(startPoint.dataset.x);
        const startY = parseFloat(startPoint.dataset.y);
        const endX = parseFloat(endPoint.dataset.x);
        const endY = parseFloat(endPoint.dataset.y);

        markerList = markerList.filter(marker => {
            const { lat, lng } = marker.getLatLng();
            if ((lat === startY && lng === startX) || (lat === endY && lng === endX)) {
                return true;
            } else {
                map.removeLayer(marker); // Remove marker from map
                return false;
            }
        });
    };

    function selectFormAddress(event) {
        const target = event.target;
        const result = target.dataset;
        const index = result.index;

        const closestDropdown = target.parentNode;
        const closestInput = closestDropdown.parentNode.children[0];

        if (index !== undefined) {
            // Update the input value with the selected address
            closestInput.value = event.target.textContent;
            closestInput.dataset.x = result.x;
            closestInput.dataset.y = result.y;
            
            const marker = L.marker([result.y, result.x]).addTo(map);
            console.log(closestInput.name);
            marker.bindPopup(closestInput.name)
            markerList.push(marker);
            
            // Remove the other search results
            closestDropdown.style.display = "none";
            closestDropdown.innerHTML = "";

            checkMarkers();
        }
    };

    startPoint.addEventListener("input", (e) => {
        e.preventDefault();
        populateDropdown(e, startDropdown)
    });

    startDropdown.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        selectFormAddress(e);
    });

    endPoint.addEventListener("input", (e) => {
        e.preventDefault();
        populateDropdown(e, endDropdown)
    });

    endDropdown.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        selectFormAddress(e);
    });

    
    // Hide the dropdowns when clicking the rest of the screen
    document.addEventListener("click", (event) => {
        if (!startPoint.contains(event.target) && !startDropdown.contains(event.target)) {
            startDropdown.style.display = "none";
        }
        if (!endPoint.contains(event.target) && !endDropdown.contains(event.target)) {
            endDropdown.style.display = "none";
        }
    });
}

// function clearElement(element) {
//     if (!element) return;
//     while (element.firstChild) {
//         element.removeChild(element.firstChild);
//     };
// };

function renderPage(pages) {
    if (!body) return;
    body.appendChild(pages);
    dynamicEventListeners();
};

renderPage(createJourneyForm());