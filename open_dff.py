"""
Windows Voice Assistant Folder Navigator
========================================

This module provides functions to open commonly used Windows folders through voice commands.
It supports opening user folders (Desktop, Documents, Downloads, etc.), system drives (C:, D:, etc.),
and important system folders.

Dependencies:
- os (built-in)
- subprocess (built-in) 
- winreg (built-in on Windows)

Usage:
Simply call open_folder_by_voice(command) with a voice command string.
Example: open_folder_by_voice("open downloads")
"""

import os
import subprocess
import winreg


def get_all_windows_drives():
    """
    Get all available drives on the Windows system.
    
    Returns:
        dict: Dictionary mapping drive names to their paths
              Format: {'drive_c': 'C:\\', 'drive_d': 'D:\\', etc.}
    
    Example:
        drives = get_all_windows_drives()
        # Returns: {'drive_c': 'C:\\', 'drive_d': 'D:\\', 'drive_e': 'E:\\'}
    """
    drives = {}
    
    # Check all possible drive letters from A to Z
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = f"{letter}:\\"
        
        # Check if the drive exists and is accessible
        if os.path.exists(drive_path):
            # Add multiple naming variations for each drive
            drives[f"drive_{letter.lower()}"] = drive_path
            drives[f"local_disk_{letter.lower()}"] = drive_path
            drives[f"{letter.lower()}_drive"] = drive_path
            drives[letter.lower()] = drive_path  # Simple letter access like 'c', 'd'
    
    return drives


def get_user_profile_folders():
    """
    Get all user profile folders (Desktop, Documents, Downloads, etc.).
    
    Returns:
        dict: Dictionary mapping folder names to their full paths
    
    Example:
        folders = get_user_profile_folders()
        # Returns: {'desktop': 'C:\\Users\\Username\\Desktop', 'documents': '...', etc.}
    """
    # Get the current user's profile directory
    user_profile = os.path.expanduser("~")     # Returns the path to home directory e.g C:\Users\Shayan
    
    # Define all common user folders
    user_folders = {
        "desktop": os.path.join(user_profile, "Desktop"),
        "documents": os.path.join(user_profile, "Documents"),
        "downloads": os.path.join(user_profile, "Downloads"),
        "pictures": os.path.join(user_profile, "Pictures"),
        "music": os.path.join(user_profile, "Music"),
        "videos": os.path.join(user_profile, "Videos"),
        "onedrive": os.path.join(user_profile, "OneDrive"),
        
        # Alternative names for the same folders
        "my_documents": os.path.join(user_profile, "Documents"),
        "my_pictures": os.path.join(user_profile, "Pictures"),
        "my_music": os.path.join(user_profile, "Music"),
        "my_videos": os.path.join(user_profile, "Videos"),
        "download": os.path.join(user_profile, "Downloads"),  # Singular form
        "document": os.path.join(user_profile, "Documents"),  # Singular form
        "picture": os.path.join(user_profile, "Pictures"),   # Singular form
        "video": os.path.join(user_profile, "Videos"),       # Singular form
        "movies": os.path.join(user_profile, "Videos"),      # Alternative name
        "photos": os.path.join(user_profile, "Pictures"),    # Alternative name
        
        # User profile itself
        "profile": user_profile,
        "user_profile": user_profile,
        "home": user_profile,
    }
    
    return user_folders


def get_system_folders():
    """
    Get important Windows system folders.
    
    Returns:
        dict: Dictionary mapping system folder names to their paths
    
    Example:
        folders = get_system_folders()
        # Returns: {'program_files': 'C:\\Program Files', 'windows': 'C:\\Windows', etc.}
    """
    user_profile = os.path.expanduser("~")
    
    system_folders = {
        # Program installation directories
        "program_files": "C:\\Program Files",
        "program_files_x86": "C:\\Program Files (x86)",
        "programs": "C:\\Program Files",  # Alternative name
        "software": "C:\\Program Files",  # Alternative name
        "apps": "C:\\Program Files",      # Alternative name
        
        # Windows system directories
        "windows": "C:\\Windows",
        "system32": "C:\\Windows\\System32",
        "system_32": "C:\\Windows\\System32",  # Alternative naming
        
        # Temporary and cache directories
        "temp": os.environ.get("TEMP", "C:\\Windows\\Temp"),
        "temporary": os.environ.get("TEMP", "C:\\Windows\\Temp"),
        
        # User application data
        "appdata": os.path.join(user_profile, "AppData"),
        "app_data": os.path.join(user_profile, "AppData"),
        "roaming": os.path.join(user_profile, "AppData", "Roaming"),
        "local": os.path.join(user_profile, "AppData", "Local"),
        
        # Startup folder - programs that start with Windows
        "startup": os.path.join(user_profile, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup"),
        
        # Recycle Bin (Note: This may not be accessible in all cases)
        "recycle_bin": "C:\\$Recycle.Bin",
        "trash": "C:\\$Recycle.Bin",
    }
    
    return system_folders


def get_special_windows_folders():
    """
    Get special Windows folders from the registry (Recent, Favorites, etc.).
    These folders are dynamically determined by Windows.
    
    Returns:
        dict: Dictionary mapping special folder names to their paths
        
    Note:
        This function safely handles registry access errors and returns an empty
        dict if registry access fails.
    """
    special_folders = {}
    
    try:
        # Access the Windows Shell Folders registry key
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            i = 0
            # Enumerate all values in the registry key
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    folder_name = name.lower()
                    
                    # Only include commonly useful special folders
                    if folder_name in ["recent", "favorites", "sendto", "cookies", "history"]:
                        special_folders[folder_name] = value
                        
                        # Add alternative names
                        if folder_name == "recent":
                            special_folders["recent_files"] = value
                        elif folder_name == "favorites":
                            special_folders["bookmarks"] = value
                    
                    i += 1
                    
                except WindowsError:
                    # No more registry values to read
                    break
                    
    except Exception as e:
        # Registry access failed - this is not critical, just return empty dict
        print(f"Note: Could not access special folders from registry: {e}")
    
    return special_folders


def get_all_folder_mappings():
    """
    Get a complete mapping of all available folders on the Windows system.
    This combines user folders, drives, system folders, and special folders.
    
    Returns:
        dict: Complete dictionary mapping folder names to their paths
        
    Example:
        all_folders = get_all_folder_mappings()
        # Returns a dict with all available folders: drives, user folders, system folders, etc.
    """
    all_folders = {}
    
    # Combine all folder types
    all_folders.update(get_user_profile_folders())    # Update is used to update the dict with a new key value pair
    all_folders.update(get_all_windows_drives())
    all_folders.update(get_system_folders())
    all_folders.update(get_special_windows_folders())
    
    return all_folders


def normalize_folder_command(command):
    """
    Normalize and clean up voice command input to match folder names.
    
    Args:
        command (str): Raw voice command input
        
    Returns:
        str: Cleaned and normalized folder name
        
    Example:
        normalized = normalize_folder_command("Open Downloads Folder")
        # Returns: "downloads"
    """
    # Convert to lowercase and strip whitespace
    command = command.lower().strip()
    
    # Remove common voice command prefixes
    prefixes_to_remove = [
        "open", "show", "go to", "navigate to", "open up", "take me to",
        "show me", "display", "launch", "start", "access", "browse"
    ]
    
    for prefix in prefixes_to_remove:
        if command.startswith(prefix + " "):
            command = command[len(prefix):].strip()
            break
    
    # Remove common suffixes
    suffixes_to_remove = ["folder", "directory", "drive", "files"]
    
    for suffix in suffixes_to_remove:
        if command.endswith(" " + suffix):
            command = command[:-len(suffix)].strip()
            break
    
    # Replace spaces with underscores for consistency
    command = command.replace(" ", "_")
    
    # Handle common alternative phrasings
    command_aliases = {
        # Drive aliases
        "c_disk": "c",
        "d_disk": "d",
        "local_c": "c",
        "local_d": "d",
        "hard_drive_c": "c",
        "hard_drive_d": "d",
        
        # Folder aliases
        "my_computer": "c",  # Often people say "my computer" meaning C drive
        "this_pc": "c",
        "computer": "c",
        "main_drive": "c",
        
        # User folder aliases
        "downloads_folder": "downloads",
        "documents_folder": "documents",
        "pictures_folder": "pictures",
        "desktop_folder": "desktop",
        "music_folder": "music",
        "videos_folder": "videos",
    }
    
    # Apply aliases if found
    if command in command_aliases:
        command = command_aliases[command]
    
    return command


def open_folder(folder_path):
    """
    Open a folder using the Windows file explorer.
    
    Args:
        folder_path (str): Full path to the folder to open
        
    Returns:
        tuple: (success: bool, message: str)
               success indicates if the operation was successful
               message contains success/error information
               
    Example:
        success, message = open_folder("C:\\Users\\Username\\Downloads")
        if success:
            print("Folder opened successfully")
        else:
            print(f"Failed to open folder: {message}")
    """
    # Check if the folder path exists
    if not os.path.exists(folder_path):
        return False, f"Folder does not exist: {folder_path}"
    
    # Check if it's actually a directory
    if not os.path.isdir(folder_path):
        return False, f"Path is not a directory: {folder_path}"
    
    try:
        # Use Windows startfile to open the folder in Explorer
        # This is the Windows-specific way to open folders
        os.startfile(folder_path)
        return True, f"Successfully opened folder: {folder_path}"
        
    except Exception as e:
        # If startfile fails, try using subprocess with explorer.exe
        try:
            subprocess.run(["explorer", folder_path], check=True)
            return True, f"Successfully opened folder: {folder_path}"
        except Exception as e2:
            return False, f"Failed to open folder: {str(e)} (also tried explorer: {str(e2)})"


def open_folder_by_voice(voice_command):
    """
    Main function to open folders based on voice commands.
    This is the primary function you'll call from your voice assistant.
    
    Args:
        voice_command (str): Voice command string (e.g., "open downloads", "show desktop")
        
    Returns:
        tuple: (success: bool, message: str)
               success indicates if the folder was opened successfully
               message contains detailed information about the result
               
    Example:
        success, message = open_folder_by_voice("open downloads folder")
        print(message)  # Will print success or error message
        
        # More examples:
        open_folder_by_voice("show desktop")
        open_folder_by_voice("go to C drive")
        open_folder_by_voice("navigate to documents")
        open_folder_by_voice("open pictures")
    """
    # Get all available folder mappings
    folder_mappings = get_all_folder_mappings()
    
    # Normalize the voice command
    normalized_command = normalize_folder_command(voice_command)
    
    # Check if the normalized command matches any folder
    if normalized_command in folder_mappings:
        folder_path = folder_mappings[normalized_command]
        
        # Attempt to open the folder
        success, message = open_folder(folder_path)
        
        if success:
            return True, f"Opened {normalized_command}: {message}"
        else:
            return False, f"Could not open {normalized_command}: {message}"
    else:
        # Folder not found - provide helpful suggestions
        available_folders = sorted(folder_mappings.keys())
        
        # Try to find similar folder names (simple substring matching)
        suggestions = [name for name in available_folders if normalized_command in name or name in normalized_command]
        
        error_message = f"Unknown folder: '{normalized_command}'"
        
        if suggestions:
            error_message += f". Did you mean: {', '.join(suggestions[:5])}?"
        else:
            error_message += f". Available folders include: {', '.join(available_folders[:10])}..."
        
        return False, error_message


def get_available_folders_list():
    """
    Get a formatted list of all available folders that can be opened.
    Useful for showing users what folders are available.
    
    Returns:
        str: Formatted string listing all available folders
        
    Example:
        print(get_available_folders_list())
        # Prints a nice formatted list of all available folders
    """
    folder_mappings = get_all_folder_mappings()
    
    # Group folders by type for better organization
    user_folders = []
    drives = []
    system_folders = []
    special_folders = []
    
    for name, path in sorted(folder_mappings.items()):
        if name.startswith(('drive_', 'local_disk_')) or name in 'abcdefghijklmnopqrstuvwxyz':
            drives.append(name)
        elif 'desktop' in name or 'documents' in name or 'downloads' in name or 'pictures' in name or 'music' in name or 'videos' in name:
            user_folders.append(name)
        elif name in ['recent', 'favorites', 'sendto', 'bookmarks']:
            special_folders.append(name)
        else:
            system_folders.append(name)
    
    # Format the output
    result = "Available Folders:\n"
    result += "=" * 50 + "\n\n"
    
    if user_folders:
        result += "User Folders:\n"
        for folder in sorted(set(user_folders)):
            result += f"  - {folder}\n"
        result += "\n"
    
    if drives:
        result += "Drives:\n"
        for drive in sorted(set(drives)):
            result += f"  - {drive}\n"
        result += "\n"
    
    if system_folders:
        result += "System Folders:\n"
        for folder in sorted(set(system_folders)):
            result += f"  - {folder}\n"
        result += "\n"
    
    if special_folders:
        result += "Special Folders:\n"
        for folder in sorted(set(special_folders)):
            result += f"  - {folder}\n"
    
    return result, user_folders, drives, system_folders, special_folders


def search_folders(search_term):
    """
    Search for folders containing the specified term.
    
    Args:
        search_term (str): Term to search for in folder names
        
    Returns:
        list: List of folder names that contain the search term
        
    Example:
        matches = search_folders("download")
        # Returns: ['downloads', 'download'] or similar matches
    """
    folder_mappings = get_all_folder_mappings()
    search_term = search_term.lower()
    
    matches = []
    for folder_name in folder_mappings.keys():
        if search_term in folder_name.lower():
            matches.append(folder_name)
    
    return sorted(matches)


# Example usage and testing functions
def test_folder_navigation():
    """
    Test function to demonstrate the folder navigation capabilities.
    This function is for testing purposes and shows example usage.
    """
    print("Windows Voice Assistant Folder Navigator Test")
    print("=" * 50)
    
    # Show all available folders
    print(get_available_folders_list())
    
    # Test some common voice commands
    test_commands = [
        "open downloads",
        "show desktop", 
        "go to documents",
        "open c drive",
        "navigate to pictures",
        "open music folder",
        "show program files",
        "go to temp",
    ]
    
    print("\nTesting Voice Commands:")
    print("-" * 30)
    
    for command in test_commands:
        print(f"\nCommand: '{command}'")
        success, message = open_folder_by_voice(command)
        status = "SUCCESS" if success else "FAILED"
        print(f"{status}: {message}")

""" 
if __name__ == "__main__":
    # Run the test when this file is executed directly
    test_folder_navigation()
    
    # Interactive testing
    print("\n" + "=" * 50)
    print("Interactive Mode (type 'quit' to exit, 'list' to show folders)")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nEnter voice command: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'list':
                print(get_available_folders_list())
            elif user_input.startswith('search '):
                search_term = user_input[7:]  # Remove 'search ' prefix
                matches = search_folders(search_term)
                if matches:
                    print(f"Found folders matching '{search_term}': {', '.join(matches)}")
                else:
                    print(f"No folders found matching '{search_term}'")
            else:
                success, message = open_folder_by_voice(user_input)
                print(message)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
 """

# Quick integration example for your voice assistant:
"""
To integrate into your voice assistant, simply use:

def handle_folder_command(voice_input):
    success, message = open_folder_by_voice(voice_input)
    if success:
        speak("Folder opened successfully")  # Your TTS function
    else:
        speak(f"Sorry, {message}")  # Your TTS function
    return success
"""