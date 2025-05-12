from haystack import component
import requests
import re

@component
class LocationRetriever:
    def __init__(self, api_key):
        self.api_key = api_key

    def _get_location_from_coordinates(self, latitude, longitude):
        """
        Get human-readable location description using OpenStreetMap Nominatim API.
        """
        try:
            url = 'https://nominatim.openstreetmap.org/reverse'
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'zoom': 18,
                'addressdetails': 1,
                'accept-language': 'en',
            }
            
            response = requests.get(url, params=params, headers={'User-Agent': 'PerceptoAI Location Service'})
            if response.status_code != 200:
                return 'Location description unavailable'
            
            data = response.json()
            components = {
                'location_name': data.get('display_name'),
                'city': data['address'].get('city'),
                'state': data['address'].get('state'),
                'neighbourhood': data['address'].get('neighbourhood'),
                'road': data['address'].get('road'),
                'postcode': data['address'].get('postcode'),
                'country': data['address'].get('country')
            }

            return components or 'Location unavailable'
        
        except Exception as e:
            print(f"Error getting location description: {e}")
            return 'Location description unavailable'
    
    def get_user_location(self):
        """
        Determine location using Google Maps Geocoding API.
        """    
        try:
            url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={self.api_key}'
            response = requests.post(url)
            
            
            if response.status_code != 200:
                print(f'Google Geolocation error: Received status code {response.status_code}')
                return None
            
            res = response.json()
            coords = res.get('location', {})
            latitude = str(coords.get('lat'))
            longitude = str(coords.get('lng'))

            location_data = self._get_location_from_coordinates(latitude, longitude) if latitude and longitude else 'Location description unavailable'
            # location_data {'location_name': 'TPL GOLF, Street 1, IVORYHILL, Sheikh Zayed, Giza, 12573, Egypt', 'city': 'Sheikh Zayed', 'state': 'Giza', 'neighbourhood': 'IVORYHILL', 'road': 'Street 1', 'postcode': '12573', 'country': 'Egypt'}
                
            return location_data['location_name']
        
        except Exception as e:
            print(f"Error determining location: {e}")
            return None

    @component.output_types(user_location=dict)
    def run(self, query: str) -> dict:
        location = self.get_user_location()
        return {"content": location}

@component
class DateTimeRetriever:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @component.output_types(result=dict)
    def run(self, query: str) -> dict:
        match = re.search(r"(?:time|date).*?(?:in|at|for)\s+([a-zA-Z\s]+)", query, re.IGNORECASE)
        location = match.group(1).strip().title() if match else "Cairo"

        url = f"http://api.weatherapi.com/v1/timezone.json?key={self.api_key}&q={location}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            location_name = data['location']['name']
            country = data['location']['country']
            localtime = data['location']['localtime']

            date_part, time_part = localtime.split()
            include_date = "date" in query.lower()
            include_time = "time" in query.lower()

            if not include_date and not include_time:
                include_date = include_time = True

            parts = []
            if include_date:
                parts.append(f"the date is {date_part}")
            if include_time:
                parts.append(f"the time is {time_part}")

            joined = " and ".join(parts)
            content = (
                f"In {location_name}, {country}, {joined}."
            )
            result = {'content': content, 'url': "https://www.weatherapi.com/"}
        else:
            result = {'content': "", 'url': ""}

        return result

@component
class WeatherRetriever:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @component.output_types(result=dict)
    def run(self, query: str) -> dict:
        # More comprehensive location detection for weather queries
        location_patterns = [
            r"(?:weather\s.*?(?:in|at|for)\s)([a-zA-Z\s]+)",  # Original pattern
            r"(?:how\s+(?:hot|cold)\s+(?:is\s+it\s+)?(?:in\s+)?)?([a-zA-Z\s]+)",  # Catch "how cold is it in Berlin"
            r"(?:temperature\s+(?:in\s+)?)?([a-zA-Z\s]+)",  # Catch "temperature in Berlin"
            r"(?:what\'s?\s+the\s+weather\s+(?:like\s+)?(?:in\s+)?)?([a-zA-Z\s]+)",  # Catch "what's the weather like in"
        ]
        
        location = None
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1).strip().title()
                break
        
        location = location or "Cairo"

        url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={location}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            location_name = data['location']['name']
            country = data['location']['country']
            condition = data['current']['condition']['text']
            temp_c = data['current']['temp_c']
            humidity = data['current']['humidity']
            wind_kph = data['current']['wind_kph']

            content = (
                f"The current weather in {location_name}, {country} is {condition} "
                f"with a temperature of {temp_c}°C, humidity at {humidity}%, "
                f"and wind speed of {wind_kph} kph."
            )
            result = {'content': content, 'url': "https://www.weatherapi.com/"}
        else:
            result = {'content': "", 'url': ""}

        return result

@component
class SerpAPIWebSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @component.output_types(web_documents=dict)
    def run(self, query: str) -> dict:
        search_url = f"https://serpapi.com/search?q={query}&api_key={self.api_key}"
        response = requests.get(search_url)
        documents = []

        if response.status_code == 200:
            search_results = response.json()
            for result in search_results.get('organic_results', [])[:2]:
                snippet = result.get('snippet', 'No snippet available')
                link = result.get('link', '')
                content = snippet
                documents.append({'content': content, 'url': link})
        else:
            documents.append({
                'content': "",
                'url': ""
            })

        return {"web_documents": documents}

