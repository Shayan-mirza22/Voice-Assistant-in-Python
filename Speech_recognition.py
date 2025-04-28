import speech_recognition as sr

# The core component of this library is the Recognizer class, which is used to recognize speech.

recognizer = sr.Recognizer()
# Important Methods of Recognizer Class
# recognizer.adjust_for_ambient_noise(source, duration=1) – Adjusts for background noise. Listens to background noise for 1 second. Adjusts noise filtering settings. Then, the actual recording begins.
# recognizer.record(source, duration=None) – Records audio.
# recognizer.recognize_google(audio) – Converts speech to text using Google Web Speech API.
# recognizer.recognize_sphinx(audio) – Uses CMU Sphinx (offline recognition).
# recognizer.recognize_ibm(audio, username, password) – Uses IBM Speech to Text.
# Used for real-time speech recognition from a microphone.

               # recognizer.listen()
#  Stops recording when the user stops speaking or after a pause.
#  Suitable for interactive conversations or continuous speech input.

# How It Works
# Listens to speech until a pause is detected.
# Stops automatically when the user stops talking.
# Captures only speech, ignoring silence.

# Capture audio from microphone
with sr.Microphone() as source:
    print("Say something...")
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source)
    print("Processing...")

# Convert speech to text
try:
    text = recognizer.recognize_google(audio)
    print("You said: " + text)
except sr.UnknownValueError:
    print("Sorry, could not understand the audio.")
except sr.RequestError:
    print("Could not request results, check your internet connection.")

# UnknownValueError: When speech is not understood.
# RequestError: When there’s no internet or API issues.
# WaitTimeoutError: If no speech is detected within the timeout period.