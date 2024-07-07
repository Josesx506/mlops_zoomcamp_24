import "../css/main.css"

function createInputFormDivs(divClass,inputId,labelText,maxlen=null) {
    const element = document.createElement("div");
    element.classList.add(divClass);

    const inputDivInput = document.createElement("input");
    inputDivInput.classList.add("address-form-input");
    inputDivInput.id = inputId;
    inputDivInput.required = true;
    inputDivInput.setAttribute("type","text");
    inputDivInput.setAttribute("name",inputId);
    inputDivInput.setAttribute("placeholder",labelText);
    inputDivInput.setAttribute("autocomplete","off");

    const inputDivDropdown = document.createElement("div");
    inputDivDropdown.id = `${inputId}-dropdown`;
    inputDivDropdown.classList.add("address-dropdown-cntr");
    
    element.appendChild(inputDivInput);
    element.appendChild(inputDivDropdown);

    return element;
};

function createJourneyForm() {
    const element = document.createElement("form");
    element.id = "new-address-entry-cntr";
    element.classList.add("modal-body");

    const startDiv = createInputFormDivs("address-location-input","start-address","Choose Starting Address");
    const endDiv = createInputFormDivs("address-location-input","end-address","Choose Ending Address");
    const submit = document.createElement("input");
    submit.id = "address-form-submit";
    submit.classList.add("clickable-btn");
    submit.setAttribute("type","submit");
    submit.value = "Check Route";

    element.appendChild(startDiv);
    element.appendChild(endDiv);
    element.appendChild(submit);

    return element;
};


export {createJourneyForm};