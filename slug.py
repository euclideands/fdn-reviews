import requests
import json
from tqdm import tqdm  # Import tqdm for progress tracking

SKINCARE_SLUG = [
    'toner', 'face', 'eye-lip', 'cream-lotion', 'facial-wash', 'oil-2', 'scrub-exfoliator', 
    'eye-serum', 'eye-mask', 'eye-cream', 'skin-soothing-treatment', 'brow-lash-treatment', 
    'peeling', 'serum-essence', 'acne-treatment', 'sleeping-mask', 'nose-pack', 'mask-sheet', 
    'wash-off', 'lotion-emulsion', 'face-mist', 'gel', 'sun-protection-1', 'cream-1', 'face-oil'
]

def fetch_data(url, params, headers):
    """Fetch data from the API with retry policy."""
    retries = 3  # Number of retries
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Error fetching data: {e}")
            if attempt < retries - 1:  # If not the last attempt, wait before retrying
                print("Retrying...")
    return None  # Return None if all attempts fail

def extract_slugs(data):
    """Extract slugs from the payload data."""
    try:
        return [item['slug'] for item in data['payload']['data']]
    except (KeyError, TypeError) as e:
        print(f"Error extracting slugs: {e}")
        return []  # Return an empty list if there's an error

def fetch_slugs_for_slug(url, headers, slug):
    """Fetch all slugs for a given slug category."""
    all_slugs = []
    params = {
        'category': slug,
        'sort': 'popular',
        'page': 1,
        'limit': 500,  # Set limit to 500 for batch fetching
        'type': 'all'
    }

    # Fetch data for the first batch (500 items)
    raw_data = fetch_data(url, params, headers)
    if raw_data is None:  # Check if there was an error fetching data
        return all_slugs

    all_slugs.extend(extract_slugs(raw_data))  # Extract slugs from the fetched data

    # Check if more data exists and continue fetching in batches of 500
    while len(raw_data['payload']['data']) == 500:
        params['page'] += 1  # Increment the page number
        raw_data = fetch_data(url, params, headers)  # Fetch the next batch

        if raw_data is None:  # Check if there was an error fetching data
            break  # Exit loop if error occurs

        all_slugs.extend(extract_slugs(raw_data))  # Add slugs from this batch

    return all_slugs

def create_json_structure(slugs_dict):
    """Create a structured JSON from the dictionary of slugs."""
    return {
        "cleanser": {
            "toner": slugs_dict.get("toner", []),
            "makeup-remover": {
                "face": slugs_dict.get("face", []),
                "eye_lip": slugs_dict.get("eye-lip", [])
            },
            "cream-lotion": slugs_dict.get("cream-lotion", []),
            "facial-wash": slugs_dict.get("facial-wash", []),
            "oil-2": slugs_dict.get("oil-2", []),
            "scrub-exfoliator": slugs_dict.get("scrub-exfoliator", [])
        },
        "treatment": {
            "eye-treatment": {
                "eye-serum": slugs_dict.get("eye-serum", []),
                "eye-mask": slugs_dict.get("eye-mask", []),
                "eye-cream": slugs_dict.get("eye-cream", [])
            },
            "skin-soothing-treatment": slugs_dict.get("skin-soothing-treatment", []),
            "brow-lash-treatment": slugs_dict.get("brow-lash-treatment", []),
            "peeling": slugs_dict.get("peeling", []),
            "serum-essence": slugs_dict.get("serum-essence", []),
            "acne-treatment": slugs_dict.get("acne-treatment", [])
        },
        "mask": {
            "sleeping-mask": slugs_dict.get("sleeping-mask", []),
            "nose-pack": slugs_dict.get("nose-pack", []),
            "mask-sheet": slugs_dict.get("mask-sheet", []),
            "wash-off": slugs_dict.get("wash-off", [])
        },
        "moisturizer": {
            "lotion-emulsion": slugs_dict.get("lotion-emulsion", []),
            "face-mist": slugs_dict.get("face-mist", []),
            "gel": slugs_dict.get("gel", []),
            "sun-protection-1": slugs_dict.get("sun-protection-1", []),
            "cream-1": slugs_dict.get("cream-1", []),
            "face-oil": slugs_dict.get("face-oil", [])
        } 
    }

def main():
    url = "https://reviews.femaledaily.com/service_review/api/products"
    
    headers = {
        'key': 'client03-TSbs94s3q5H9PP2yNPBr',
        'version': '1.5',
        'device': '3',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    # Dictionary to hold all slugs
    all_slugs = {slug: [] for slug in SKINCARE_SLUG}

    # Loop through each slug in SKINCARE_SLUG with progress tracking
    for slug in tqdm(SKINCARE_SLUG, desc="Fetching data for slugs"):
        all_slugs[slug] = fetch_slugs_for_slug(url, headers, slug)  # Fetch slugs for the current category

    # Create structured JSON output with all slugs
    structured_output = create_json_structure(all_slugs)

    # Save structured JSON output to a file
    with open("skincare-slug.json", "w") as json_file:
        json.dump(structured_output, json_file, indent=4)  # Pretty print the JSON data to file

    print("Data saved to skincare-slug.json")

if __name__ == "__main__":
    main()