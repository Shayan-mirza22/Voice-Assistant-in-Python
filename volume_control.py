# Required for interacting with low-level Windows audio APIs
from ctypes import cast, POINTER
# Initializes COM (Component Object Model) library for multimedia operations
from comtypes import CLSCTX_ALL, CoInitialize
# pycaw (Python Core Audio Windows Library) for managing system audio
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
# For printing detailed exception tracebacks (helps with debugging)
import traceback
# For extracting numbers (volume levels) from strings using regex
import re


def init_volume_control():
    """
    Initializes the audio endpoint volume interface to check if volume control is accessible.

    Returns:
    - True if initialization is successful, False otherwise.
    """
    """Test the connection to the audio system"""
    try:
        # Initialize COM to use system audio devices
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()      # Get default audio playback device (usually speakers)
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)     # Activate endpoint volume interface (for volume control)
        volume = cast(interface, POINTER(IAudioEndpointVolume))     # Convert the interface to a usable Python object
        current = volume.GetMasterVolumeLevelScalar()      # Check current volume (used here for testing connection)
        #print(f"Volume controller initialized. Current volume: {int(current * 100)}%")
        return True
    except Exception as e:
        print(f"Error initializing volume controller: {e}")
        return False

def get_volume():
    """Get current volume as percentage (0-100)"""
    try:
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        level = int(volume.GetMasterVolumeLevelScalar() * 100)      # Volume level is always returned between 0.0 to 1.0 so it is converted to % for efficient working
        return level
    except Exception as e:
        print(f"Error getting volume: {e}")
        return None

def set_volume(level):
    """
    Sets the system volume to a specific percentage.

    Parameters:
    - level: integer (0-100)

    Returns:
    - True if volume set successfully, False otherwise.
    """
    """Set volume to specified percentage (0-100)"""
    try:
        # Ensure valid level
        level = max(0, min(100, level))
        scalar = level / 100.0     # Convert to scaler in range 0-1
        
        # Initialize COM in this method call
        CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Debug output before change
        before = volume.GetMasterVolumeLevelScalar()
        print(f"Current volume before change: {int(before * 100)}%")
        
        # Set the volume
        volume.SetMasterVolumeLevelScalar(scalar, None)
        
        # Verify the change worked
        after = volume.GetMasterVolumeLevelScalar()
        print(f"Volume after change: {int(after * 100)}%")
        
        return True
    except Exception as e:
        print(f"Error setting volume to {level}%:")
        print(traceback.format_exc())
        return False

def increase_volume(amount=10):
    """Increase volume by specified amount"""
    current = get_volume()
    if current is not None:
        return set_volume(min(current + amount, 100))
    return False

def decrease_volume(amount=10):
    """Decrease volume by specified amount"""
    current = get_volume()
    if current is not None:
        return set_volume(max(current - amount, 0))
    return False

def mute(state=None):
    """
    Mutes (sets volume to 0%), unmutes (sets to 40%), or toggles the mute state.

    Parameters:
    - state (bool or None):
        - True: force mute
        - False: force unmute (sets volume to 40%)
        - None: toggle mute based on current volume

    Returns:
    - True if operation successful, False otherwise
    """
    """Mute (set volume to 0), unmute (set to 40%), or toggle"""
    try:
        current_volume = get_volume()

        if state is None:
            if current_volume == 0:
                return set_volume(40)
            else:
                return set_volume(0)
        elif state:  # Mute
            return set_volume(0)
        else:  # Unmute
            return set_volume(40)
    except Exception as e:
        print(f"Error in mute/unmute logic: {e}")
        return False

def extract_level(command):
    """Extract volume level from command"""
    match = re.search(r'(\d+)(\s*%)?', command)    # d part captures the numbers while the s part optionally captures 0s and extra spaces
    if match:
        return int(match.group(1))     # For capturing only the integer part of number not the signs like %
    return None

def process_volume_command(command, speak_func=None):
    """Process a volume-related voice command"""
    command = command.lower().strip()
    
    # Default speak function if none provided
    if speak_func is None:
        def speak_func(text):
            print(text)
    
    # Check for unmute commands
    if any(word in command for word in ["unmute", "unsilence"]):
        if mute(False):
            speak_func("Audio unmuted")
            return True
        speak_func("Failed to unmute audio")
        return False
    
    # Check for mute commands
    elif any(word in command for word in ["mute", "silence"]):
        if mute(True):
            speak_func("Audio muted")
            return True
        speak_func("Failed to mute audio")
        return False
    
    
    # Volume set keywords
    set_words = ["set", "adjust", "change", "make", "put", "switch to", "move to", 
                 "fix at", "turn to", "volume should be", "volume needs to be",
                 "i want volume at", "volume to be"]
    
    # Volume increase keywords  
    up_words = ["increase", "raise", "up", "louder", "boost", "volume up"]
    
    # Volume decrease keywords
    down_words = ["decrease", "down", "lower", "quieter", "reduce", "volume down"]

    check_words = ["what's the volume", "current volume", "volume level", "tell me the volume", "get volume"] # to check current status 

    
    # Extract volume level
    level = extract_level(command)
    
    # Process command types
    if any(word in command for word in set_words):
        if level is not None:
            if set_volume(level):
                speak_func(f"Volume set to {level}%")
                return True
            speak_func("Failed to set volume")
            return False
        speak_func("Please specify a volume level")
        return False
    
    elif any(word in command for word in up_words):
        amount = level if level is not None else 10
        if increase_volume(amount):
            new_level = get_volume()
            speak_func(f"Increased volume to {new_level}%")
            return True
        speak_func("Failed to increase volume")
        return False
    
    elif any(word in command for word in down_words):
        amount = level if level is not None else 10
        if decrease_volume(amount):
            new_level = get_volume()
            speak_func(f"Decreased volume to {new_level}%")
            return True
        speak_func("Failed to decrease volume")
        return False
    # Check for volume query
    elif any(word in command for word in check_words):
        level = get_volume()
        if level is not None:
            speak_func(f"The current volume is {level} percent")
            return True
        speak_func("I couldn't determine the current volume")
        return False

    speak_func("Volume command not recognized")
    return False


# Test functions if this module is run directly
if __name__ == "__main__":
    # Initialize
    init_volume_control()
    
    # Test basic volume operations
    print("\nTesting volume control:")
    current = get_volume()
    print(f"Current volume: {current}%")
    
    print("\nSetting to 30%...")
    set_volume(30)
    
    print("\nIncreasing by 20%...")
    increase_volume(20)
    
    print("\nDecreasing by 10%...")
    decrease_volume(10)
    
    # Test command processing
    print("\nTesting command processor:")
    test_commands = [
        "set volume to 50 percent",
        "increase volume by 10",
        "decrease volume",
        "mute the sound",
        "unmute"
    ]
    
    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        process_volume_command(cmd)
        print(f"Current volume: {get_volume()}%")