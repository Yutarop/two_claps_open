import io
import time
import webbrowser
import numpy as np
import pyaudio
import pygame
import speech_recognition as sr
from dotenv import load_dotenv
from gtts import gTTS
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from scipy import signal

load_dotenv()

class VoiceActivatedAI:
    def __init__(self):
        # Audio settings
        self.Fs = 44100
        self.frame_duration = 0.02
        self.frame_size = int(self.Fs * self.frame_duration)

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None

        # Bandpass filter (1.4kHz-1.8kHz)
        self.f_low = 1400
        self.f_high = 1800
        self.order = 2
        self.sos = signal.butter(
            self.order,
            [self.f_low, self.f_high],
            btype="bandpass",
            fs=self.Fs,
            output="sos",
        )

        # Window function
        self.window = signal.windows.hann(self.frame_size)

        # Peak detection settings
        self.threshold = 0.2
        self.min_peak_distance_sec = 0.2

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize pygame mixer
        pygame.mixer.init()

        # Initialize AI agent
        self.setup_ai_agent()

    def setup_ai_agent(self):
        @tool
        def open_browser(url: str) -> str:
            """Opens the given URL in the firefox web browser."""
            webbrowser.open(url)
            return f"Opened browser to {url}"

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        self.tools = [open_browser]
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful voice assistant. You can open URLs in the firefox browser. "
                    "Be concise in your responses as they will be converted to speech.",
                ),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_tool_calling_agent(prompt=self.prompt, tools=self.tools, llm=self.llm)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def detect_claps(self):
        print("Listening for claps... Please clap twice to activate the AI assistant.")
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.Fs,
            input=True,
            frames_per_buffer=self.frame_size,
        )

        clap_count = 0
        last_peak_time = -float("inf")
        zi = np.zeros((self.sos.shape[0], 2))
        start_time = time.time()

        while clap_count < 2:
            try:
                frame = np.frombuffer(
                    self.stream.read(self.frame_size, exception_on_overflow=False),
                    dtype=np.float32,
                )
                frame = frame * self.window
                frame_filtered, zi = signal.sosfilt(self.sos, frame, zi=zi)
                peaks, _ = signal.find_peaks(np.abs(frame_filtered), height=self.threshold)
                current_time = time.time() - start_time

                if len(peaks) > 0 and (current_time - last_peak_time) >= self.min_peak_distance_sec:
                    clap_count += 1
                    print(f"Clap detected: {current_time:.2f} seconds (Count: {clap_count}/2)")
                    last_peak_time = current_time

            except Exception as e:
                print(f"Error in clap detection: {e}")
                continue

        self.stream.stop_stream()
        self.stream.close()
        print("Two claps detected! Activating AI assistant...")
        return True

    def play_intro_sound(self):
        try:
            tts = gTTS(text="Hi, how can I help you?", lang="en")
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Error playing intro sound: {e}")
            print("Hi, how can I help you?")

    def listen_for_speech(self, timeout=5):
        print(f"Listening for your voice input for {timeout} seconds...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None

    def process_with_ai_agent(self, user_input):
        try:
            print(f"Processing request: {user_input}")
            response = self.agent_executor.invoke(input={"input": user_input})
            output_text = response.get("output", "I apologize, but I could not process your request.")
            print(f"AI Response: {output_text}")
            return output_text
        except Exception as e:
            error_message = f"Sorry, I encountered an error while processing your request: {str(e)}"
            print(error_message)
            return error_message

    def text_to_speech(self, text):
        try:
            print(f"Converting to speech: {text}")
            tts = gTTS(text=text, lang="en")
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"Error in text-to-speech conversion: {e}")
            print(f"AI says: {text}")

    def run(self):
        try:
            while True:
                if self.detect_claps():
                    self.play_intro_sound()
                    user_speech = self.listen_for_speech(timeout=5)
                    if user_speech:
                        ai_response = self.process_with_ai_agent(user_speech)
                        self.text_to_speech(ai_response)
                    else:
                        self.text_to_speech("I didn't hear anything. Please try again by clapping twice.")
                    print("\n" + "=" * 50)
                    print("Ready for next activation. Clap twice to continue...")
                    print("=" * 50 + "\n")
        except KeyboardInterrupt:
            print("\nShutting down voice-activated AI assistant...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if self.stream and not self.stream.is_stopped():
                self.stream.stop_stream()
                self.stream.close()
            self.p.terminate()
            pygame.mixer.quit()

def main():
    print("- Clap twice to activate")
    assistant = VoiceActivatedAI()
    assistant.run()

if __name__ == "__main__":
    main()