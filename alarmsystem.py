import datetime
import re
import time
import threading
import os
import platform
import subprocess
from dateutil import parser
from dateutil.relativedelta import relativedelta

def set_alarm(user_input, speak_function):
    """
    Parse the user input to extract time information and set an alarm.
    
    Args:
        user_input (str): The user's request to set an alarm
        speak_function: Your existing function to speak responses to the user
    
    Returns:
        bool: True if alarm was set successfully, False otherwise
    """
    # Extract time and date information from user input
    alarm_time = extract_time_from_input(user_input)
    
    if not alarm_time:
        speak_function("I couldn't understand the time for the alarm. Please try again.")
        return False
    
    # Check if the requested time has already passed
    now = datetime.datetime.now()
    if alarm_time < now:
        # If the time has passed, set it for tomorrow
        if "tomorrow" not in user_input.lower():
            alarm_time += datetime.timedelta(days=1)
            speak_function(f"The time you requested has already passed today. Setting the alarm for {format_time_for_speech(alarm_time)} tomorrow.")
    
    # Calculate seconds until alarm
    time_diff = (alarm_time - now).total_seconds()
    
    # Set the alarm
    threading.Thread(target=start_alarm, args=(time_diff, speak_function, alarm_time)).start()
    
    # Confirm to the user
    speak_function(f"Alarm set for {format_time_for_speech(alarm_time)}.")
    return True

def extract_time_from_input(user_input):
    """
    Extract time information from user input and return a datetime object.
    
    Args:
        user_input (str): The user's request
        
    Returns:
        datetime.datetime: The parsed alarm time, or None if parsing fails
    """
    user_input = user_input.lower()
    
    try:
        # Handle "tomorrow" specifically
        if "tomorrow" in user_input:
            # Remove the word "tomorrow" and parse the time
            time_str = user_input.replace("tomorrow", "")
            parsed_time = parser.parse(time_str, fuzzy=True)
            
            # Set to tomorrow's date
            tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
            alarm_time = datetime.datetime(
                tomorrow.year, 
                tomorrow.month, 
                tomorrow.day,
                parsed_time.hour,
                parsed_time.minute,
                0  # Seconds
            )
            return alarm_time
        
        # Handle specific time expressions
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm|a\.m\.|p\.m\.)?', user_input)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            # Handle AM/PM
            if period:
                if any(p in period.lower() for p in ['pm', 'p.m.']) and hour < 12:
                    hour += 12
                elif any(p in period.lower() for p in ['am', 'a.m.']) and hour == 12:
                    hour = 0
            elif hour < 12 and "evening" in user_input or "night" in user_input:
                hour += 12
                
            now = datetime.datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return alarm_time
        
        # Use dateutil parser as a fallback
        return parser.parse(user_input, fuzzy=True)
        
    except Exception as e:
        print(f"Error parsing time: {e}")
        return None

def format_time_for_speech(dt):
    """Format datetime object for natural speech output"""
    hour = dt.hour
    minute = dt.minute
    period = "AM" if hour < 12 else "PM"
    
    if hour > 12:
        hour -= 12
    elif hour == 0:
        hour = 12
        
    if minute == 0:
        return f"{hour} {period}"
    else:
        return f"{hour}:{minute:02d} {period}"

def start_alarm(seconds_to_wait, speak_function, alarm_time):
    """
    Wait for the specified time and then trigger the alarm.
    
    Args:
        seconds_to_wait (float): Seconds to wait before triggering alarm
        speak_function: Function to speak to the user
        alarm_time (datetime.datetime): The scheduled alarm time
    """
    # Wait until alarm time
    time.sleep(seconds_to_wait)
    
    # Announce the alarm
    speak_function(f"It's now {format_time_for_speech(alarm_time)}. Your alarm is ringing.")
    
    # Play the system default alarm sound
    play_alarm_sound()
    
def play_alarm_sound():
    """Play the default system alarm sound based on the OS"""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Play Windows default alarm sound
            import winsound
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            
            # Continue playing for a few times
            for _ in range(5):
                time.sleep(1)
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                
        elif system == "Darwin":  # macOS
            # Play macOS default alert sound
            subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"])
            
            # Continue playing for a few times
            for _ in range(5):
                time.sleep(1)
                subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"])
                
        elif system == "Linux":
            # Try to use paplay (PulseAudio) with a system sound
            # This might need adjustment based on the Linux distribution
            for _ in range(5):
                try:
                    subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"])
                    time.sleep(1)
                except FileNotFoundError:
                    # Try to use aplay if paplay is not available
                    try:
                        subprocess.run(["aplay", "/usr/share/sounds/alsa/Front_Center.wav"])
                        time.sleep(1)
                    except:
                        print("Could not play alarm sound. No compatible audio player found.")
                        break
    except Exception as e:
        print(f"Error playing alarm sound: {e}")

def process_alarm_command(user_input, speak_function, listen_function):
    """
    Process a user command related to alarms.
    
    Args:
        user_input (str): The user's command
        speak_function: Your function to speak to the user
        listen_function: Your function to listen to the user
        
    Returns:
        bool: True if this was an alarm-related command and was handled
    """
    # Check if this is an alarm-related command
    if "set alarm" in user_input.lower() or "wake me" in user_input.lower():
        set_alarm(user_input, speak_function)
        return True
        
    return False

# Example of how to integrate this with your main voice assistant loop:
"""
def main():
    while True:
        # Use your existing listen function
        user_input = listen_function()
        
        # Check if this is an alarm command
        if process_alarm_command(user_input, speak_function, listen_function):
            continue
            
        # Your existing voice assistant code for other commands
        # ...

if __name__ == "__main__":
    main()
"""