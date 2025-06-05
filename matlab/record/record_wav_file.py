import os
import threading
import time
import wave

import keyboard
import pyaudio


class AudioRecorder:
    def __init__(self):
        # Audio settings
        self.chunk = 1024  # Buffer size
        self.format = pyaudio.paInt16  # 16bit
        self.channels = 1  # Mono
        self.rate = 44100  # Sampling rate

        self.frames = []
        self.recording = False
        self.audio = pyaudio.PyAudio()

    def start_recording(self):
        """Start recording"""
        self.recording = True
        self.frames = []

        # Open audio stream
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        print("Recording... Press Enter to stop")

        # Recording loop
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)

        # Close stream
        stream.stop_stream()
        stream.close()

        print("Recording stopped")

    def stop_recording(self):
        """Stop recording"""
        self.recording = False

    def save_recording(self, filename):
        """Save recording data as WAV file"""
        if not self.frames:
            print("No recording data available")
            return

        # Create wav_files directory if it doesn't exist
        wav_dir = "wav_files"
        if not os.path.exists(wav_dir):
            os.makedirs(wav_dir)

        # Full path for the file
        filepath = os.path.join(wav_dir, filename)

        # Save as WAV file
        wf = wave.open(filepath, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b"".join(self.frames))
        wf.close()

        print(f"Recording saved as {filepath}")

    def cleanup(self):
        """Clean up resources"""
        self.audio.terminate()


def main():
    recorder = AudioRecorder()

    try:
        # Get filename from user input
        filename = input(
            "Enter filename for recording (without .wav extension): "
        ).strip()
        if not filename:
            filename = "recording"

        # Add .wav extension if not present
        if not filename.endswith(".wav"):
            filename += ".wav"

        print(f"Filename set to: {filename}")
        print("Press Enter to start recording...")
        input()  # Wait for Enter to start

        # Start recording in a separate thread
        recording_thread = threading.Thread(target=recorder.start_recording)
        recording_thread.start()

        # Wait for Enter key to stop recording
        keyboard.wait("enter")

        # Stop recording
        recorder.stop_recording()
        recording_thread.join()

        # Save the recording
        recorder.save_recording(filename)

    except KeyboardInterrupt:
        print("\nRecording interrupted")
        recorder.stop_recording()

    finally:
        recorder.cleanup()


if __name__ == "__main__":
    main()
