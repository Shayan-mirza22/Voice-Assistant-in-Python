# Basic Usage
import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()

# Text to be spoken
text = "Hello, how are you?"

# Pass the text to the engine
engine.say(text)
engine.runAndWait()

# Adjusting the spped of voice that how fast the assistant speaks
rate = engine.getProperty('rate')
print(f"Current rate: {rate}")  # Default is usually 200

engine.setProperty('rate', 100)  # Slow down
engine.say("This is slower speech.")
engine.runAndWait()

engine.setProperty('rate', 250)  # Speed up
engine.say("This is faster speech.")
engine.runAndWait()

# Changing the voice of assistant
# Retrieve available voices
voices = engine.getProperty('voices')
print(voices)

# Set the engine to use the first voice (typically male)
engine.setProperty('voice', voices[0].id)
engine.say("This is the male voice.")
engine.runAndWait()

# Set the engine to use the second voice (typically female)
engine.setProperty('voice', voices[1].id)
engine.say("This is the female voice.")
# Process and deliver the speech
engine.runAndWait()

# To adjust the volume
engine.setProperty('volume', 1.0)  # Max volume
engine.say("This is spoken at full volume.")
engine.runAndWait()
