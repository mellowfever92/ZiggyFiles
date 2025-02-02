import json
import re
import requests
from bs4 import BeautifulSoup
from docx import Document
import argparse
import sys
from urllib.parse import urlencode, quote_plus

def fetch_birth_chart_data(user_name, birth_date, birth_time_hour, birth_time_minute, birth_time_ampm, address, txt_filename='results.txt'):
    """Fetches birth chart data by constructing a GET request to the astrology site."""

    # Convert birth date and time to the required format
    # birth_date is in 'mm-dd-yyyy', we need day, month, year
    birth_month, birth_day, birth_year = birth_date.split('-')
    # Convert to integers
    birth_day = int(birth_day)
    birth_month = int(birth_month)
    birth_year = int(birth_year)

    # Convert birth time to 24-hour format
    birth_hour = int(birth_time_hour)
    birth_minute = int(birth_time_minute)
    if birth_time_ampm.upper() == 'PM' and birth_hour != 12:
        birth_hour += 12
    elif birth_time_ampm.upper() == 'AM' and birth_hour == 12:
        birth_hour = 0

    # Use Google Maps Geocoding API to get latitude and longitude
    # Replace 'GOOGLE_KEY' with your actual API key 
    api_key = 'AIzaSyApCYq4S2V7yL4BBqdtLggl4s9RdWXe6Yo' 
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    # Format the address according to Google Geocoding API requirements
    formatted_address = address.strip()
    geocode_params = {'address': formatted_address, 'key': api_key}
    response = requests.get(geocode_url, params=geocode_params)
    if response.status_code != 200:
        print("Error fetching geocoding data.")
        return None

    data = response.json()
    if data['status'] != 'OK':
        print("Error in geocoding response:", data['status'])
        return None

    location = data['results'][0]['geometry']['location']
    latitude = location['lat']
    longitude = location['lng']
    address_components = data['results'][0]['address_components']

    # Convert latitude and longitude to degrees and minutes
    def decimal_to_deg_min(decimal_coord):
        degrees = int(abs(decimal_coord))
        minutes = (abs(decimal_coord) - degrees) * 60
        return degrees, minutes

    lat_deg, lat_min = decimal_to_deg_min(latitude)
    lon_deg, lon_min = decimal_to_deg_min(longitude)

    # Determine direction
    lat_direction = 0 if latitude >= 0 else 1  # 0 for North, 1 for South
    lon_direction = 1 if longitude >= 0 else 0  # 1 for East, 0 for West

    # Get country and state codes
    country_code = ''
    state_code = ''
    city_name = ''
    for component in address_components:
        if 'country' in component['types']:
            country_code = component['short_name']
        if 'administrative_area_level_1' in component['types']:
            state_code = component['short_name']
        if 'locality' in component['types']:
            city_name = component['long_name']

    if not city_name:
        city_name = formatted_address  # Fallback to the provided address

    # Prepare parameters for the GET request to the astrology site
    astro_params = {
        'input_natal': '1',
        'send_calculation': '1',
        'narozeni_den': birth_day,
        'narozeni_mesic': birth_month,
        'narozeni_rok': birth_year,
        'narozeni_hodina': birth_hour,
        'narozeni_minuta': birth_minute,
        'narozeni_sekunda': '00',
        'narozeni_city': f"{city_name}, {state_code}, {country_code}",
        'narozeni_mesto_hidden': city_name,
        'narozeni_stat_hidden': country_code,
        'narozeni_podstat_kratky_hidden': state_code,
        'narozeni_sirka_stupne': str(lat_deg),
        'narozeni_sirka_minuty': f"{lat_min:.2f}",
        'narozeni_sirka_smer': str(lat_direction),
        'narozeni_delka_stupne': str(lon_deg),
        'narozeni_delka_minuty': f"{lon_min:.2f}",
        'narozeni_delka_smer': str(lon_direction),
        'narozeni_timezone_form': 'auto',
        'narozeni_timezone_dst_form': 'auto',
        'house_system': 'placidus',
        'hid_fortune': '1',
        'hid_fortune_check': 'on',
        'hid_vertex': '1',
        'hid_vertex_check': 'on',
        'hid_chiron': '1',
        'hid_chiron_check': 'on',
        'hid_lilith': '1',
        'hid_lilith_check': 'on',
        'hid_uzel': '1',
        'hid_uzel_check': 'on',
        'tolerance': '1',
        'aya': '',
        'tolerance_paral': '1.2'
    }

    base_url = 'https://horoscopes.astro-seek.com/calculate-birth-chart-horoscope-online/'
    full_url = f"{base_url}?{urlencode(astro_params, quote_via=quote_plus)}"

    # Fetch the data from the astrology site
    response = requests.get(full_url)
    if response.status_code != 200:
        print("Error fetching birth chart data.")
        return None

    # Save raw HTML response to a txt file
    with open(txt_filename, 'w', encoding='utf-8') as txt_file:
        txt_file.write(response.text)

    # Parse the response to extract the birth chart data
    soup = BeautifulSoup(response.text, 'html.parser')

    api_response = {
        'planets': [],
        'houses': [],
        'main_aspects': [],
        'other_aspects': []
    }

    # Function to parse degree notation from HTML content
    def parse_degree_html(cell):
        degree = ''
        for element in cell.contents:
            if isinstance(element, str):
                degree += element.strip()
            elif element.name == 'span':
                degree += element.get_text(strip=True)
        return degree

    # Function to find the section by text and parse the following table
    def parse_section_table(soup, section_text):
        # Find the span containing the section text
        section_span = soup.find('span', string=section_text)
        if section_span:
            # Navigate to the next table
            next_table = section_span.find_next('table')
            if next_table:
                return next_table
            else:
                # If no table found, look further in the siblings
                parent = section_span.parent
                next_sibling = parent.find_next_sibling()
                while next_sibling:
                    if next_sibling.name == 'table':
                        return next_sibling
                    elif next_sibling.find('table'):
                        return next_sibling.find('table')
                    next_sibling = next_sibling.find_next_sibling()
        print(f"Section '{section_text}' not found.")
        return None

    # --- Parse Planets Table ---
    planets_table = parse_section_table(soup, 'Planets:')
    if planets_table:
        rows = planets_table.find_all('tr')
        for idx, row in enumerate(rows[1:]):  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 5:
                planet = cells[0].get_text(strip=True)
                sign = cells[1].get_text(strip=True)
                degree = parse_degree_html(cells[2])
                house = cells[3].get_text(strip=True)
                motion = cells[4].get_text(strip=True)
                api_response['planets'].append({
                    'index': idx,
                    'planet': planet,
                    'sign': sign,
                    'degree': degree,
                    'house': house,
                    'motion': motion
                })

    # --- Parse Houses Tables (There are two tables for houses 1-6 and 7-12) ---
    houses_table = parse_section_table(soup, 'Houses:')
    if houses_table:
        tables = [houses_table]
        # Check for additional houses table
        next_table = houses_table.find_next('table')
        if next_table and next_table != houses_table:
            tables.append(next_table)
        idx = 0
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 0:
                    house_number = cells[0].get_text(strip=True)
                    sign = cells[1].get_text(strip=True)
                    degree = parse_degree_html(cells[2])
                    api_response['houses'].append({
                        'index': idx,
                        'house_number': house_number,
                        'sign': sign,
                        'degree': degree
                    })
                    idx += 1

    # --- Parse Main Aspects Table ---
    main_aspects_table = parse_section_table(soup, 'Main aspects:')
    if main_aspects_table:
        rows = main_aspects_table.find_all('tr')
        for idx, row in enumerate(rows[1:]):  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 5:
                planet1 = cells[0].get_text(strip=True)
                aspect_type = cells[1].get_text(strip=True)
                planet2 = cells[2].get_text(strip=True)
                orb = parse_degree_html(cells[3])
                applying_separating = cells[4].get_text(strip=True)
                api_response['main_aspects'].append({
                    'index': idx,
                    'planet1': planet1,
                    'aspect': aspect_type,
                    'planet2': planet2,
                    'orb': orb,
                    'applying_separating': applying_separating
                })

    # --- Parse Other Aspects Table ---
    other_aspects_table = parse_section_table(soup, 'Other aspects:')
    if other_aspects_table:
        rows = other_aspects_table.find_all('tr')
        for idx, row in enumerate(rows[1:]):  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 5:
                object1 = cells[0].get_text(strip=True)
                aspect_type = cells[1].get_text(strip=True)
                object2 = cells[2].get_text(strip=True)
                orb = parse_degree_html(cells[3])
                applying_separating = cells[4].get_text(strip=True)
                api_response['other_aspects'].append({
                    'index': idx,
                    'object1': object1,
                    'aspect': aspect_type,
                    'object2': object2,
                    'orb': orb,
                    'applying_separating': applying_separating
                })

    # --- Write results to results.txt ---
    with open(txt_filename, 'w', encoding='utf-8') as txt_file:
        # Write Planets
        for planet_info in api_response['planets']:
            planet = planet_info['planet']
            sign = planet_info['sign']
            degree = planet_info['degree']
            house = planet_info['house']
            motion = planet_info['motion']
            txt_file.write(f"The planet/celestial body {planet} is in {sign}, House {house}, at {degree}.\n")

        # Write Houses
        for house_info in api_response['houses']:
            house_number = house_info['house_number']
            sign = house_info['sign']
            degree = house_info['degree']
            txt_file.write(f"House {house_number} is in {sign} at {degree}.\n")

        # Write Main Aspects
        for aspect_info in api_response['main_aspects']:
            planet1 = aspect_info['planet1']
            aspect = aspect_info['aspect']
            planet2 = aspect_info['planet2']
            orb = aspect_info['orb']
            applying_separating = aspect_info['applying_separating']
            txt_file.write(f"{planet1} forms a {aspect} with {planet2} (orb: {orb}, {applying_separating}).\n")

        # Write Other Aspects
        for aspect_info in api_response['other_aspects']:
            object1 = aspect_info['object1']
            aspect = aspect_info['aspect']
            object2 = aspect_info['object2']
            orb = aspect_info['orb']
            applying_separating = aspect_info['applying_separating']
            txt_file.write(f"{object1} forms a {aspect} with {object2} (orb: {orb}, {applying_separating}).\n")

    return {'api_response': api_response}

def save_to_jsonl(data, filename='results.jsonl', system_prompt=''):
    """Saves the extracted data to a JSONL file in the specified structure."""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            total_requests = sum(len(data.get('api_response', {}).get(key, [])) for key in ['planets', 'houses', 'main_aspects', 'other_aspects'])
            custom_id_prefix = 'request-'

            # Extract the relevant data from the API response
            api_response = data.get('api_response')
            if not api_response:
                print("No data available to process.")
                return

            data_items = []

            # Process planets
            planets = api_response.get('planets', [])
            for body in planets:
                index = body.get('index')
                planet = body.get('planet')
                sign = body.get('sign')
                degree = body.get('degree')
                house = body.get('house')
                motion = body.get('motion')
                user_content = (f"The planet/body {planet} is in {sign} at {degree}, "
                                f"in house {house}, with a {motion} motion.")
                data_items.append({'index': index, 'content': user_content})

            # Process houses
            houses = api_response.get('houses', [])
            for house_info in houses:
                index = house_info.get('index')
                house_number = house_info.get('house_number')
                sign = house_info.get('sign')
                degree = house_info.get('degree')
                user_content = f"House {house_number} ({sign}) is at {degree}."
                data_items.append({'index': index + 1000, 'content': user_content})  # Adding 1000 to index to ensure ordering after planets

            # Process main aspects
            main_aspects = api_response.get('main_aspects', [])
            for aspect in main_aspects:
                index = aspect.get('index')
                planet1 = aspect.get('planet1')
                aspect_type = aspect.get('aspect')
                planet2 = aspect.get('planet2')
                orb = aspect.get('orb')
                applying_separating = aspect.get('applying_separating')
                user_content = (f"{planet1} forms a {aspect_type} with {planet2} "
                                f"(orb: {orb}, {applying_separating}).")
                data_items.append({'index': index + 2000, 'content': user_content})  # Adding 2000 to index for ordering

            # Process other aspects
            other_aspects = api_response.get('other_aspects', [])
            for aspect in other_aspects:
                index = aspect.get('index')
                object1 = aspect.get('object1')
                aspect_type = aspect.get('aspect')
                object2 = aspect.get('object2')
                orb = aspect.get('orb')
                applying_separating = aspect.get('applying_separating')
                user_content = (f"{object1} forms a {aspect_type} with {object2} "
                                f"(orb: {orb}, {applying_separating}).")
                data_items.append({'index': index + 3000, 'content': user_content})  # Adding 3000 to index

            if not data_items:
                print("No data available to process.")
                return

            data_items.sort(key=lambda x: x['index'])
            data_length = len(data_items)
            index = 0
            for i in range(1, total_requests + 1): 
                # Cycle through the data if there are fewer items than total_requests
                user_content = data_items[index % data_length]['content']
                index += 1

                json_object = {
                    "custom_id": f"{custom_id_prefix}{i}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ]
                    }
                }

                json_line = json.dumps(json_object, ensure_ascii=False)
                file.write(json_line + '\n')

            print(f"Data saved to {filename} with {total_requests} requests.")
    except Exception as e:
        print(f"An error occurred while saving data to JSONL: {e}")

def process_api_output(jsonl_file, docx_file):
    """Processes the OpenAI API output JSONL file and writes assistant responses to a .docx file."""
    try:
        document = Document()
        with open(jsonl_file, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    json_obj = json.loads(line)
                    # Check for errors in the response
                    error = json_obj.get('error')
                    if error is not None:
                        print(f"Line {line_number}: Error in response: {error}")
                        continue
                    # Get the 'response' field
                    response = json_obj.get('response', {})
                    if not response:
                        print(f"Line {line_number}: No 'response' found.")
                        continue
                    status_code = response.get('status_code')
                    if status_code != 200:
                        print(f"Line {line_number}: Non-200 status code: {status_code}")
                        continue
                    # Get the 'body' field
                    body = response.get('body', {})
                    if not body:
                        print(f"Line {line_number}: No 'body' in response.")
                        continue
                    # Extract assistant's content
                    choices = body.get('choices', [])
                    if not choices:
                        print(f"Line {line_number}: No choices found in body.")
                        continue
                    assistant_content = choices[0].get('message', {}).get('content', '')
                    # Add content to document
                    if assistant_content:
                        assistant_content = assistant_content.strip()
                        document.add_paragraph(assistant_content)
                    else:
                        print(f"Line {line_number}: Assistant content is empty.")
                except json.JSONDecodeError as e:
                    print(f"Line {line_number}: JSON decode error: {e}")
        document.save(docx_file)
        print(f"Assistant's responses have been saved to {docx_file}")
    except Exception as e:
        print(f"An error occurred while processing the API output: {e}")

def main():
    parser = argparse.ArgumentParser(description="Astrology Chart Processor")
    subparsers = parser.add_subparsers(dest='command')

    # Subparser for Phase 1: Generate JSONL file
    parser_phase1 = subparsers.add_parser('generate', help='Generate JSONL file for OpenAI batch API')
    parser_phase1.add_argument('--name', required=False, help='Your name')
    parser_phase1.add_argument('--birthdate', required=False, help='Birth date (mm-dd-yyyy)')
    parser_phase1.add_argument('--birthhour', required=False, help='Birth hour (1-12)')
    parser_phase1.add_argument('--birthminute', required=False, help='Birth minute (0-59)')
    parser_phase1.add_argument('--ampm', required=False, choices=['AM', 'PM'], help='AM or PM')
    parser_phase1.add_argument('--address', required=False, help="Birth city, state, and country (e.g., 'Los Angeles, CA, USA')")

    # Subparser for Phase 2: Process API output into .docx
    parser_phase2 = subparsers.add_parser('process', help='Process OpenAI API output JSONL file into .docx')
    parser_phase2.add_argument('--input', required=True, help='Path to OpenAI API output JSONL file')
    parser_phase2.add_argument('--output', required=True, help='Desired .docx output filename')

    args = parser.parse_args()

    if args.command == 'generate':
        # Collect inputs
        user_name = args.name or input("Enter your name: ")
        birth_date = args.birthdate or input("Enter your birth date (mm-dd-yyyy): ")
        birth_time_hour = args.birthhour or input("Enter birth hour (1-12): ")
        birth_time_minute = args.birthminute or input("Enter birth minute (0-59): ")
        birth_time_ampm = args.ampm or input("Enter AM or PM: ").upper()
        address = args.address or input("Enter your birth city, state, and country (e.g., 'Los Angeles, CA, USA'): ")

        # Sanitize the user_name to create a valid filename
        sanitized_user_name = re.sub(r'[<>:"/\\|?*]', '', user_name)  # Remove invalid filename characters
        sanitized_user_name = sanitized_user_name.strip().replace(' ', '_')  # Replace spaces with underscores
        sanitized_user_name = sanitized_user_name.lower()  # Convert to lowercase

        # Validate inputs
        if not birth_date:
            print("Birth date is required.")
            return

        if not birth_time_hour or not birth_time_minute or not birth_time_ampm:
            print("Birth time is required.")
            return
        if birth_time_ampm not in ['AM', 'PM']:
            print("Invalid time period entered. Please enter 'AM' or 'PM'.")
            return

        # Fetch data from the astrology site
        data = fetch_birth_chart_data(
            user_name=user_name,
            birth_date=birth_date,
            birth_time_hour=birth_time_hour,
            birth_time_minute=birth_time_minute,
            birth_time_ampm=birth_time_ampm,
            address=address,
            txt_filename=f"{sanitized_user_name}_raw_results.txt"
        )

        if data:
            # System prompt for OpenAI's API
            system_prompt = "[my system prompt will go here]" 
            # Save data to JSONL
            save_to_jsonl(data, filename=f"{sanitized_user_name}.jsonl", system_prompt=system_prompt)
            print(f"JSONL file '{sanitized_user_name}.jsonl' has been generated.")
            print("Please submit the generated JSONL file to the OpenAI batch API. After you receive the output, run this script with the 'process' command to generate the .docx file.")
        else:
            print("Failed to fetch data from the astrology site.")

    elif args.command == 'process':
        jsonl_file = args.input
        docx_file = args.output
        process_api_output(jsonl_file, docx_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()