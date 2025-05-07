import os
import platform
import subprocess
import time
import psutil
import signal
from collections import defaultdict
from utilities import speak, listen

def lock_computer():
    """Lock the computer screen"""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows lock command
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            speak("Computer locked successfully")
            return True
        elif system == "Darwin":  # macOS
            # macOS lock command
            subprocess.run(["pmset", "displaysleepnow"], check=True)
            speak("Computer locked successfully")
            return True
        elif system == "Linux":
            # Try common Linux lock commands
            try:
                # GNOME/Ubuntu
                subprocess.run(["gnome-screensaver-command", "-l"], check=True)
            except FileNotFoundError:
                try:
                    # KDE
                    subprocess.run(["qdbus", "org.freedesktop.ScreenSaver", "/ScreenSaver", "Lock"], check=True)
                except FileNotFoundError:
                    try:
                        # i3lock (for i3 window manager)
                        subprocess.run(["i3lock"], check=True)
                    except FileNotFoundError:
                        try:
                            # xdg-screensaver (generic)
                            subprocess.run(["xdg-screensaver", "lock"], check=True)
                        except FileNotFoundError:
                            speak("Could not find a suitable lock command for your Linux system")
                            return False
            speak("Computer locked successfully")
            return True
        else:
            speak(f"Unsupported operating system: {system}")
            return False
    except Exception as e:
        speak(f"Error locking computer: {e}")
        return False

def sleep_computer():
    """Put the computer to sleep"""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows sleep command
            subprocess.run(["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)"], check=True)
            speak("It's time to sleep")
            return True
        elif system == "Darwin":  # macOS
            # macOS sleep command
            subprocess.run(["pmset", "sleepnow"], check=True)
            speak("Computer is going to sleep")
            return True
        elif system == "Linux":
            # Try common Linux sleep commands
            try:
                # systemd
                subprocess.run(["systemctl", "suspend"], check=True)
            except FileNotFoundError:
                try:
                    # pm-utils
                    subprocess.run(["pm-suspend"], check=True)
                except FileNotFoundError:
                    try:
                        # dbus
                        subprocess.run(["dbus-send", "--system", "--print-reply", "--dest=org.freedesktop.UPower", "/org/freedesktop/UPower", "org.freedesktop.UPower.Suspend"], check=True)
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

def confirm_shutdown(confirmation_func=None):
    """
    Ask for confirmation before shutting down
    
    Args:
        confirmation_func: Function to get confirmation from user
                          Should return True for yes, False for no
                          If None, will use input() to get confirmation
    
    Returns:
        True if confirmed, False otherwise
    """
    if confirmation_func is None:
        # Default confirmation using input()

        speak("Say yes if you want to shut down your computer and otherwise say no: ")
        response = listen()
        return response in ["yes yes", "yes", "y", "true", "t", "1", "sure", "ok", "okay", "affirmative", "confirm", "yes please", "yes indeed", "absolutely", "definitely", "certainly", "yep", "yup", "yeah", "sure thing"]
    else:
        # Use custom confirmation function (e.g., voice recognition)
        return confirmation_func()

def close_all_applications():
    """
    Close all running applications
    
    Returns:
        dict: Summary of applications closed and failed to close
    """
    print("Attempting to close all running applications...")
    system = platform.system()
    
    # Track closed and failed apps
    results = {
        "closed": [],
        "failed": []
    }
    
    # Get list of running processes
    try:
        if system == "Windows":
            # Windows: Focus on user applications with window
            # This is a simplified approach - may not catch all apps
            app_list = []
            
            # Get list of running processes with windows
            try:
                import win32gui
                import win32process
                import win32con
                
                def enum_windows_callback(hwnd, apps):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            # Get process name
                            proc = psutil.Process(pid)
                            app_name = proc.name()
                            
                            # Skip system processes
                            if app_name.lower() not in ["explorer.exe", "taskmgr.exe", "cmd.exe", 
                                                        "python.exe", "pythonw.exe"]:
                                apps.append((pid, app_name, hwnd))
                        except:
                            pass
                    return True
                
                apps = []
                win32gui.EnumWindows(enum_windows_callback, apps)
                app_list = apps
                
                # Close each application
                for pid, app_name, hwnd in app_list:
                    try:
                        print(f"Closing {app_name} (PID: {pid})...")
                        # Try to send close message first
                        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        time.sleep(0.5)  # Give some time to close gracefully
                        
                        # Check if process still exists
                        if psutil.pid_exists(pid):
                            proc = psutil.Process(pid)
                            proc.terminate()  # More forceful
                            results["closed"].append(app_name)
                        else:
                            results["closed"].append(app_name)
                    except Exception as e:
                        speak(f"Failed to close {app_name}: {e}")
                        results["failed"].append(app_name)
                
            except ImportError:
                # Fall back to basic approach if pywin32 is not available
                print("pywin32 not available, using basic process termination")
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_info = proc.info
                        # Skip system processes
                        if proc_info['name'].lower() not in ["explorer.exe", "taskmgr.exe", "cmd.exe", 
                                                             "python.exe", "pythonw.exe", "svchost.exe", 
                                                             "lsass.exe", "services.exe", "winlogon.exe",
                                                             "csrss.exe", "smss.exe", "dwm.exe"]:
                            print(f"Closing {proc_info['name']} (PID: {proc_info['pid']})...")
                            proc.terminate()
                            results["closed"].append(proc_info['name'])
                    except Exception as e:
                        results["failed"].append(proc_info.get('name', f"PID:{proc_info.get('pid', 'unknown')}"))
                
        elif system == "Darwin":  # macOS
            # Use AppleScript to close applications gracefully
            try:
                # Get list of running applications
                cmd = "osascript -e 'tell application \"System Events\" to get name of every process where background is false'"
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)
                apps = result.stdout.strip().split(", ")
                
                # Close each application
                for app in apps:
                    # Skip Finder and system apps
                    if app.lower() in ["finder", "dock", "systemuiserver", "terminal"]:
                        continue
                        
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
            # For Linux, focus on GUI applications with X11
            try:
                # Try getting X11 windows
                cmd = "wmctrl -l"
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                
                if result.returncode == 0:
                    # Get window process mapping
                    windows = result.stdout.strip().split('\n')
                    window_ids = [line.split()[0] for line in windows if line]
                    
                    # Close each window
                    for win_id in window_ids:
                        try:
                            print(f"Closing window {win_id}...")
                            subprocess.run(["wmctrl", "-ic", win_id], check=True)
                            results["closed"].append(f"Window {win_id}")
                        except Exception as e:
                            results["failed"].append(f"Window {win_id}")
                else:
                    # Fallback for non-X11 systems or missing wmctrl
                    print("wmctrl not available, using basic process termination")
                    
                    # Get current user's processes
                    user_processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'username']):
                        try:
                            proc_info = proc.info
                            if proc_info['username'] == os.getlogin():
                                # Skip terminal, system processes
                                if proc_info['name'] not in ["bash", "sh", "python", "systemd", "kworker", 
                                                            "sshd", "gnome-terminal", "konsole"]:
                                    user_processes.append(proc)
                        except:
                            pass
                    
                    # Close each process
                    for proc in user_processes:
                        try:
                            print(f"Closing {proc.name()} (PID: {proc.pid})...")
                            proc.terminate()
                            results["closed"].append(proc.name())
                        except Exception as e:
                            results["failed"].append(proc.name())
            except Exception as e:
                speak(f"Error closing applications: {e}")
        
        # Wait a moment for processes to close
        time.sleep(2)
        
        print(f"Attempted to close {len(results['closed'])} applications")
        if results['failed']:
            speak(f"Failed to close {len(results['failed'])} applications")
            
        return results
        
    except Exception as e:
        speak(f"Error closing applications: {e}")
        return {
            "closed": [],
            "failed": ["Error occurred while closing applications: " + str(e)]
        }

def shutdown_computer(confirmation_func=None, close_apps=True):
    """
    Shut down the computer with confirmation
    
    Args:
        confirmation_func: Function to get confirmation from user
        close_apps: Whether to close all applications before shutdown
    
    Returns:
        True if shutdown initiated, False otherwise
    """
    # Ask for confirmation
    speak("Requesting confirmation to shut down computer...")
    confirmed = confirm_shutdown(confirmation_func)
    
    if not confirmed:
        print("Shutdown cancelled")
        return False
    
    # Close all applications if requested
    if close_apps:
        speak("Closing all applications before shutdown...")
        close_results = close_all_applications()
        
        # Show summary of closed applications
        if close_results["closed"]:
            print(f"Successfully closed {len(close_results['closed'])} applications")
            
        if close_results["failed"]:
            print(f"Failed to close {len(close_results['failed'])} applications")
            print("The system will attempt to shut down anyway")
    
    system = platform.system()
    
    try:
        if system == "Windows":
            # Windows shutdown command
            subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
            speak("Computer is shutting down in 5 seconds")
            return True
        elif system == "Darwin":  # macOS
            # macOS shutdown command
            subprocess.run(["shutdown", "-h", "now"], check=True)
            speak("Computer is shutting down")
            return True
        elif system == "Linux":
            # Linux shutdown command
            subprocess.run(["shutdown", "-h", "now"], check=True)
            speak("Computer is shutting down")
            return True
        else:
            speak(f"Unsupported operating system: {system}")
            return False
    except Exception as e:
        speak(f"Error shutting down computer: {e}")
        return False

# Example usage
if __name__ == "__main__":
    print("System control example:")
    print("1. Lock computer")
    print("2. Sleep computer")
    print("3. Shutdown computer")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        lock_computer()
    elif choice == "2":
        sleep_computer()
    elif choice == "3":
        shutdown_computer()
    else:
        print("Invalid choice")