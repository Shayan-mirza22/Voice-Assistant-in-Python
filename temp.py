#  A temporary file to test different functions and commands
from speedtest import Speedtest

def check_internet_speed():
    st = Speedtest()
    download_speed = st.download() / 1_000_000  # Convert to Mbps
    upload_speed = st.upload() / 1_000_000

    print(f"Download speed: {download_speed:.2f} Mbps")
    print(f"Upload speed: {upload_speed:.2f} Mbps")

# Call the function
check_internet_speed()
