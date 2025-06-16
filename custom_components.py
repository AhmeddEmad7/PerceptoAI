from haystack import component
import requests
import re
from num2words import num2words

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
    def run(self, query: str = None) -> dict:
        location = self.get_user_location()
        return {"content": f"Based on your location, you are at {location}."}


@component
class DateTimeRetriever:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @component.output_types(datetime=dict)
    def run(self, query: str) -> dict:
        match = re.search(r"(?:date|time|وقت|تاريخ|ساعة).*?(?:in|at|for|في)\s+([a-zA-Z\s]+)", query, re.IGNORECASE)
        extracted = match.group(1).strip() if match else ""

        filler_terms = {"time", "date", "today", "now", "it", "is", "this", "وقت", "تاريخ", "اليوم", "الآن", "ساعة", ""}
        if extracted.lower() in filler_terms or not extracted:
            location = "Cairo"
        else:
            location = extracted.title()

        print(f"Fetching time for location: {location}")
        url = f"http://api.weatherapi.com/v1/timezone.json?key={self.api_key}&q={location}"
        try:
            response = requests.get(url)
            print(f"Time API response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                location_name = data['location']['name']
                country = data['location']['country']
                localtime = data['location']['localtime']

                date_part, time_part = localtime.split()
                year, month, day = map(int, date_part.split('-'))
                hour, minute = map(int, time_part.split(':'))

                include_date = any(term in query.lower() for term in ["date", "تاريخ"])
                include_time = any(term in query.lower() for term in ["time", "وقت", "ساعة"])

                if not include_date and not include_time:
                    include_date = include_time = True

                parts = []
                if include_date:
                    # Verbalize date (e.g., "eleventh of June two thousand twenty-five")
                    day_text = num2words(day, to='ordinal', lang='en')
                    month_text = ["January", "February", "March", "April", "May", "June",
                                  "July", "August", "September", "October", "November", "December"][month-1]
                    year_text = num2words(year, lang='en')
                    parts.append(f"the date is {day_text} of {month_text} {year_text}")
                if include_time:
                    # Verbalize time (e.g., "thirteen and seventeen")
                    hour_text = num2words(hour, lang='en')
                    minute_text = num2words(minute, lang='en')
                    parts.append(f"the time is {hour_text} and {minute_text}")

                joined = " and ".join(parts)
                content = f"In {location_name}, {country}, {joined}."

                result = {'content': content, 'url': "https://www.weatherapi.com/"}
            else:
                error_message = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"Time API error: {error_message}")
                result = {'content': "Sorry, I couldn't retrieve the time.", 'url': ""}
        except Exception as e:
            print(f"Time API request error: {str(e)}")
            result = {'content': "Sorry, I couldn't retrieve the time.", 'url': ""}

        return result


@component
class WeatherRetriever:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @component.output_types(weather=dict)
    def run(self, query: str) -> dict:
        location_patterns = [
            r"(?:in|at|for)\s+([a-zA-Z\s]+)", 
        ]
        
        location = None
        for pattern in location_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) > 2 and extracted.lower() not in ["it", "is", "today", "now"]:
                    location = extracted.title()
                    break

        if not location:
            try:
                ip_data = requests.get("http://ip-api.com/json/").json()
                location = ip_data.get("city", "Cairo")
            except Exception as e:
                print(f"IP location error: {str(e)}")
                location = "Cairo"

        print(f"Fetching weather for location: {location}")
        url = f"https://api.weatherapi.com/v1/current.json?key={self.api_key}&q={location}"
        try:
            response = requests.get(url)
            print(f"Weather API response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                location_name = data['location']['name']
                country = data['location']['country']
                condition = data['current']['condition']['text']
                temp_c = data['current']['temp_c']
                humidity = data['current']['humidity']
                wind_kph = data['current']['wind_kph']

                # Verbalize numbers
                temp_c_int = int(temp_c)
                temp_c_dec = int((temp_c - temp_c_int) * 10)
                temp_text = num2words(temp_c_int, lang='en')
                if temp_c_dec > 0:
                    temp_dec_text = num2words(temp_c_dec, lang='en')
                    temp_text += f" and {temp_dec_text} tenths"
                humidity_text = num2words(humidity, lang='en')
                wind_kph_int = int(wind_kph)
                wind_kph_dec = int((wind_kph - wind_kph_int) * 10)
                wind_text = num2words(wind_kph_int, lang='en')
                if wind_kph_dec > 0:
                    wind_dec_text = num2words(wind_kph_dec, lang='en')
                    wind_text += f" and {wind_dec_text} tenths"

                content = (
                    f"The current weather in {location_name}, {country} is {condition} "
                    f"with a temperature of {temp_text} degrees Celsius, "
                    f"humidity at {humidity_text} percent, "
                    f"and wind speed of {wind_text} kilometers per hour."
                )
                result = {'content': content, 'url': "https://www.weatherapi.com/"}
            else:
                error_message = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"Weather API error: {error_message}")
                result = {'content': "I'm sorry, I couldn't retrieve the weather right now.", 'url': ""}
        except Exception as e:
            print(f"Weather API request error: {str(e)}")
            result = {'content': "I'm sorry, I couldn't retrieve the weather right now.", 'url': ""}

        return result

@component
class SerpAPIWebSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def truncate_text(self, text: str) -> str:
        """Truncate the text after the second period."""
        periods = text.split('.')
        if len(periods) > 2:
            return '.'.join(periods[:2]) + '.'
        return text

    @component.output_types(web_documents=dict)
    def run(self, query: str) -> dict:
        print("Searching the web..")
        search_url = f"https://serpapi.com/search?q={query}&api_key={self.api_key}"
        response = requests.get(search_url)
        documents = {}

        if response.status_code == 200:
            search_results = response.json()
            top_results = search_results.get('organic_results', [])[:3]
            merged_snippet = ' '.join([
                self.truncate_text(result.get('snippet', '')) 
                for result in top_results
            ])
            links = [result.get('link', '') for result in top_results]
            documents['content'] = "I have searched the web and found the following: " + merged_snippet
            documents['url'] = ', '.join(links)
        else:
            documents['content'] = "I couldn't find any relevant information through web search."
            documents['url'] = ""

        return {"web_documents": documents}