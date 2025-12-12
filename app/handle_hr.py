"""
Heart rate measurement handler.

This module implements the interactive heart rate measurement flow invoked
from the main menu. It shows a brief instruction screen, waits for the user
to press the encoder button to begin, calibrates the signal threshold for
beat detection, then collects live signal samples for a fixed duration
(30 seconds). During collection it maintains a sliding buffer of recent
signal samples for the ECG display, detects beats and intervals between
successive beats, estimates the current BPM for display, and finally shows
the measured BPM on a results screen.

The implementation is deliberately synchronous and blocking (typical for
small embedded UI flows): while measurement is active the function controls
the UI and sampling loop until the measurement period ends.
"""

from ui.layout_hr import show_start_instruction, show_hr_screen
from ui.layout_animations import draw_ecg_frame
from core.hrm import calibrate_threshold, read_live_signal, calculate_bpm
from core.utils import is_encoder_pressed, encoder_button
import time
from core.adc_sampler import start_sampling
from machine import Pin

led = Pin("LED", Pin.OUT)


def handle_measure_hr(encoder):
    """
    Run a single heart rate measurement session.

    Args:
        encoder: The shared `Encoder` instance (not used directly here but kept
                 for API consistency with other handlers and potential future
                 interactions inside UI callbacks).

    Flow:
    1. Show instructions telling the user how to position sensors and press
       the encoder button to start.
    2. Wait for the user to press the encoder (debounced using short sleeps).
    3. Calibrate the signal threshold using `calibrate_threshold()` which
       should examine the current signal and choose a detection threshold.
    4. Sample the live signal in a tight loop for 30 seconds:
       - Use `read_live_signal(threshold)` to obtain raw sample values and a
         boolean `beat` indicating whether a beat was detected at that sample.
       - Maintain a sliding window `buffer` of the most recent 128 samples
         for plotting an ECG-like frame.
       - Track timestamps of beat events and compute valid inter-beat
         intervals (in milliseconds) for BPM calculation; intervals outside
         a plausible range (250 ms to 2000 ms) are ignored.
       - Continuously estimate BPM over the last few intervals using
         `calculate_bpm(...)` and render the ECG frame with `draw_ecg_frame`.
    5. After the 30s measurement window finishes, compute the final BPM
       from all collected intervals and show the summarized heart rate screen.

    Timing and units:
    - `time.ticks_ms()` and `time.ticks_diff()` are used for millisecond
      resolution timing compatible with MicroPython timing helpers.
    - The measurement window uses 30_000 ms (30 seconds) as the active
      sampling period.
    """

    # Show starting instructions to the user (how to prepare for the test).
    show_start_instruction()

    # Wait until the encoder button is pressed to begin the measurement. The
    # `is_encoder_pressed()` helper abstracts the higher-level check while
    # the `encoder_button.value()` raw pin read is used below to wait for the
    # button state to settle. Short sleeps provide a simple debounce.
    while not is_encoder_pressed():
        time.sleep(0.05)
    while encoder_button.value() == 0:
        time.sleep(0.05)
    
    start_sampling()
    # Calibrate a threshold for beat detection. The implementation should
    # examine current signal characteristics (e.g. noise level) and return
    # a numeric threshold value appropriate for `read_live_signal`.
    threshold = calibrate_threshold()

    # Buffer to store recent raw values for plotting. Keep at most 128
    # samples to bound memory usage on embedded devices.
    buffer = []

    # `intervals` stores valid inter-beat intervals (ms) used for BPM
    # calculation. `beats` stores raw timestamped beat events and is used to
    # compute intervals incrementally.
    intervals = []
    beats = []

    # Mark the start time (ms) of the measurement window.
    start_time = time.ticks_ms()

    # Active sampling loop: run until 30 seconds have elapsed since start.
    while time.ticks_diff(time.ticks_ms(), start_time) < 30_000:
        # Read a single live sample and whether a beat has been detected at
        # this sample given the calibrated threshold.
        value, beat = read_live_signal(threshold)

        # Append the newest sample to the sliding buffer and drop the oldest
        # sample if buffer exceeds the display capacity.
        buffer.append(value)
        if len(buffer) > 128:
            buffer.pop(0) 

        # If a beat was detected, timestamp it and compute the interval to
        # the previous beat. Only intervals within a plausible physiological
        # range are kept to avoid corrupting BPM calculations with noise.
        if beat:
            led.toggle()
            now = time.ticks_ms()
            beats.append(now)
            if len(beats) > 1:
                interval = time.ticks_diff(beats[-1], beats[-2])
                # Accept intervals between approximately 250 ms (240 bpm)
                # and 2000 ms (30 bpm). Adjust these bounds if your device
                # or population requires different limits.
                if 250 < interval < 2000:
                    intervals.append(interval)

        # Continuously compute a short-term BPM estimate using the last few
        # intervals (for example the last 5) so the UI shows a responsive
        # value while the measurement proceeds.
        bpm = calculate_bpm(intervals[-5:])

        # Compute remaining time in seconds for the 30s window and draw the
        # ECG frame with the buffer, remaining time, and current BPM.
        time_left = 30 - time.ticks_diff(time.ticks_ms(), start_time) // 1000
        draw_ecg_frame(buffer, time_left, bpm)

        # Small sleep to pace sampling and avoid hogging CPU — adjust as
        # necessary for your sampling rate and responsiveness requirements.
        time.sleep(0.01)

    # After the sampling window ends, compute the final BPM using all
    # collected intervals and show the result screen to the user.
    bpm = calculate_bpm(intervals)
    show_hr_screen(bpm)
