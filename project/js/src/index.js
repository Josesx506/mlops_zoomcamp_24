import "@fortawesome/fontawesome-free/js/all";
import L from "leaflet";
import { GeoSearchControl, OpenStreetMapProvider } from "leaflet-geosearch";
import "leaflet-geosearch/assets/css/leaflet.css";
import "leaflet/dist/leaflet.css";
import "./css/main.css";
import { createJourneyForm } from "./utils/form";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// Configure default icon paths
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow
});

const body = document.getElementById("content");

let map = L.map("map", {
    center: [40.773782, -73.88031],
    zoom: 10});

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    subdomains: "abcd",
    attribution: "&copy; <a href='http://www.openstreetmap.org/copyright'>OpenStreetMap</a>"
}).addTo(map);

const provider = new OpenStreetMapProvider();

const startAddress = new GeoSearchControl({
    provider: provider,
    style: "bar",
    showMarker: true,
    showPopup: false,
    retainZoomLevel: false,
    animateZoom: true,
    keepResult: true,
    marker: {
      icon: new L.Icon.Default(),
      draggable: false,
    },
});

const endAddress = new GeoSearchControl({
    provider: provider,
    style: "bar",
    showMarker: true,
    showPopup: false,
    retainZoomLevel: false,
    animateZoom: true,
    keepResult: true,
    marker: {
      icon: new L.Icon.Default(),
      draggable: false,
    },
});

// console.log(startAddress.searchElement.form);
// console.log(map._marker);

// map.addControl(startAddress);
// map.addControl(endAddress);



function dynamicEventListeners() {
    const addressForm = document.querySelector("#new-address-entry-cntr");
    const startPoint = document.querySelector("#start-address");
    const startDropdown = document.querySelector("#start-address-dropdown");
    const endPoint = document.querySelector("#end-address");
    const endDropdown = document.querySelector("#end-address-dropdown");

    async function populateDropdown(event, dropdown) {
        const queryVal = event.target.value;
        if (queryVal.length < 3) return;
        const results = await provider.search({ query: queryVal });

        dropdown.innerHTML = "";

        // Populate dropdown with results
        results.forEach((result, index) => {
            const item = document.createElement("div");
            item.classList.add("address-search-result")
            item.textContent = result.label;
            item.dataset.index = index;
            item.dataset.x = result.x;
            item.dataset.y = result.y;
            dropdown.appendChild(item);
        });

        dropdown.style.display = "grid";
    };

    function selectFormAddress(event) {
        const target = event.target;
        const result = target.dataset;
        const index = result.index;

        const closestDropdown = target.parentNode;
        const closestInput = closestDropdown.parentNode.children[1];

        if (index !== undefined) {
            // Update the input value with the selected address
            closestInput.value = event.target.textContent;
            closestInput.dataset.x = result.x;
            closestInput.dataset.y = result.y;

            const marker = L.marker([result.y, result.x]).addTo(map);
            
            // Remove the other search results
            closestDropdown.style.display = "none";
            closestDropdown.innerHTML = "";
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

    
    // Hide the dropdown when clicking outside of it
    document.addEventListener("click", (event) => {
        if (!startPoint.contains(event.target) && !startDropdown.contains(event.target)) {
            startDropdown.style.display = "none";
        }
        if (!endPoint.contains(event.target) && !endDropdown.contains(event.target)) {
            endDropdown.style.display = "none";
        }
    });
    // startAddress.addTo(startPoint);
    
    // addressForm.addEventListener("submit", async (event) => {
    //     event.preventDefault();
    //     const results = await provider.search({ query: startPoint.value });
    //     console.log(results); // » [{}, {}, {}, ...]
    // });
}

function clearElement(element) {
    if (!element) return;
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    };
};

function renderPage(pages) {
    if (!body) return;
    body.appendChild(pages);
    dynamicEventListeners();
};

renderPage(createJourneyForm());