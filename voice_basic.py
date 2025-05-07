import speech_recognition as sr  # Library for speech recognition
import pyttsx3  # Text-to-speech conversion
import webbrowser  # Opening URLs in a web browser
import datetime  # Getting current time and date
import wikipedia  # Searching and fetching summaries from Wikipedia
import os  # Operating system-related functions (file handling, directory access)
import subprocess  # Running system commands and opening applications
import shutil  # File and directory management
from geopy.geocoders import Nominatim              # pip install geopy  and pip install geocoder
from geopy import distance
from geopy.distance import geodesic  # Calculating distances between geographical coordinates
import pyjokes  # Generating random jokes
# from fuzzywuzzy import process  # Fuzzy string matching to handle variations in user input
# import threading  # Running background processes for performance optimization
import requests  # Importing the requests library to make HTTP requests (e.g., fetching data from APIs) Used here for getting weather updates and much more
import pythoncom  # Importing pythoncom to handle COM (Component Object Model) operations, required for interacting with Windows services e.g Windows Search API
import win32com.client  # Importing win32com.client to create and manage COM objects, often used for automating Windows applications. These both are used for searching and opening files
import screen_brightness_control as sbc  # Importing screen_brightness_control to adjust the screen brightness on a Windows system
import re  # Importing re (regular expressions) to search, match, and manipulate text patterns (e.g., extracting numbers from voice commands) used in brightness and volume control 
import pyautogui  # Importing pyautogui to control the mouse and keyboard, allowing for GUI automation (e.g., clicking buttons, typing text)
# import speedtest # Importing speedtest to measure internet speed (download/upload) and ping time
# import pywhatkit as pwk # for whatsapp messaging 
# Importing the pycaw library, which allows control of the Windows audio system
#import pycaw
# 'ctypes' is a Python library for interacting with C-compatible data types. C-compatible data types are data types that follow the same structure, size, and memory layout as defined in the C programming language which is required as windows is developed in C and C++
# 'cast' is used to convert one pointer type to another. cast is a function from the ctypes module in Python. It is used to convert (or cast) a data type or object to a specific C-compatible type, especially pointers to structures or interfaces — just like casting in C or C++.
# 'POINTER' is used to define pointer types to COM interfaces.
from ctypes import cast, POINTER
# COM (Component Object Model) is a Microsoft technology that enables software components to communicate with each other.
# A COM interface is essentially a contract between software components. It defines a set of methods that a COM object must implement.
# A COM interface is essentially a contract between software components. It defines a set of methods that a COM object must implement.
# 'comtypes' is a package for defining and calling COM interfaces in Windows.
# 'CLSCTX_ALL' is a constant specifying the context in which the COM object is activated.
# Here, it allows accessing the audio endpoint in all available contexts (in-process, out-of-process, etc.)
from comtypes import CLSCTX_ALL
# Importing classes from pycaw to access audio devices and control their volume
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# - AudioUtilities: Provides functions to get all active audio devices.
# - IAudioEndpointVolume: Interface that gives access to volume settings of an audio endpoint (e.g., your speaker).
from volume_control import init_volume_control, process_volume_command

# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
init_volume_control()

def speak(text):
    """Converts text to speech and speaks it aloud."""
    engine.say(text)
    print(text)
    engine.runAndWait()

def listen():
    """Listens to user input via the microphone and returns recognized speech as text."""
    try:
        with sr.Microphone() as mic:  # Using the system's microphone
            print("Listening...")
            recognizer.adjust_for_ambient_noise(mic, duration=0.5)  # Reduce background noise
            audio = recognizer.listen(mic)  # Capture audio
            command = recognizer.recognize_google(audio).lower()  # Convert speech to text
            print(f"You said: {command}")
            return command
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand.")  # If speech is unclear
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")  # If there's an issue with the API
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None    
    
def greet_the_user():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning! How can I help you today?")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon! How can I help you today?")
    else:
        speak("Good Evening! How can I help you today?")


def proper_case(name):
    """
    Capitalize the first letter of each word, handling special cases
    """
    # Split the name into words
    words = name.split()
    
    # Capitalize each word
    capitalized_words = [word.capitalize() for word in words]
    
    # Join the words back together
    return ' '.join(capitalized_words)

def get_time():
    """Gets and speaks the current time."""
    now = datetime.datetime.now().strftime("%I:%M %p")  # Format: HH:MM AM/PM
    speak(f"The time is {now}")

""" def open_website(url, site_name):
    Opens a given website URL in the default web browser.
    speak(f"Opening {site_name}")
    webbrowser.open(url)  # Opens the website """

def take_screenshot():
    """Takes a screenshot and saves it to the current directory."""
    screenshot = pyautogui.screenshot()  # Take a screenshot
    path = "D:\\SSofVoiceAssistant"  # Directory to save the screenshot
    if not os.path.exists(path):  # Check if the directory exists
        os.makedirs(path, exist_ok=True)
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y-%m-%d')}.png"
    try:
        screenshot.save(f"{path}\\{filename}")  # Save the screenshot with a timestamp
        speak("Screenshot taken successfully!")
    except Exception as e:
        speak("Failed to take screenshot.")
        print("Error:", e)

def check_internet_connection():
    """Checks if the internet connection is available."""
    try:
        response = requests.get("http://www.google.com", timeout=5)    # Trying to connect to Google to check if internet is available
        # If the response is successful (status code 200), it means internet is available
        if response.status_code == 200:
            speak(f"You are connected to {get_wifi_name()} ")
            return True
        else:
            speak("Unable to reach the internet.")
            return False
    except requests.ConnectionError:
        speak("No internet connection. Please check your network settings.")
        return False

def calculate_distance():
    geocoder = Nominatim(user_agent="Shayan Mirza")  # Initialize geocoder

    speak("Tell me the first city name?")
    location1 = listen()
    speak("Tell me the second city name?")
    location2 = listen()

    coordinates1 = geocoder.geocode(location1)
    coordinates2 = geocoder.geocode(location2)

    if coordinates1 is None or coordinates2 is None:
        speak("Sorry, I couldn't find one of the locations.")
        return

    lat1, long1 = coordinates1.latitude, coordinates1.longitude
    lat2, long2 = coordinates2.latitude, coordinates2.longitude

    place1 = (lat1, long1)
    place2 = (lat2, long2)

    distance_km = geodesic(place1, place2).km
    rounded_distance = round(distance_km)

    speak(f"The distance between {location1.title()} and {location2.title()} is {rounded_distance} kilometers.")

def get_wifi_name():
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
        for line in result.split("\n"):
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
                return ssid
        return "Wi-Fi not connected"
    except Exception as e:
        return f"Error getting Wi-Fi name: {e}"
    
def tell_joke():
    """Fetches and speaks a random joke."""
    joke = pyjokes.get_joke()  # Get a random joke
    speak(joke)  # Speak the joke aloud

    """ def check_internet_speed():
    st = Speedtest()  # Create a Speedtest object
    speak("Wait!! I am checking your Internet Speed...")
    dw_speed = st.download()
    up_speed = st.upload()
    dw_speed = dw_speed / 1000000
    up_speed = up_speed / 1000000
    speak(f'Your download speed is {round(dw_speed, 3)} Mbps')
    speak(f'Your upload speed is {round(up_speed, 3)} Mbps')     
  """
def search_wikipedia(command):
    """Search Wikipedia based on a flexible user command."""
    
    # More comprehensive regex pattern to capture search terms
    patterns = [
        r"(?:search|find|look up|tell me about)\s*(?:on|for)?\s*wikipedia\s*(?:about|for)?\s*(.*)",
        r"wikipedia\s*(?:search|find|look up)\s*(?:about|for)?\s*(.*)",
        r"(?:search|find|look up)\s*(.*?)\s*(?:on|in)?\s*wikipedia"
    ]
    
    query = None
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            break
    
    if query:
        cap_query = proper_case(query)
        print(f"Searching Wikipedia for: {cap_query}")
        try:
            search_results = wikipedia.search(cap_query)
            if search_results:
                best_match = search_results[0]  # Take the first match
                result = wikipedia.summary(best_match, sentences=3)  # Fetch summary
                speak(f"According to Wikipedia, {result}")
            else:
                speak("No relevant results found on Wikipedia.")
        except wikipedia.exceptions.DisambiguationError as e:
            speak(f"Multiple matches found. Try being more specific. Some options: {', '.join(e.options[:3])}")
        except wikipedia.exceptions.PageError:
            # Attempt fuzzy matching or suggest similar terms
            suggestions = wikipedia.search(cap_query)
            if suggestions:
                speak(f"No exact match found on wikipedia. Did you mean: {suggestions[0]}? Yes or No")
                ans = listen()
                if "yes" in command:
                    result = wikipedia.summary(suggestions[0], sentences= 3)
                elif "no" in command:
                    speak("No information found on wikipedia.")
                else:
                    speak("Wrong command given!")
            else:
                speak("Could not find any Wikipedia information on this topic.")
        except Exception as er:
            speak("Oops! Some error occured.")
    else:
        speak("Could not extract a search query. Please try again.")


def search_windows_index(query):
    pythoncom.CoInitialize()  # initializes the COM library, which is required when using Windows COM-based APIs.
# COM (Component Object Model) is a Microsoft technology that allows interaction with system components like Windows Search API.
    try:
        conn = win32com.client.Dispatch("ADODB.Connection") # Creates a connection to the Windows Search Index. A database connection
        conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';") # specifies that we are using the Windows Search Provider.

        rs_tuple = conn.Execute(f"SELECT System.ItemPathDisplay FROM SystemIndex WHERE System.FileName LIKE '%{query}%'") # This is an SQL query to search the window index
# System.ItemPathDisplay → Fetches the full path of matching files.
# SystemIndex → Represents the Windows Search database.
# System.FileName LIKE '%{query}%' → Searches for partial matches in file names.
        # Fix: Extract the Recordset from the tuple
        rs = rs_tuple[0]  # rs_tuple[0] is the actual Recordset object
# conn.Execute returns a tuple in which the first element is the actual record set object so we extract it using rs_tuple[0]
# A Recordset object is a container that holds the results of a database query. It acts like a virtual table that allows us to access and manipulate rows and columns from a database query.
        results = []
        while not rs.EOF:  # EOF: End of File
            results.append(rs.Fields.Item("System.ItemPathDisplay").Value)  
            rs.MoveNext()

        rs.Close()
        conn.Close()

        return results if results else None

    except Exception as e:
        print(f"Error in Windows Search: {e}")
        return None


def open_item():
    """Listen for a file name, search, and open it."""
    speak("What do you want to open?")
    name = listen()
    if name:
        speak(f"Searching for {name}. Please wait...")
        results = search_windows_index(name)

        if results:
            file_path = results[0]  # Open the first matched file
            try:
                os.startfile(file_path)
                speak(f"Opening {name}")
            except Exception as e:
                speak(f"Failed to open {name}. Error: {e}")
        else:
            speak(f"No results found for {name}.")


important_websites = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "X": "https://X.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "wikipedia": "https://www.wikipedia.org",
    "linkedin": "https://www.linkedin.com",
    "spotify": "https://open.spotify.com",
    "zoom": "https://zoom.us",
    "reddit": "https://www.reddit.com",
    "github": "https://www.github.com",
    "coursera": "https://www.coursera.com",
    "udemy": "https://www.udemy.com",
    "fiverr": "https://www.fiverr.com",
    "upwork": "https://www.upwork.com"
}

def open_dynamic_website(command):
    """Opens any website and is called when command has website word in it."""
    command = command.lower()  # Convert to lowercase for easier matching

    # Remove common irrelevant words (like 'open', 'go to', 'search for')
    irrelevant_words = ['open', 'go to', 'search for', 'show me', 'visit', 'launch', 'website']
    site_name = command
    for word in irrelevant_words:
        site_name = site_name.replace(word, '')
    site_name = site_name.strip()
    if site_name:
        url = f"https://www.{site_name}.com"
        try:
            webbrowser.open(url)
            speak(f"Opening {site_name}")
        except Exception:
            speak("I couldn't open the website. Trying Google search instead.")
            search_url = f"https://www.google.com/search?q={site_name} site:.com"
            webbrowser.open(search_url)

def extract_website_name(command):
    command = command.lower()  # Convert to lowercase for easier matching

    # Remove common irrelevant words (like 'open', 'go to', 'search for')
    irrelevant_words = ['open', 'go to', 'search for', 'show me', 'visit', 'launch']
    for word in irrelevant_words:
        command = command.replace(word, '')

    # Find potential website names
    for site_name in important_websites:
        if site_name in command:
            return site_name

    return None  # No match found 

def open_common_website(command):
    """It opens the most common websites"""
    command = command.strip()  # Clean the command remove the spaces in start and end of the command

    for site_name in important_websites:
        if site_name in command:
            webbrowser.open(important_websites[site_name])
            print(f"Opening {site_name.capitalize()}...")
            return

    print("Website not recognized. Please try again.")

def weather_info():
    base_url = "http://api.openweathermap.org/data/2.5/weather?" # URL for the open weather website
    api_key = "f93374b6ea693452a274ec862e0e1bb6"  # Required for authentication when making requests to Open Weather
    speak("Tell the name of city whose weather you want to search: ")
    city = listen()
    def Temp_conv(kelvin):
        celsius = kelvin - 273.15
        fah = celsius * (9/5) + 32
        return round(celsius), round(fah)  # Round values to 2 decimal places
    url = base_url + "appid=" + api_key + "&q=" + city  # Constructs sthe final URL to get weather updates for the said city

    try:
        response = requests.get(url).json()
# The program sends an HTTP request using requests.get(url).
# Converts the response into a Python dictionary using .json().

        if response.get("cod") != 200:
            speak(f"Error: {response.get('message', 'Invalid request')}")
            return
# The API returns a cod (code) in the response:
# If cod == 200, the request is successful.
# Otherwise, an error message (e.g., "city not found") is returned and spoken.

# As response is now a dictionary so it has key value pairs. It has separate dictionaries inside it also like main is a dictionary likewise wind is a separate dictionary having keys whose names are temp, speed and humidity etc
        temp_kelv = response['main']['temp']
        temp_cel, temp_fah = Temp_conv(temp_kelv)
        description = response['weather'][0]['description']
        humidity = response['main']['humidity']
        wind_speed = response['wind']['speed']
        visibility = response.get('visibility', 'N/A')
        cloudiness = response['clouds']['all']
        rain_chance = response.get('rain', {}).get('1h', 0)  # Rain in last 1 hour (mm)
        snow_chance = response.get('snow', {}).get('1h', 0)  # Snow in last 1 hour (mm)

        if rain_chance:
            rain_prob = min(100, int(rain_chance * 10))  # Approximate % probability
        else:
            rain_prob = 0
# If 1 mm of rain fell → Assume 10% chance of rain.
# If 5 mm of rain fell → Assume 50% chance of rain.
# Uses min(100, value), so it never exceeds 100%
        if snow_chance:
            snow_prob = min(100, int(snow_chance * 10))
        else:
            snow_prob = 0
        #next_weather = response['list'][2]  # 6 hours later
        #expected_description = next_weather['weather'][0]['description']

        weather_report = (
            f"{city} has {description}. "
            f"The temperature feels like {temp_cel}°C ({temp_fah}°F). "
            f"Humidity is at {humidity}%, and wind speed is {wind_speed} meter per second. "
            f"Visibility is {visibility} meters. "
            f"Cloud coverage is {cloudiness}%. "
            f"Chance of rain is {rain_prob}%. "
            f"Chance of snow is {snow_prob}%. "
         #   f"It is expected {expected_description}"
        )

        speak(weather_report)
    except requests.exceptions.RequestException as e:
        speak(f"Network error: {e}")
    except TypeError as er:
        speak("No city name was recognized.")

def get_current_brightness():
    try:
        return sbc.get_brightness(display=0)[0]      # Returns the current brightness
    except Exception as e:
        speak("Could not retrieve brightness.")     # Notify user of error and return nothing
        return None
    
def set_brightness(level):
    """Adjust screen brightness to the given level."""
    try:
        sbc.set_brightness(level)  # Set screen brightness using screen_brightness_control
        speak(f"Brightness set to {level} percent.")  # Notify user via voice feedback
    except Exception as e:  # Catch any errors (e.g., unsupported system)
        speak("Failed to set brightness.")  # Inform user of failure
        print(f"Error: {e}")  # Print the error message for debugging

def extract_brightness_level(command):
    """Extract the brightness level from a voice command."""
    numbers = re.findall(r'\d+', command)  # Find all numbers in the command
    if numbers:  # If a number is found
        level = int(numbers[0])  # Convert the first found number to an integer
        return max(0, min(level, 100))  # Ensure brightness stays between 0 and 100
    return None  # Return None if no number was found

def adjust_brightness(command):
    bright_increase_words = ["increase", "rise", "up", "raise", "illuminate", "improve", "add", "brighter", "bright", "high", "higher", "more", "enhance", "boost"]
    bright_decrease_words = ["decrease", "fall", "down", "lower", "substract", "dimmer", "dim", "low", "less", "reduce", "darken"]
    bright_set_words = [
        'set', 'adjust', 'change', 'make', 'put', 'switch to', 'move to',
        'fix at', 'turn to', 'brightness should be', 'brightness needs to be',
        'i want brightness at', 'brightness to be'
    ]
    check_brightness_words = ["what's the brightness", "current brightness", "brightness level", "tell me the brightness", "get brightness"]

    command = command.lower().strip()    # Converting the command to lower case and removing additional spaces to process it better
    current = get_current_brightness()
    if current is None:
        return

    level = extract_brightness_level(command)

    # Check for set brightness intent
    """              any keyword:
       Returns True if at least one element is True.
       Returns False if all elements are False or the iterable is empty."""
    if any(word in command for word in bright_set_words):
        if level is not None:
            sbc.set_brightness(level)
            speak(f"Set brightness to {level}%")
            #print(current)
        else:
            speak("Please specify a brightness level.")

    # Check for decrease brightness intent
    elif any(word in command for word in bright_decrease_words):
        new_level = max(current - (level if level is not None else 20), 0)
        sbc.set_brightness(new_level)
        speak(f"Decreased brightness to {new_level}%")
        #print(current)

    # Check for brightness query
    elif any(word in command for word in check_brightness_words):
        brightness = get_current_brightness()  # Replace with the actual method for getting brightness
        if brightness is not None:
            speak(f"The current brightness is {brightness} percent")
            return True
        speak("I couldn't determine the current brightness")
        return False
    
    # Check for increase brightness intent
    elif any(word in command for word in bright_increase_words):    # any keyword returns true or false depending upon the iterable object
        new_level = min(current + (level if level is not None else 20), 100)     # Brightness should not be greater than 100.
        sbc.set_brightness(new_level)
        speak(f"Increased brightness to {new_level}%")
        #print(current)
    

    else:
        speak("Brightness command not recognized.")

def telldate():
    today = datetime.datetime.today().strftime("%A, %d %B %Y")
    speak(f"Today is {today}")

def mathematics():
    pass

def tellnews():
    pass

def choose_your_own_greeting():
    pass

def choose_my_name():
    pass

def handle_command(command):
    """Processes and executes a given voice command."""
    if "hello" in command:
        speak("Hello! How can I help you?")
    #elif "time" in command:
     #   get_time()
    elif "search" in command and "wikipedia" in command:
        search_wikipedia(command)
    elif "open file" in command or "open folder" in command or "open application" in command or "open app" in command:
        open_item()
    elif "open" in command and "website" in command:
        open_dynamic_website(command)
    elif "weather" in command:
        weather_info()
    elif "date" in command or "time" in command:
        if "date" in command:
           telldate()
        if "time" in command:
           get_time()
    elif "internet" in command or "network" in command or "wifi" in command:
            check_internet_connection()
    elif "brightness" in command or "brighter" in command or "illuminate" in command or "lighten" in command:
        adjust_brightness(command)
    elif "screenshot" in command or "take a screenshot" in command:
        take_screenshot()
    elif "distance" in command:
        calculate_distance()
    elif any(word in command.lower() for word in ["volume", "sound level", "louder", "quieter", "mute"]):
        process_volume_command(command, speak)
    elif "open" in command and extract_website_name(command) in command:
        open_common_website(command)
    elif "exit" in command or "stop" in command:
        speak("Goodbye Shayan Mirza! You are the best!")
        return False  # Stop the program
    return True  # Continue listening

def main():
    """Main function to execute only one command and stop."""
    greet_the_user()
    command = listen()  # Listen for a command
    if command:
        handle_command(command)  # Execute the command
        return  # Exit after executing the first task

if __name__ == "__main__":
    main()