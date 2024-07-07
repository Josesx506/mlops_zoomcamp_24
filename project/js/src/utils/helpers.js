import { OpenStreetMapProvider } from "leaflet-geosearch";

const provider = new OpenStreetMapProvider();

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

export { populateDropdown };