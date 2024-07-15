function regularStyle(feature) {
    return {
        color: "black",
        fillColor: "yellow",
        weight: 0.5,
        opacity: 0.9,
        fillOpacity: 0.05,
    };
};

function highlightStyle(feature) {
    return {
        color: "black",
        fillColor: "red",
        weight: 0.5,
        opacity: 0.9,
        fillOpacity: 0.5,
    };
};

function showNameLocationid(feature, layer) {
    layer.bindPopup(`Name: ${feature.properties.zone} ID: ${feature.properties.location_id}`);
};

export { highlightStyle, regularStyle, showNameLocationid };
