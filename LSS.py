# Import necessary libraries
import os  # For interacting with the operating system
import platform  # To detect the OS type (Windows, macOS, Linux)
import subprocess  # To run system commands e.g for shut down
import time  # For delays and timing
import psutil  # For interacting with running system processes. The psutil library in Python (short for process and system utilities) is used to monitor and manage system resources and running processes. It gives you detailed information about your computer's CPU, memory, disk, network, and more.
import signal  # For sending termination signals to processes
from collections import defaultdict  # For default dictionary behavior
from utilities import speak, listen  # Custom functions for speech output and input

# Function to lock the computer screen
def lock_computer():
    """Lock the computer screen"""
    system = platform.system()  # Get current OS name (Windows, Linux, Darwin for macOS)
    
    try:
        if system == "Windows":
            # Lock command for Windows
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)    # This locks the screen just like pressing Win+L. check=True makes sure Python will raise an error if the command fails.
            speak("Computer locked successfully")  # Announce success   
            return True  # Return True to indicate successful lock

        elif system == "Darwin":  # macOS. macOS doesn’t have a direct lock command like Windows. pmset displaysleepnow immediately puts the display to sleep, which effectively locks the screen if password on wake is enabled.
            # Lock command for macOS
            subprocess.run(["pmset", "displaysleepnow"], check=True)
            speak("Computer locked successfully")
            return True

        elif system == "Linux":      # Linux has many desktop environments, each with different lock commands. So this function tries them one by one until one works.
            # Try common lock commands for Linux systems
            try:
                subprocess.run(["gnome-screensaver-command", "-l"], check=True)  # GNOME. 
            except FileNotFoundError:
                try:
                    subprocess.run(["qdbus", "org.freedesktop.ScreenSaver", "/ScreenSaver", "Lock"], check=True)  # KDE
                except FileNotFoundError:
                    try:
                        subprocess.run(["i3lock"], check=True)  # i3 window manager
                    except FileNotFoundError:
                        try:
                            subprocess.run(["xdg-screensaver", "lock"], check=True)  # Generic Linux
                        except FileNotFoundError:
                            speak("Could not find a suitable lock command for your Linux system")  # If all fail
                            return False  # Return False on failure
            speak("Computer locked successfully")  # Announce success
            return True

        else:
            speak(f"Unsupported operating system: {system}")  # Inform if OS is unsupported
            return False  # Return False on unsupported OS

    except Exception as e:
        speak(f"Error locking computer: {e}")  # Announce error
        return False  # Return False if any exception occurs

# Function to put the computer to sleep
def sleep_computer():
    """Put the computer to sleep"""
    system = platform.system()  # Get OS name
    
    try:
        if system == "Windows":
            # Windows sleep command using PowerShell
            # It is just like : "Hey PowerShell, open the toolbox called System.Windows.Forms so I can use the sleep function inside it."
            subprocess.run([
                "powershell", 
                "-Command", 
                "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"
            ], check=True)
            """It's telling PowerShell to load the .NET library called System.Windows.Forms. It's a .NET Framework assembly used primarily for creating Windows GUI applications. Because the SetSuspendState method, which puts the computer to sleep, lives inside this assembly.By loading it with Add-Type, PowerShell gains access to that method."""
            """Calls SetSuspendState('Suspend', false, false) to put the PC to sleep (not hibernate or hybrid).
            'Suspend' → sleep
            $false → do not force apps to close
            $false → do not disable wake-up events"""
            speak("It's time to sleep")
            return True

        elif system == "Darwin":  # macOS
            subprocess.run(["pmset", "sleepnow"], check=True)  # Sleep command for macOS
            speak("Computer is going to sleep")
            return True

        elif system == "Linux":
            try:
                subprocess.run(["systemctl", "suspend"], check=True)  # Try systemd
            except FileNotFoundError:
                try:
                    subprocess.run(["pm-suspend"], check=True)  # Try pm-utils
                except FileNotFoundError:
                    try:
                        subprocess.run([
                            "dbus-send", "--system", "--print-reply", "--dest=org.freedesktop.UPower",
                            "/org/freedesktop/UPower", "org.freedesktop.UPower.Suspend"
                        ], check=True)  # Try dbus
                    except FileNotFoundError:
                        print("Could not find a suitable sleep command for your Linux system")
                        return False
            speak("Computer is going to sleep")
            return True

        else:
            speak(f"Unsupported operating system: {system}")
            return False

    except Exception as e:
        speak(f"Error putting computer to sleep: {e}")
        return False

# Function to confirm shutdown using voice or fallback input
def confirm_shutdown():
    """
    Ask for confirmation before shutting down the computer
    Returns:
        True if confirmed, False otherwise
    """
        # Default method using voice command
    speak("Say yes if you want to shut down your computer and otherwise say no: ")
    response = listen()  # Listen to user's voice
    return response in [  # Match response to known "yes" phrases
        "yes yes", "yes", "y", "true", "t", "1", "sure", "ok", "okay", 
        "affirmative", "confirm", "yes please", "yes indeed", 
        "absolutely", "definitely", "certainly", "yep", "yup", "yeah", "sure thing"
    ]    # return True if any of the phrases match, else return False

# Function to close all running applications
def close_all_applications():
    """
    Close all running applications
    Returns:
        dict: Summary of applications closed and failed to close
    """
    print("Attempting to close all running applications...")
    system = platform.system()  # Get current OS name

    results = {
        "closed": [],  # List of successfully closed apps
        "failed": []   # List of apps that failed to close
    }

    try:
        if system == "Windows":
            app_list = []  # Initialize app list

            try:
                import win32gui     # Tries to import pywin32 modules to access Windows GUI features.
                import win32process
                import win32con

                # Callback function to enumerate windows
                def enum_windows_callback(hwnd, apps):     # hwnd stands for handle to a window. It's a unique identifier (a number) that Windows assigns to every open window (including GUI apps, dialog boxes, etc.).
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):     # win32gui.IsWindowVisible(hwnd) --> Returns True if the window is visible on screen.  # win32gui.GetWindowText(hwnd) Returns the title of the window (as a string). If the window has no title, it returns an empty string.
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        """GetWindowThreadProcessId(hwnd) returns a tuple:
                            (thread_id, process_id) of the window.
                            We only need process_id so insert _ to ignore thread_id."""
                        try:
                            proc = psutil.Process(pid)      # Creates a Process object that allows inspection of the app running with that process ID.
                            app_name = proc.name()       # Returns the name of the executable, like chrome.exe, notepad.exe, etc.
                            if app_name.lower() not in ["explorer.exe", "taskmgr.exe", "cmd.exe", 
                                                        "python.exe", "pythonw.exe"]:
                                apps.append((pid, app_name, hwnd))  # Add app to list
                        except:
                            pass
                    return True

                apps = []
                win32gui.EnumWindows(enum_windows_callback, apps)  # Get all windowed apps
                app_list = apps     # Collects all open app windows and stores them in app_list.

                # Try to close each application
                for pid, app_name, hwnd in app_list:
                    try:
                        print(f"Closing {app_name} (PID: {pid})...")
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)  # Attempt to Gracefully Close Each App. sends a message to the window to close it. This is like clicking the "X" button on the window.
                        time.sleep(0.5)  # Give time for graceful shutdown
                        if psutil.pid_exists(pid):  # If still running
                            proc = psutil.Process(pid)    # If the process is still running after the close request, forcibly terminates it and logs it as closed.
                            proc.terminate()  # Force close
                        results["closed"].append(app_name)
                    except Exception as e:
                        speak(f"Failed to close {app_name}: {e}")
                        results["failed"].append(app_name)

            except ImportError:
                # If pywin32 is not installed
                print("pywin32 not available, using basic process termination")
                for proc in psutil.process_iter(['pid', 'name']): # is a generator function from the psutil library that lets you iterate over all running processes on your system, efficiently and optionally with selected attributes.
                    # If pywin32 isn't installed, it just kills all user processes excluding important system ones.
                    try:
                        proc_info = proc.info
                        if proc_info['name'].lower() not in [
                            "explorer.exe", "taskmgr.exe", "cmd.exe", 
                            "python.exe", "pythonw.exe", "svchost.exe", 
                            "lsass.exe", "services.exe", "winlogon.exe",
                            "csrss.exe", "smss.exe", "dwm.exe"
                        ]:
                            print(f"Closing {proc_info['name']} (PID: {proc_info['pid']})...")
                            proc.terminate()     # Force close the process
                            results["closed"].append(proc_info['name'])
                    except Exception as e:
                        results["failed"].append(proc_info.get('name', f"PID:{proc_info.get('pid', 'unknown')}"))

        elif system == "Darwin":  # macOS
            try:
                # Get running apps using AppleScript
                cmd = "osascript -e 'tell application \"System Events\" to get name of every process where background is false'"
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
                apps = result.stdout.strip().split(", ")

                for app in apps:
                    if app.lower() in ["finder", "dock", "systemuiserver", "terminal"]:
                        continue  # Skip essential system apps
                    try:
                        print(f"Closing {app}...")
                        cmd = f"osascript -e 'tell application \"{app}\" to quit'"
                        subprocess.run(cmd, shell=True, check=True)
                        results["closed"].append(app)
                    except Exception as e:
                        speak(f"Failed to close {app}: {e}")
                        results["failed"].append(app)
            except Exception as e:
                print(f"Error getting application list: {e}")

        elif system == "Linux":
            try:
                cmd = "wmctrl -l"  # List windows
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

                if result.returncode == 0:
                    windows = result.stdout.strip().split('\n')
                    window_ids = [line.split()[0] for line in windows if line]

                    for win_id in window_ids:
                        try:
                            print(f"Closing window {win_id}...")
                            subprocess.run(["wmctrl", "-ic", win_id], check=True)
                            results["closed"].append(f"Window {win_id}")
                        except Exception as e:
                            results["failed"].append(f"Window {win_id}")
                else:
                    print("wmctrl not available, using basic process termination")
                    user_processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'username']):
                        try:
                            proc_info = proc.info
                            if proc_info['username'] == os.getlogin():
                                if proc_info['name'] not in [
                                    "bash", "sh", "python", "systemd", "kworker", 
                                    "sshd", "gnome-terminal", "konsole"
                                ]:
                                    user_processes.append(proc)
                        except:
                            pass

                    for proc in user_processes:
                        try:
                            print(f"Closing {proc.name()} (PID: {proc.pid})...")
                            proc.terminate()
                            results["closed"].append(proc.name())
                        except Exception as e:
                            results["failed"].append(proc.name())

            except Exception as e:
                speak(f"Error closing applications: {e}")

        time.sleep(2)  # Wait to ensure processes are terminated

        print(f"Attempted to close {len(results['closed'])} applications")  # Print summary
        if results["failed"]:
            speak(f"Failed to close {len(results['failed'])} applications")  # Speak failures

        return results  # Return final result with details

    except Exception as e:
        speak(f"Error closing applications: {e}")
        return {
            "closed": [],  # Empty result on total failure. Returns the summary dictionary or an error message in case of complete failure.
            "failed": ["Error occurred while closing applications: " + str(e)]
        }

# Function to confirm and shut down the computer
def shutdown_computer(close_apps=True):
    """
    Shut down the computer with confirmation
    
    Args:
        confirmation_func: Optional voice/input confirmation
        close_apps: If True, attempt to close all apps first
    
    Returns:
        True if shutdown started, False otherwise
    """
    speak("Say yes to confirm shutdown...")  # Ask user for confirmation
    if not confirm_shutdown():  # Check confirmation
        speak("Shutdown cancelled")  # Notify user
        return False  # Do not proceed

    if close_apps:
        close_all_applications()  # Try closing apps before shutdown

    try:
        system = platform.system()  # Detect OS
        if system == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "5"], check=True)  # Shutdown in 5 seconds
        elif system == "Darwin":
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)  # Shutdown macOS
        elif system == "Linux":
            subprocess.run(["shutdown", "now"], check=True)  # Shutdown Linux
        else:
            speak("Unsupported operating system for shutdown")  # Unsupported OS
            return False
        return True  # Return True on success
    except Exception as e:
        speak(f"Error shutting down computer: {e}")  # Notify user of error
        return False  # Return False on failure
