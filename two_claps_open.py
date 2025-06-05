import time
import webbrowser

import numpy as np
import pyaudio
from scipy import signal

# import win32com.client

# Audio configuration
SAMPLING_RATE = 44100  # Hz
FRAME_DURATION = 0.02  # seconds (20ms)
FRAME_SIZE = int(SAMPLING_RATE * FRAME_DURATION)

# Filter configuration
FILTER_ORDER = 2
FREQ_LOW = 1400  # Hz
FREQ_HIGH = 1800  # Hz

# Peak detection configuration
AMPLITUDE_THRESHOLD = 0.2
MIN_PEAK_INTERVAL = 0.2  # seconds

# FILE_PATH = "/path/to/your_file/presentation.pptx"

def initialize_audio_stream():
    """Initialize PyAudio stream for audio input."""
    p = pyaudio.PyAudio()
    return p, p.open(
        format=pyaudio.paFloat32,
        channels=1,
        rate=SAMPLING_RATE,
        input=True,
        frames_per_buffer=FRAME_SIZE,
    )


def create_bandpass_filter():
    """Create bandpass filter for 1.4kHz to 1.8kHz range."""
    return signal.butter(
        FILTER_ORDER,
        [FREQ_LOW, FREQ_HIGH],
        btype="bandpass",
        fs=SAMPLING_RATE,
        output="sos",
    )


def main():
    # Initialize audio processing
    p, stream = initialize_audio_stream()
    sos = create_bandpass_filter()
    window = signal.windows.hann(FRAME_SIZE)

    # Initialize state variables
    clap_count = 0
    clap_times = []
    last_peak_time = -float("inf")
    filter_state = np.zeros((sos.shape[0], 2))

    print("Starting real-time processing. Please clap twice.")
    start_time = time.time()

    try:
        while clap_count < 2:
            # Read and process audio frame
            frame = np.frombuffer(
                stream.read(FRAME_SIZE, exception_on_overflow=False), dtype=np.float32
            )
            frame = frame * window

            # Apply bandpass filter
            frame_filtered, filter_state = signal.sosfilt(sos, frame, zi=filter_state)

            # Detect peaks
            peaks, _ = signal.find_peaks(
                np.abs(frame_filtered), height=AMPLITUDE_THRESHOLD
            )
            current_time = time.time() - start_time

            if peaks.size > 0 and (current_time - last_peak_time) >= MIN_PEAK_INTERVAL:
                clap_count += 1
                clap_times.append(current_time)
                print(f"Clap detected: {current_time:.2f} seconds")
                last_peak_time = current_time

                if clap_count == 2:
                    webbrowser.open("https://www.netflix.com/")
                    # this is for powerpoint
                    # if os.path.exists(FILE_PATH):
                    #     try:
                    #         # Start the PowerPoint application
                    #         powerpoint = win32com.client.Dispatch("PowerPoint.Application")
                    #         powerpoint.Visible = True  # Show PowerPoint
                    #         # Open the presentation
                    #         presentation = powerpoint.Presentations.Open(os.path.abspath(FILE_PATH))
                    #         # Start the slideshow
                    #         presentation.SlideShowSettings.Run()
                    #     except Exception as e:
                    #         print(f"PowerPoint operation error: {e}")
                    #     else:
                    #         print(f"Error: PowerPoint file {FILE_PATH} not found")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    print(f"\nResults:")
    print(f"Sampling frequency: {SAMPLING_RATE} Hz")
    print(f"Number of detected claps: {clap_count}")
    print("Two claps have been detected!")

    if clap_times:
        print("Clap times (seconds):")
        for t in clap_times:
            print(f"{t:.4f}")


if __name__ == "__main__":
    main()
