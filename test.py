import requests

# Your location
LOCATION_NAME = "Balajinagar Community Hall, Kukatpally"

def get_lat_lng_geocode_xyz(location):
    """Fetch latitude and longitude using Geocode.xyz API."""
    geocode_url = f"https://geocode.xyz/{location.replace(' ', '%20')}?json=1"

    try:
        response = requests.get(geocode_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        
        # Print the response for debugging
        print(f"🔍 API Response:\n{response.text}")

        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return None, None

        data = response.json()
        if "latt" in data and "longt" in data:
            return data["latt"], data["longt"]
        else:
            print("❌ No data found.")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None, None

# Fetch coordinates
latitude, longitude = get_lat_lng_geocode_xyz(LOCATION_NAME)

if latitude and longitude:
    print(f"✅ Coordinates for '{LOCATION_NAME}': Latitude: {latitude}, Longitude: {longitude}")
else:
    print("❌ Could not fetch latitude and longitude for the given location.")