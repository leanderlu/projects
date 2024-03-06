function validateInput(event) {
    const value = event.target.value;
    const valid = /^-?\d*\.?\d*$/.test(value); // Regex to allow only numbers and floats
    if (!valid) {
        event.target.value = value.slice(0, -1); // Remove last character if invalid
    }
}

function predictSalary() {
    // Updated coefficients from your regression model
    const intercept = -42170000;
    const ageCoefficient = 1057000;
    const bWARCoefficient = 1243000;
    const drsCoefficient = -174000;
    const xwOBACoefficient = 51330000;

    // Fetch values from the form
    const age = document.getElementById('age').value;
    const bWAR = document.getElementById('bWAR').value;
    const drs = document.getElementById('drs').value;
    const xwOBA = document.getElementById('xwOBA').value;

    // Calculate the predicted salary
    let predictedSalary = intercept + (ageCoefficient * age) + (bWARCoefficient * bWAR)
        + (drsCoefficient * drs) + (xwOBACoefficient * xwOBA);

    // Round to the nearest whole number and format with commas
    let formattedSalary = Math.round(predictedSalary).toLocaleString();

    // Update the UI with the formatted predicted salary
    document.getElementById('predictedSalary').innerText = formattedSalary;
}
