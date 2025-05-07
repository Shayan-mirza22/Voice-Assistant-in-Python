import speech_recognition as sr  # Library for speech recognition
import pyttsx3  # Text-to-speech conversion

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