
const fetch = require('node-fetch');

async function getSkyId(location) {
    return location; 
}

async function fetchFlightData(userResponses) {
    const { start_location, end_location, start_date, end_date, cabin_class, adult_count, child_count, infant_count, preference } = userResponses.flight_booking;

    const originSkyId = await getSkyId(start_location);
    const destinationSkyId = await getSkyId(end_location);

    let url = `https://sky-scrapper.p.rapidapi.com/api/v2/flights/searchFlightsComplete?originSkyId=${originSkyId}&destinationSkyId=${destinationSkyId}&originEntityId=${start_location}&destinationEntityId=${end_location}&date=${start_date}&returnDate=${end_date}&cabinClass=${cabin_class}&adults=${adult_count}&childrens=${child_count}&infants=${infant_count}&sortBy=${preference === "NULL" ? "" : preference}&currency=USD&market=en-US&countryCode=US`;

    const options = {
        method: 'GET',
        headers: {
            'x-rapidapi-key': 'YOUR_API_KEY_HERE',
            'x-rapidapi-host': 'sky-scrapper.p.rapidapi.com'
        }
    };

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! Status: ${response.status}, Message: ${errorText}`);
        }

        const result = await response.json();
        if (result.status) {
            console.log(JSON.stringify(result.data.itineraries, null, 2));
        } else {
            console.error("Error fetching data:", result.message);
        }
    } catch (error) {
        console.error("Error:", error.message);
    }
}

const userResponses = JSON.parse(process.argv[2]);
fetchFlightData(userResponses);
