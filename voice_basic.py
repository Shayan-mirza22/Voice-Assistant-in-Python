import speech_recognition as sr  # Library for speech recognition
import pyttsx3  # Text-to-speech conversion
import webbrowser  # Opening URLs in a web browser
import datetime  # Getting current time and date
import wikipedia  # Searching and fetching summaries from Wikipedia
import os  # Operating system-related functions (file handling, directory access)
import subprocess  # Running system commands and opening applications
import shutil  # File and directory management
# from fuzzywuzzy import process  # Fuzzy string matching to handle variations in user input
# import threading  # Running background processes for performance optimization
import requests  # Importing the requests library to make HTTP requests (e.g., fetching data from APIs) Used here for getting weather updates and much more
import pythoncom  # Importing pythoncom to handle COM (Component Object Model) operations, required for interacting with Windows services e.g Windows Search API
import win32com.client  # Importing win32com.client to create and manage COM objects, often used for automating Windows applications. These both are used for searching and opening files
import screen_brightness_control as sbc  # Importing screen_brightness_control to adjust the screen brightness on a Windows system
import re  # Importing re (regular expressions) to search, match, and manipulate text patterns (e.g., extracting numbers from voice commands) used in brightness and volume control 
import pywhatkit as pwk # for whatsapp messaging 
# Initialize speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

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
    """Asks for a website name and attempts to open it in a browser."""
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
    command = command.strip()  # Clean the command

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
    """Adjust screen brightness based on a voice command."""
    level = extract_brightness_level(command)  # Extract brightness level from command
    if level is not None:  # If a valid brightness level is found
        set_brightness(level)  # Set screen brightness
    else:
        speak("No valid brightness level found.")  # Inform user if no valid number was found

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
    elif "brightness" in command:
        adjust_brightness(command)
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