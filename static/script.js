document.getElementById('valuation-form').addEventListener('submit', async function(event) {
    // 1. Prevent the page from reloading
    event.preventDefault();

    // 2. Grab the UI elements we need to update
    const submitBtn = document.getElementById('submit-btn');
    const resultBox = document.getElementById('result-box');
    const errorBox = document.getElementById('error-box');
    
    // 3. Set the Loading State
    submitBtn.innerText = 'Calculating... ⏳';
    submitBtn.disabled = true;
    resultBox.classList.add('hidden');
    errorBox.classList.add('hidden');

    // 4. Gather all the data automatically using FormData
    const formData = new FormData(event.target);
    const houseData = Object.fromEntries(formData.entries());

    // Fix the checkboxes: If they are checked, send 1. If not, send 0.
    houseData.Has_Gym = formData.has('Has_Gym') ? 1 : 0;
    houseData.Has_Pool = formData.has('Has_Pool') ? 1 : 0;
    houseData.Has_BQ = formData.has('Has_BQ') ? 1 : 0;
    houseData.Has_Elevator = formData.has('Has_Elevator') ? 1 : 0;

    try {
        //Send the data to your Python Flask API
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(houseData)
        });

        const data = await response.json();

        // 6. Handle the Response
        if (data.success) {
            // Format the exact exact prediction nicely with commas and the Naira sign
            let formattedExactPrice = new Intl.NumberFormat('en-NG', { 
                style: 'currency', 
                currency: 'NGN' 
            }).format(data.exact_price);
            
            // Inject the data into your new HTML elements
            document.getElementById('exact-price').innerText = formattedExactPrice;
            document.getElementById('price-range').innerText = data.price_range;
            
            // Unhide the beautiful results box!
            resultBox.classList.remove('hidden');
        } else {
            // If Python throws an error (like "Location not found"), show it here
            errorBox.innerText = `❌ ${data.error}`;
            errorBox.classList.remove('hidden');
        }
    } catch (error) {
        // Fallback for major network crashes
        console.error("Error:", error);
        errorBox.innerText = "❌ Failed to connect to the AI server. Please make sure your Flask app is running.";
        errorBox.classList.remove('hidden');
    } finally {
        // 7. Reset the button back to normal no matter what happened
        submitBtn.innerText = 'Calculate Market Value';
        submitBtn.disabled = false;
    }
});