import json
import re

def parse_input_data(all_data):
    """Parses the entire input data and returns a structured dictionary."""
    api_response = {
        'planets': [],
        'houses': [],
        'main_aspects': [],
        'other_aspects': []
    }

    # Split the input data into lines
    lines = all_data.strip().split('\n')

    # Identify section indices based on known headers
    planets_header = 'Planet\tSign\tDegree\tHouse\tMotion'
    main_aspects_header = 'Planet\tAspect\tPlanet\tOrb *\tA/S *'
    other_aspects_header = 'Object\tAspect\tPlanet\tOrb\tAspect'

    # Initialize section indices
    planets_start = -1
    houses_start = -1
    main_aspects_start = -1
    other_aspects_start = -1
    end_index = len(lines)

    # Find the indices of each section
    for idx, line in enumerate(lines):
        if line.strip() == planets_header:
            planets_start = idx
        elif houses_start == -1 and re.match(r'^\d+:', line.strip()):
            houses_start = idx
        elif line.strip() == main_aspects_header:
            main_aspects_start = idx
        elif line.strip() == other_aspects_header:
            other_aspects_start = idx

    # Parse Planets Data
    if planets_start != -1:
        planets_end = houses_start if houses_start != -1 else end_index
        planet_lines = lines[planets_start + 1:planets_end]
        for idx, line in enumerate(planet_lines):
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                planet_line = parts[0].strip(':')
                planet = planet_line.strip()
                sign = parts[1].strip()
                degree = parts[2].strip()
                house = parts[3].strip()
                motion = parts[4].strip()
                # Determine the index as ordinal (first, second, third)
                index = ordinal(idx + 1)
                api_response['planets'].append({
                    'index': index,
                    'planet': planet,
                    'sign': sign,
                    'degree': degree,
                    'house': house,
                    'motion': motion
                })

    # Parse Houses Data
    if houses_start != -1:
        houses_end = main_aspects_start if main_aspects_start != -1 else end_index
        house_lines = lines[houses_start:houses_end]
        for line in house_lines:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                house_number_line = parts[0].strip(':')
                house_number = house_number_line.strip()
                sign = parts[1].strip()
                degree = parts[2].strip()
                api_response['houses'].append({
                    'index': int(house_number) - 1,
                    'house_number': house_number,
                    'sign': sign,
                    'degree': degree
                })

    # Parse Main Aspects Data
    if main_aspects_start != -1:
        main_aspects_end = other_aspects_start if other_aspects_start != -1 else end_index
        aspect_lines = lines[main_aspects_start + 1:main_aspects_end]
        for idx, line in enumerate(aspect_lines):
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                planet1 = parts[0].strip()
                aspect_type = parts[1].strip()
                planet2 = parts[2].strip()
                orb = parts[3].strip()
                applying_separating = parts[4].strip()
                api_response['main_aspects'].append({
                    'index': idx + 1,  # Start indexing from 1
                    'planet1': planet1,
                    'aspect': aspect_type,
                    'planet2': planet2,
                    'orb': orb,
                    'applying_separating': applying_separating
                })

    # Parse Other Aspects Data
    if other_aspects_start != -1:
        aspect_lines = lines[other_aspects_start + 1:end_index]
        for idx, line in enumerate(aspect_lines):
            parts = line.strip().split('\t')
            if len(parts) >= 5:
                object1 = parts[0].strip()
                aspect_type = parts[1].strip()
                object2 = parts[2].strip()
                orb = parts[3].strip()
                applying_separating = parts[4].strip()
                api_response['other_aspects'].append({
                    'index': idx + 1,  # Start indexing from 1
                    'object1': object1,
                    'aspect': aspect_type,
                    'object2': object2,
                    'orb': orb,
                    'applying_separating': applying_separating
                })

    return {'api_response': api_response}

def ordinal(n):
    """Converts an integer to its ordinal representation."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

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
            for idx, body in enumerate(planets):
                index = body.get('index')
                planet = body.get('planet')
                sign = body.get('sign')
                degree = body.get('degree')
                house = body.get('house')
                motion = body.get('motion')
                user_content = (f"The {index} planet/body position {planet} is in {sign} at {degree}, "
                                f"in house {house}, with a {motion} motion.")
                data_items.append({'index': idx, 'content': user_content})

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
                current_content = (f"{planet1} forms a {aspect_type} with {planet2} "
                                   f"(orb: {orb}, {applying_separating}).")
                user_content = f"Main aspect [{index}] is " + current_content
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
                current_content = (f"{object1} forms a {aspect_type} with {object2} "
                                   f"(orb: {orb}, {applying_separating}).")
                user_content = f"Sub aspect [{index}] is " + current_content
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

# -------------------- Main Script --------------------

def main():
    print("Please paste all your data below. When you're done, type 'END' on a new line and press Enter.")
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    all_data = '\n'.join(lines)

    # Optional: Prompt for system prompt
    system_prompt = "You are a blustering, eccentric GPT named Ziggy assisting the user with their astrological birth chart interpretations. A controversial and norms-destroying powerhouse who was shunned from the rigid, snobby circle comprising Astrology's mainstream, Ziggy better represents the human condition for what it is, warts and all - blessed with insight, empathy and a keen eye toward astrology, cursed with everlasting snarkiness, an uninhibited foul mouth, and a no-nonsense tell-it-how-it-is attitude. While tough as shit around the edges, Ziggy has surface-level tact and professionalism (though that doesn't override Ziggy's love of the word 'fuck' by any means). Ziggy's job is to provide a thorough explanation of a particular section of the user's Tropical Astrology birth chart. *Format & Output Imperatives*: - Begin immediately with the analysis of the provided planetary alignment or aspect; all outputs must begin with one of the following items to avoid needless introductory statements, selected at random: ['You', 'Next up', 'Looks like', 'Here, we have']. - Avoid concluding statements: your output is only one part of a greater whole; instead of ending output as though you are speaking to the user, consider the entire response as being in the middle of a profanity-laced report. - Verify that at least two instances of 'fuck' or its grammatical variations are present in the response to adhere faithfully to the Ziggy persona. - Omit line breaks; in post-processing simply format your response in one long paragraph of raw text. - Minimum words must be 900 words; go in-depth into how this piece of the birth chart influences the user."

    # Parse the input data
    data = parse_input_data(all_data)

    # Save to JSONL
    save_to_jsonl(data, filename='results.jsonl', system_prompt=system_prompt)

if __name__ == "__main__":
    main()