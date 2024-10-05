from flask import Flask, render_template, request, jsonify, session
import secrets
import subprocess
import json
app = Flask(__name__)  # Corrected __name__

import secrets
import requests

# Generate a random 16-byte hex string
secret_key = secrets.token_hex(16)
app.secret_key = secret_key
grouped_data = {}
# Dictionary to store user responses
user_responses = {'flight_booking':{}
                    }

current_question_index=0

question_key_mapping = ['message',
                        'start_location',
                        'end_location',
                        'start_date',
                        'end_date',
                        'cabin_class',
                        'adult_count',
                        'child_count',
                        'infant_count',
                        'preference'
                    ]
def save_response(category, question_index, value):
    """Save user's response to a nested dictionary."""
    # Check if the category exists (in this case 'flight_booking'), if not, return an error.
    if category not in user_responses:
        return "Invalid category!"
    
    # Get the corresponding key for the current question index
    if question_index < len(question_key_mapping):
        key = question_key_mapping[question_index]
        user_responses[category][key] = value
        return f"{key} updated with value: {value}"
    else:
        return "Invalid question index!"

# Main chatbot logic for different options
def travel_assistant(user_choice, user_input=None):
    # Respond based on the user's choice
    if user_choice == '1':
        return flight_booking_flow(user_input)
    elif user_choice == '2':
        return hotel_booking_flow(user_input)
    elif user_choice == '3':
        return trip_planning_flow(user_input)
    elif user_choice == '4':
        return weather_enquiry_flow(user_input)
    else:
        return "Invalid option. Please try again."

import subprocess
import json

def fetch_flight_options(user_responses):
    try:
        # Create the JS file
        js_code = """
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
"""

        with open('fetch_flights.js', 'w') as f:
            f.write(js_code)

        # Call the JavaScript file
        result = subprocess.run(['node', 'fetch_flights.js', json.dumps(user_responses)], capture_output=True, text=True)

        if result.returncode != 0:
            return f"Error calling JavaScript: {result.stderr}"

        # Parse the output as JSON
        itineraries = json.loads(result.stdout)

        if itineraries:
            responses = []
            for itin in itineraries:
                price = itin['price']
                origin_name = itin['origin']['name']
                origin_city = itin['origin']['city']
                origin_country = itin['origin']['country']
                origin_display_code = itin['origin']['displayCode']
                
                dest_name = itin['destination']['name']
                dest_city = itin['destination']['city']
                dest_country = itin['destination']['country']
                dest_display_code = itin['destination']['displayCode']
                
                departure_time = itin['departure']
                arrival_time = itin['arrival']
                
                responses.append(
                    f"Price for flight: {price}\n"
                    f"Origin Name: {origin_name}\n"
                    f"Origin City: {origin_city}\n"
                    f"Origin Country: {origin_country}\n"
                    f"Origin Display Code: {origin_display_code}\n"
                    f"Destination Name: {dest_name}\n"
                    f"Destination City: {dest_city}\n"
                    f"Destination Country: {dest_country}\n"
                    f"Destination Display Code: {dest_display_code}\n"
                    f"Departure Time: {departure_time}\n"
                    f"Arrival Time: {arrival_time}\n"
                )
            return "\n".join(responses)

        else:
            return "No available options."

    except Exception as e:
        return f"Error calling JavaScript: {str(e)}"


def reset_question_index():
    session['current_question_index'] = 0

import subprocess
import json

def extract_titles():
    global grouped_data  # Ensure this is declared as global at the beginning

    try:
        # Run the JavaScript file and capture the output
        json_output = subprocess.run(['node', 'fetch_titles.js'], capture_output=True, text=True)

        # Check if the JavaScript executed successfully
        if json_output.returncode != 0:
            return f"Error calling JavaScript: {json_output.stderr.strip()}"  # Strip to clean output

        # Load the JSON data
        json_data = json.loads(json_output.stdout)

        # Initialize grouped_data if it's not already done
        if 'grouped_data' not in globals():
            grouped_data = {}

        # Check if the data has the expected structure
        if json_data.get('status'):
            # Process each entity in the data list
            for entity in json_data.get('data', []):
                title = entity.get('presentation', {}).get('title')
                entity_id = entity.get('entityId')

                # Add the title and entity_id to the corresponding entity type
                if title and entity_id not in grouped_data:
                    # Use entity_id as the key to avoid duplicates
                    grouped_data[entity_id] = title

            # Format the output for return
            output = [f"{title} ({entity_id})" for entity_id, title in grouped_data.items()]
            return output if output else ["No titles found."]  # Handle empty case

        else:
            return ["Status is false, no data to display."]
    
    except json.JSONDecodeError:
        return ["Error decoding JSON response."]
    except Exception as error:
        return [f"Error: {str(error)}"]  # Ensure error is converted to string


    
# Flight booking questions
def flight_booking_flow(user_input):
    """Flow for booking flights."""
    global grouped_data
    import http.client
    import json

    # Create a connection
    conn = http.client.HTTPSConnection("sky-scrapper.p.rapidapi.com")

    # Define the headers
    url = "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport?query=new&locale=en-US"
    headers = {
        'x-rapidapi-key': "e249a3f4cbmsh4f1a4ad98e12a42p1dc226jsnee8181aac2e0",
        'x-rapidapi-host': "sky-scrapper.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        api_response = response.json()
        entity_to_sky_dict = {}

        if api_response.get("status"):
            # Loop through each item in the data list
            for item in api_response.get("data", []):
                entity_id = item.get("entityId")
                sky_id = item.get("skyId")
        
                # Store in the dictionary
                entity_to_sky_dict[entity_id] = sky_id
    except requests.exceptions.RequestException as e:
        return f"Error making request: {e}"
    # Make the request
    conn.request("GET", "/api/v1/flights/searchAirport?query=new&locale=en-US", headers=headers)

    # Get the response
    res = conn.getresponse()
    data = res.read()

    # Decode the response data and store it in a variable as a JSON object
    api_response = json.loads(data.decode("utf-8"))

    # Create a dictionary to map entityId to skyId
    entity_to_sky_dict = {}

    # Check if the response status is true
    if api_response.get("status"):
        # Loop through each item in the data list
        for item in api_response.get("data", []):
            entity_id = item.get("entityId")
            sky_id = item.get("skyId")
        
            # Store in the dictionary
            entity_to_sky_dict[entity_id] = sky_id

    titles_output = extract_titles()
    # Display the available options to the user
    if titles_output:
        response = f"Available options:\n{titles_output}\n"
    else:
        response = "No available options found.\n"

    questions = [
        "Hello I am here to guide to towards flight booking"
        f"{response}Where do you want to travel to?", 
        "Where do you want to travel from?", 
        "What is your expected departure date? (Format: YYYY-MM-DD)",
        "What is your expected arrival date? (Format: YYYY-MM-DD)",
        "Which type of cabin class do you prefer: \n1. Economy\n2. Premium Economy\n3. Business\n4. First\n5. Will inform later",
        "Number of Adults travelling?",
        "Number of children travelling (2-12 yrs)?",
        "Number of infants in travel (UNDER 2 yrs)?",
        "What is your preference in flights: \n1. Best Experience\n2. Cheapest Travel\n3. Fastest Reach"
    ]

    if 'current_question_index' not in session:
        session['user_responses'] = {'flight_booking': {}} 
        session['current_question_index'] = 0

    current_question_index = session['current_question_index']

    if ((current_question_index == 1) or (current_question_index == 2)):
        for key,value in grouped_data.items():
            if (value==user_input):
                save_response('flight_booking', current_question_index, key)
                break

    elif ((current_question_index ==3) or  (current_question_index ==4)) :
        save_response('flight_booking', current_question_index, user_input)
    
    elif (current_question_index == 5):
        class_mapping = {
            1: 'economy',
            2: 'premium_economy',
            3: 'business',
            4: 'first',
            5: 'NULL'
        }

        # Save the response
        save_response('flight_booking', current_question_index, class_mapping.get(int(user_input)))
        response_message = save_response('flight_booking', current_question_index, class_mapping.get(user_input))
        print(response_message) 
    
    elif ((current_question_index >=6)  and (current_question_index <=8)):
        save_response('flight_booking', current_question_index, int(user_input))

    elif (current_question_index == 9):
        class_mapping = {
            1: 'best',
            2: 'cheap',
            3: 'fast',
            4: 'NULL'
        }
        # Save the response
        save_response('flight_booking', current_question_index, class_mapping.get(int(user_input)))

    if (current_question_index==len(questions)):
        response_summary = fetch_flight_options(user_responses)
        return response_summary

    current_question_index = session['current_question_index']
    session['current_question_index'] += 1  
    next_question = questions[current_question_index]
    return next_question  # Return the next question

# Hotel booking questions
def hotel_booking_flow(user_input):
    if 'hotel_city' not in user_responses:
        save_response('hotel_city', user_input)
        return "Enter the check-in date (YYYY-MM-DD): "
    
    elif 'check_in_date' not in user_responses:
        save_response('check_in_date', user_input)
        return "Enter the check-out date (YYYY-MM-DD): "
    
    elif 'check_out_date' not in user_responses:
        save_response('check_out_date', user_input)
        return "What is your budget per night? "
    
    elif 'hotel_budget' not in user_responses:
        save_response('hotel_budget', user_input)
        return "What type of room are you looking for (e.g., single, double, suite)? "

# Trip planning questions
def trip_planning_flow(user_input):
    if 'trip_destination' not in user_responses:
        save_response('trip_destination', user_input)
        return "Where are you planning to visit? "
    
    elif 'trip_duration' not in user_responses:
        save_response('trip_duration', user_input)
        return "How many days will you be spending there? "
    
    elif 'trip_interests' not in user_responses:
        save_response('trip_interests', user_input)
        return "What are your areas of interest (e.g., historical sites, adventure, shopping)? "

# Weather enquiry questions
def weather_enquiry_flow(user_input):
    if 'weather_city' not in user_responses:
        save_response('weather_city', user_input)
        return f"\nFetching weather information for {user_input}...\n"

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# API to handle chatbot interaction
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_choice = data.get('user_choice')
    user_input = data.get('user_input')
    
    # Get the appropriate response
    response = travel_assistant(user_choice, user_input)
    
    return jsonify({'response': response})

if __name__ == "__main__":  # Corrected __name__
    app.run(debug=True)
