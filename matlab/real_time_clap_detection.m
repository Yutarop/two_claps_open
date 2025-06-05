% Real-time audio processing (detecting two claps, no graphs)

% Setting up the audio input device
Fs = 44100; % Sampling frequency (e.g., 44.1kHz)
frameDuration = 0.02; % Frame length (20ms)
frameSize = round(Fs * frameDuration); % Frame size (number of samples)
audioIn = audioDeviceReader('SampleRate', Fs, 'SamplesPerFrame', frameSize);

% Designing the bandpass filter (1kHz to 2.5kHz)
f_low = 1400; % Lower cutoff frequency (Hz)
f_high = 1800; % Upper cutoff frequency (Hz)
order = 2; % Filter order
[b, a] = butter(order, [f_low, f_high]/(Fs/2), 'bandpass');

% Setting up the window function
window = hann(frameSize); % Hanning window

% Settings for peak detection
threshold = 0.2; % Amplitude threshold (needs adjustment)
minPeakDistanceSec = 0.2; % Minimum peak interval (seconds)
clapCount = 0; % Number of detected claps
clapTimes = []; % Times of claps
lastPeakTime = -Inf; % Time of the last peak

% Real-time processing loop (detecting two claps)
disp('Starting real-time processing. Please clap twice.');
startTime = tic;
while clapCount < 2 % Exit after detecting 2 claps
    % Getting audio frame
    frame = audioIn() .* window; % Apply window function

    % Applying the bandpass filter
    frame_filtered = filter(b, a, frame);

    % Peak detection (managing intervals between frames)
    [peaks, ~] = findpeaks(abs(frame_filtered), 'MinPeakHeight', threshold);
    currentTime = toc(startTime);
    if ~isempty(peaks)
        % Check peak interval (at least 0.2 seconds) between frames
        timeDiff = currentTime - lastPeakTime;
        if timeDiff >= minPeakDistanceSec
            clapCount = clapCount + 1;
            clapTimes = [clapTimes; currentTime];
            disp(['Detected clap: ' num2str(currentTime) ' seconds']);
            lastPeakTime = currentTime;
        end
    end
end

% Releasing resources
release(audioIn);

% Displaying results and comments
disp(['Sampling frequency: ' num2str(Fs) ' Hz']);
disp(['Number of detected claps: ' num2str(clapCount)]);
disp('Two claps have been detected!');
if ~isempty(clapTimes)
    disp('Times of claps (seconds):');
    disp(clapTimes);
end
