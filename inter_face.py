import tkinter as tk
from tkinter import ttk
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pyaudio

# Import your existing functions (adjust the import path as needed)
# from your_voice_module import listen, speak, process_command

# Global variables
root = None
canvas = None
command_label = None
response_label = None
start_button = None
stop_button = None
status_label = None
waveform_frame = None
fig = None
ax = None
line = None
is_listening = False
audio_thread = None

# Audio settings for waveform
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize audio
p = pyaudio.PyAudio()
stream = None

def create_circular_button(parent, text, command, bg_color, x, y, size=80):
    """Create a circular button using Canvas"""
    canvas_btn = tk.Canvas(parent, width=size, height=size, bg='#f0f8ff', highlightthickness=0)
    canvas_btn.place(x=x, y=y)
    
    # Draw circle
    circle = canvas_btn.create_oval(5, 5, size-5, size-5, fill=bg_color, outline='#34495e', width=2)
    
    # Add text
    text_item = canvas_btn.create_text(size//2, size//2, text=text, font=('Arial', 10, 'bold'), fill='white')
    
    # Bind click events
    def on_click(event):
        command()
    
    def on_enter(event):
        canvas_btn.create_oval(5, 5, size-5, size-5, fill=lighten_color(bg_color), outline='#34495e', width=2)
        canvas_btn.create_text(size//2, size//2, text=text, font=('Arial', 10, 'bold'), fill='white')
    
    def on_leave(event):
        canvas_btn.create_oval(5, 5, size-5, size-5, fill=bg_color, outline='#34495e', width=2)
        canvas_btn.create_text(size//2, size//2, text=text, font=('Arial', 10, 'bold'), fill='white')
    
    canvas_btn.bind("<Button-1>", on_click)
    canvas_btn.bind("<Enter>", on_enter)
    canvas_btn.bind("<Leave>", on_leave)
    
    return canvas_btn

def lighten_color(color):
    """Lighten a hex color for hover effect"""
    colors = {
        '#27ae60': '#2ecc71',
        '#e74c3c': '#c0392b'
    }
    return colors.get(color, color)

def create_gui():
    """Creates and initializes the main GUI window."""
    global root, canvas, command_label, response_label, start_button, stop_button
    global status_label, waveform_frame, fig, ax, line
    
    root = tk.Tk()
    root.title("FS22.pk Voice Assistant")
    #root.iconbitmap("images (2).ico")
    root.geometry("800x600")
    root.configure(bg='#f0f8ff')
    root.resizable(False, False)
    
    # Company header
    header_frame = tk.Frame(root, bg='#f0f8ff', height=80)
    header_frame.place(x=0, y=0, width=800, height=80)
    
    company_label = tk.Label(
        header_frame,
        text="FS22.pk",
        font=('Arial', 24, 'bold'),
        fg='#2c3e50',
        bg='#f0f8ff'
    )
    company_label.place(x=400, y=15, anchor='center')
    
    tagline_label = tk.Label(
        header_frame,
        text="Your Intelligent Voice Assistant",
        font=('Arial', 12, 'italic'),
        fg='#7f8c8d',
        bg='#f0f8ff'
    )
    tagline_label.place(x=400, y=50, anchor='center')
    
    # Status label
    status_label = tk.Label(
        root,
        text="Ready to listen...",
        font=('Arial', 12, 'bold'),
        fg='#34495e',
        bg='#f0f8ff'
    )
    status_label.place(x=400, y=90, anchor='center')
    
    # Waveform visualization frame (smaller)
    waveform_frame = tk.Frame(root, bg='white', relief='sunken', bd=2)
    waveform_frame.place(x=100, y=120, width=600, height=120)
    
    # Create matplotlib figure for waveform (smaller)
    fig = Figure(figsize=(6, 1.2), dpi=100, facecolor='white')
    ax = fig.add_subplot(111)
    ax.set_xlim(0, CHUNK)
    ax.set_ylim(-32768, 32767)
    ax.set_title("Voice Waveform", fontsize=10, color='#2c3e50')
    ax.set_facecolor('#f8f9fa')
    
    # Remove grid lines and axis labels/ticks
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Initialize empty line for waveform
    x = np.arange(0, CHUNK)
    y = np.zeros(CHUNK)
    line, = ax.plot(x, y, color='#3498db', linewidth=2)
    
    canvas = FigureCanvasTkAgg(fig, waveform_frame)
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=0, width=600, height=120)
    
    # Command display section
    command_frame = tk.Frame(root, bg='#f0f8ff', relief='flat')
    command_frame.place(x=50, y=260, width=700, height=100)
    
    # Command header
    tk.Label(
        command_frame,
        text="What you said:",
        font=('Arial', 14, 'bold'),
        fg='#2c3e50',
        bg='#f0f8ff',
        anchor='w'
    ).place(x=0, y=0)
    
    # Command display area with border
    command_display_frame = tk.Frame(command_frame, bg='white', relief='solid', bd=1)
    command_display_frame.place(x=0, y=30, width=700, height=60)
    
    command_label = tk.Label(
        command_display_frame,
        text="",
        font=('Arial', 12),
        fg='#2c3e50',
        bg='white',
        anchor='w',
        justify='left',
        wraplength=680,
        padx=10,
        pady=5
    )
    command_label.place(x=0, y=0, width=700, height=60)
    
    # Separator line
    separator = tk.Frame(root, bg='#bdc3c7', height=2)
    separator.place(x=50, y=370, width=700, height=2)
    
    # Response display section
    response_frame = tk.Frame(root, bg='#f0f8ff', relief='flat')
    response_frame.place(x=50, y=390, width=700, height=100)
    
    # Response header
    tk.Label(
        response_frame,
        text="Assistant Response:",
        font=('Arial', 14, 'bold'),
        fg='#2c3e50',
        bg='#f0f8ff',
        anchor='w'
    ).place(x=0, y=0)
    
    # Response display area with border
    response_display_frame = tk.Frame(response_frame, bg='#f8f9fa', relief='solid', bd=1)
    response_display_frame.place(x=0, y=30, width=700, height=60)
    
    response_label = tk.Label(
        response_display_frame,
        text="",
        font=('Arial', 12),
        fg='#2c3e50',
        bg='#f8f9fa',
        anchor='w',
        justify='left',
        wraplength=680,
        padx=10,
        pady=5
    )
    response_label.place(x=0, y=0, width=700, height=60)
    
    # Circular control buttons at bottom
    start_button = create_circular_button(
        root, 
        "🎤\nSTART", 
        start_listening, 
        '#27ae60', 
        310, 
        520, 
        80
    )
    
    stop_button = create_circular_button(
        root, 
        "⏹\nSTOP", 
        stop_listening, 
        '#e74c3c', 
        410, 
        520, 
        80
    )
    
    # Initially disable stop button
    stop_button.configure(state='disabled')

def update_waveform():
    """Updates the waveform visualization in real-time."""
    global stream, line, ax, canvas, is_listening
    
    if not is_listening:
        return
    
    try:
        if stream and stream.is_active():
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Update the waveform line
            line.set_ydata(audio_data)
            if len(audio_data) > 0:
                ax.set_ylim(np.min(audio_data) - 1000, np.max(audio_data) + 1000)
            canvas.draw_idle()
    except Exception as e:
        print(f"Waveform update error: {e}")
    
    if is_listening:
        root.after(50, update_waveform)

def start_listening():
    """Starts the voice assistant listening process."""
    global is_listening, audio_thread, stream
    
    if is_listening:
        return
    
    is_listening = True
    start_button.configure(state='disabled')
    stop_button.configure(state='normal')
    status_label.config(text="Listening... Speak now!", fg='#27ae60')
    
    # Clear previous text
    command_label.config(text="")
    response_label.config(text="")
    
    # Start audio stream for waveform
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Start waveform update
        update_waveform()
        
        # Start listening thread
        audio_thread = threading.Thread(target=listening_worker, daemon=True)
        audio_thread.start()
        
    except Exception as e:
        display_response(f"Error starting audio: {e}")
        stop_listening()

def stop_listening():
    """Stops the voice assistant listening process."""
    global is_listening, stream
    
    is_listening = False
    start_button.configure(state='normal')
    stop_button.configure(state='disabled')
    status_label.config(text="Stopped listening.", fg='#e74c3c')
    
    # Stop audio stream
    if stream:
        try:
            stream.stop_stream()
            stream.close()
        except:
            pass
        stream = None
    
    # Reset waveform
    reset_waveform()

def reset_waveform():
    """Resets the waveform to flat line."""
    global line, ax, canvas
    
    y = np.zeros(CHUNK)
    line.set_ydata(y)
    ax.set_ylim(-1000, 1000)
    canvas.draw()

def listening_worker():
    """Worker function for the listening thread."""
    try:
        # Call your existing listen function
        # Replace this with your actual listen function
        command = listen_function()  # This should be your existing listen function
        
        if command:
            display_command(command)
            
            # Call your existing function to process the command and get response
            # Replace this with your actual command processing function
            response = process_command_function(command)  # This should be your existing process function
            
            display_response(response)
            
            # Optionally speak the response using your existing speak function
            # speak_function(response)  # This should be your existing speak function
            
    except Exception as e:
        display_response(f"Error: {e}")
    finally:
        if is_listening:
            root.after(100, stop_listening)

def display_command(text):
    """Displays user command in the GUI."""
    if command_label:
        command_label.config(text=text)

def display_response(text):
    """Displays assistant response in the GUI."""
    if response_label:
        response_label.config(text=text)

# Placeholder functions - replace these with your actual functions
def listen_function():
    """Replace this with your actual listen function"""
    # This is a placeholder - replace with your actual listen function
    import time
    time.sleep(2)  # Simulate listening time
    return "Hello, how are you?"  # This should return the actual command from your listen function

def process_command_function(command):
    """Replace this with your actual command processing function"""
    # This is a placeholder - replace with your actual command processing function
    return f"I heard you say: {command}"  # This should return the actual response

def speak_function(text):
    """Replace this with your actual speak function"""
    # This is a placeholder - replace with your actual speak function
    pass

def run_gui():
    """Runs the GUI main loop."""
    if root:
        root.mainloop()

def cleanup():
    """Cleanup function to be called when closing the application."""
    global p, stream, is_listening
    
    is_listening = False
    
    if stream:
        try:
            stream.stop_stream()
            stream.close()
        except:
            pass
    
    if p:
        try:
            p.terminate()
        except:
            pass

def on_closing():
    """Handle window closing event"""
    cleanup()
    if root:
        root.destroy()

# Main execution
if __name__ == "__main__":
    create_gui()
    if root:
        root.protocol("WM_DELETE_WINDOW", on_closing)
    run_gui()