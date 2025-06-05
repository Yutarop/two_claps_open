% Detection of clap sound (Bandpass filter and peak detection)

% Reading the WAV file
[y, Fs] = audioread('rec3_with_noise.wav'); % Change 'clap.wav' to the actual filename

% Creating the time axis
t = (0:length(y)-1)/Fs;

% Designing the bandpass filter (1.4kHz to 1.8kHz)
f_low = 1400;  % Lower cutoff frequency (Hz)
f_high = 1800; % Upper cutoff frequency (Hz)
order = 4;     % Filter order (Butterworth)
[b, a] = butter(order, [f_low, f_high]/(Fs/2), 'bandpass'); % Butterworth bandpass filter

% Applying the filter
y_filtered = filter(b, a, y);

% Fourier transform (to check the frequency spectrum after filtering)
Y_filtered = fft(y_filtered);
N = length(y);
f = (0:N-1)*(Fs/N);
amplitude_filtered = abs(Y_filtered)/N;
half_N = floor(N/2);
f = f(1:half_N);
amplitude_filtered = amplitude_filtered(1:half_N);

% Peak detection (detecting clap sound)
% threshold = 0.3 * max(abs(y_filtered)); % Threshold (30% of maximum amplitude)
threshold = 0.25;
disp(['threshold: ' num2str(threshold)]);
[peaks, locs] = findpeaks(abs(y_filtered), 'MinPeakHeight', threshold, 'MinPeakDistance', round(Fs*0.2)); % Detect peaks with a minimum interval of 0.2 seconds
% Display the number of detected peaks
disp(['Number of detected peaks: ']);
disp(peaks);
% Display the amplitude of detected peaks
disp('Amplitude of detected peaks:');
disp(locs);
clap_times = t(locs); % Time positions of the peaks

% Plotting the graphs
figure;

% Subplot 1: Original time waveform
subplot(3,1,1);
plot(t, y);
title('Original audio signal (clap sound)');
xlabel('Time (seconds)');
ylabel('Amplitude');
grid on;

% Subplot 2: Time waveform after filtering and peak detection
subplot(3,1,2);
plot(t, y_filtered);
hold on;
plot(clap_times, y_filtered(locs), 'ro', 'MarkerSize', 8, 'LineWidth', 2); % Display peaks as red circles
title('After applying bandpass filter (1.4kHz to 1.8kHz) and peak detection');
xlabel('Time (seconds)');
ylabel('Amplitude');
grid on;
hold off;

% Subplot 3: Frequency spectrum after filtering
subplot(3,1,3);
plot(f, amplitude_filtered);
title('Frequency spectrum after filtering');
xlabel('Frequency (Hz)');
ylabel('Amplitude');
grid on;

% Overall title for the graphs
sgtitle('Detection of clap sound (1.4kHz to 1.8kHz)');

% Displaying the sampling frequency and detection results
disp(['Sampling frequency: ' num2str(Fs) ' Hz']);
disp(['Number of detected claps: ' num2str(length(locs))]);
disp('Times of claps (seconds):');
disp(clap_times');
