# `two_claps_open` 👏
Open Chrome (or any file/app) by simply clapping twice — just like [Tony Stark](https://www.youtube.com/watch?v=OT2b5KzMoC0&t=101s).

#### 🔸Open a presentation slide and chrome by clapping twice (two_claps_open.py)


https://github.com/user-attachments/assets/15849e57-b662-4096-8f67-f8937ae61711


#### 🔸Activate a voice assistant agent by clapping twice (agent_on_clap.py)


https://github.com/user-attachments/assets/3b0ef232-7229-4ca4-9d57-f2fc325295bc


## Clap Detection
To figure out what a clap "looks like" in terms of sound, I first recorded a sample clap and ran a Fourier transform on it to check the frequency content.
From the analysis, most of the energy from the clap is concentrated around 1.4kHz to 1.8kHz. 
Based on this, I set up a bandpass filter to isolate only that range and ignore irrelevant noise.
After filtering, I used peak detection to recognize when a clap happens in real time. (see figure below)
Once two peaks (claps) are detected with some minimum spacing, the system launches Chrome (or any command you define).

![fig](https://github.com/user-attachments/assets/fa15cd8d-8690-4a86-b878-273dbac2f241)

## Dependencies
##### 🗂️ requirements-core.txt (for `two_claps_open.py`)
```bash
numpy
pyaudio
scipy
pywin32
```

##### 🗂️ requirements-agent.txt (for `agent_on_clap.py`) 
```bash
PyAudio
pygame
SpeechRecognition
dotenv
gTTS
langchain
langchain-core
langchain-google
scipy
```
> 💡 Don’t forget to set your Google API key in a .env file. Google offers a free tier for API usage.
