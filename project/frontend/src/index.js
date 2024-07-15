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
import { highlightStyle, regularStyle, showNameLocationid } from "./utils/maps";
import "./plugins/leaflet-mask"
import geoJsonPath from "../../data/NYCTaxiZones.geojson";

// Check if the host env variable exists else default to local host
const serverHost = process.env.APP_SERVER_HOST || "http://127.0.0.1:8534";


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

// Load shapefile data. Use it to clip and shade the map
// const geoJsonPath = "../../data/NYCTaxiZones.geojson";
// console.log(geoJsonPath)
L.mask(geoJsonPath, {
    interactive: true, 
    fitBounds: true,
    restrictBounds: true,
    fillOpacity:0.3,
    fillColor:"#3b3b38",
    weight: 0.5,
    color: "black",
}).addTo(map);

const nycTaxiZoneLayer = new L.GeoJSON.AJAX(geoJsonPath, {
    style: regularStyle,
    onEachFeature: showNameLocationid
});

nycTaxiZoneLayer.addTo(map);
let markerList = []; // List of active markers
let routesList = []; // List of plotted routes

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

    async function predictCollisions(mkrCoords) {
        try {
            let response = await fetch(`${serverHost}/predict_collisions`, {
                method: "POST",
                body: JSON.stringify({
                    "coords": mkrCoords,
                }),
                headers: {
                    "Content-Type": "application/json"
                }
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            } else {
                let jsonResponse = await response.json();
                let routeGeoJSON = jsonResponse.route;
                let predIncidents = jsonResponse.incidents;
                let anmlyBoroughs = jsonResponse.boroughs;

                console.log(predIncidents,anmlyBoroughs)

                routesList.forEach(route => map.removeLayer(route));

                // Plot the route on the map
                let routeLayer = L.geoJSON(routeGeoJSON).addTo(map);
                routesList.push(routeLayer);

                nycTaxiZoneLayer.eachLayer(function (layer) {
                    if (anmlyBoroughs.includes(layer.feature.properties.zone)) {
                        layer.setStyle(highlightStyle(layer.feature));
                    } else {
                        layer.setStyle(regularStyle(layer.feature));
                    }
                });

                addressForm.reset();
            }
            
        } catch (error) {
            console.error("There was a problem with the fetch operation:", error);
        }};

    addressForm.addEventListener("submit", (event) => {
        event.preventDefault();

        let formInputs = document.querySelectorAll(".address-form-input");
        let locationMarkers = {}
        formInputs.forEach( function(el) {
            locationMarkers[el.id] = {"lng":el.dataset.x,"lat":el.dataset.y};
        });

        nycTaxiZoneLayer.eachLayer(function (layer) {
            layer.setStyle(regularStyle(layer.feature));
        });

        predictCollisions(locationMarkers);
    });
}

function renderPage(pages) {
    if (!body) return;
    body.appendChild(pages);
    dynamicEventListeners();
};

renderPage(createJourneyForm());