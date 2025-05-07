# Import necessary libraries
import os  # For interacting with the operating system
import platform  # To detect the OS type (Windows, macOS, Linux)
import subprocess  # To run system commands
import time  # For delays and timing
import psutil  # For interacting with running system processes
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
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            speak("Computer locked successfully")  # Announce success
            return True  # Return True to indicate successful lock

        elif system == "Darwin":  # macOS
            # Lock command for macOS
            subprocess.run(["pmset", "displaysleepnow"], check=True)
            speak("Computer locked successfully")
            return True

        elif system == "Linux":
            # Try common lock commands for Linux systems
            try:
                subprocess.run(["gnome-screensaver-command", "-l"], check=True)  # GNOME
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
            subprocess.run([
                "powershell", 
                "-Command", 
                "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"
            ], check=True)
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
def confirm_shutdown(confirmation_func=None):
    """
    Ask for confirmation before shutting down
    
    Args:
        confirmation_func: Optional function to get voice confirmation
    Returns:
        True if confirmed, False otherwise
    """
    if confirmation_func is None:
        # Default method using voice command
        speak("Say yes if you want to shut down your computer and otherwise say no: ")
        response = listen()  # Listen to user's voice
        return response in [  # Match response to known "yes" phrases
            "yes yes", "yes", "y", "true", "t", "1", "sure", "ok", "okay", 
            "affirmative", "confirm", "yes please", "yes indeed", 
            "absolutely", "definitely", "certainly", "yep", "yup", "yeah", "sure thing"
        ]
    else:
        return confirmation_func()  # Use custom confirmation function if provided

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
                import win32gui
                import win32process
                import win32con

                # Callback function to enumerate windows
                def enum_windows_callback(hwnd, apps):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            proc = psutil.Process(pid)
                            app_name = proc.name()
                            if app_name.lower() not in ["explorer.exe", "taskmgr.exe", "cmd.exe", 
                                                        "python.exe", "pythonw.exe"]:
                                apps.append((pid, app_name, hwnd))  # Add app to list
                        except:
                            pass
                    return True

                apps = []
                win32gui.EnumWindows(enum_windows_callback, apps)  # Get all windowed apps
                app_list = apps

                # Try to close each application
                for pid, app_name, hwnd in app_list:
                    try:
                        print(f"Closing {app_name} (PID: {pid})...")
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)  # Send close message
                        time.sleep(0.5)  # Give time for graceful shutdown
                        if psutil.pid_exists(pid):  # If still running
                            proc = psutil.Process(pid)
                            proc.terminate()  # Force close
                        results["closed"].append(app_name)
                    except Exception as e:
                        speak(f"Failed to close {app_name}: {e}")
                        results["failed"].append(app_name)

            except ImportError:
                # If pywin32 is not installed
                print("pywin32 not available, using basic process termination")
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_info = proc.info
                        if proc_info['name'].lower() not in [
                            "explorer.exe", "taskmgr.exe", "cmd.exe", 
                            "python.exe", "pythonw.exe", "svchost.exe", 
                            "lsass.exe", "services.exe", "winlogon.exe",
                            "csrss.exe", "smss.exe", "dwm.exe"
                        ]:
                            print(f"Closing {proc_info['name']} (PID: {proc_info['pid']})...")
                            proc.terminate()
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
            "closed": [],  # Empty result on total failure
            "failed": ["Error occurred while closing applications: " + str(e)]
        }

# Function to confirm and shut down the computer
def shutdown_computer(confirmation_func=None, close_apps=True):
    """
    Shut down the computer with confirmation
    
    Args:
        confirmation_func: Optional voice/input confirmation
        close_apps: If True, attempt to close all apps first
    
    Returns:
        True if shutdown started, False otherwise
    """
    speak("Say yes to confirm shutdown...")  # Ask user for confirmation
    if not confirm_shutdown(confirmation_func):  # Check confirmation
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
