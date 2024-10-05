const url = 'https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport?query=new&locale=en-US';
const options = {
    method: 'GET',
    headers: {
        'x-rapidapi-key': 'e249a3f4cbmsh4f1a4ad98e12a42p1dc226jsnee8181aac2e0',  // Replace with your actual API key
        'x-rapidapi-host': 'sky-scrapper.p.rapidapi.com'
    }
};

async function fetchAirportData() {
    const fetch = (await import('node-fetch')).default; // Dynamic import

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        console.log(JSON.stringify(data, null, 2)); // Pretty-print JSON data
    } catch (error) {
        console.error('Error fetching data:', error.message); // More concise error message
    }
}

fetchAirportData();

