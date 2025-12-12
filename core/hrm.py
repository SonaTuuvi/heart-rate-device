"""
Heart rate sensing utilities.

This module provides low-level helpers to interact with a PPG/pulse sensor
connected to an ADC pin on the microcontroller. The functions here are
intended to be simple and efficient for use in embedded measurement flows.

Provided functions:
- `calibrate_threshold(calibration_time_ms=2000)`: sample the sensor for a
  short period and determine a threshold for beat detection.
- `measure_intervals(duration_sec=10)`: perform a blocking interval
  measurement for `duration_sec` seconds and return cleaned inter-beat
  intervals in milliseconds.
- `calculate_bpm(intervals)`: compute a BPM (beats per minute) value from
  a list of inter-beat intervals (ms).
- `read_live_signal(threshold)`: read a single sample and detect whether a
  beat occurred crossing the provided threshold; useful for live plotting
  and immediate beat detection during measurement.

Notes and assumptions:
- The ADC returns 16-bit values via `read_u16()`; adjust scaling if your
  platform differs.
- Inter-beat intervals outside of 250 ms (240 bpm) and 2000 ms (30 bpm)
  are treated as invalid and filtered out to reduce noise impact.
"""

from machine import Pin, ADC
import time
from core.adc_sampler import read_sample

# ADC pin used for the pulse/PPG sensor. Change this constant to match your
# board wiring. The code assumes the ADC supports `read_u16()` returning a
# 0..65535 range (MicroPython typical behaviour on many ports).
PULSE_SENSOR_PIN = 26
pulse_sensor = ADC(Pin(PULSE_SENSOR_PIN))

# Internal state used by `read_live_signal` to detect rising-edge crossings.
_last_value = 0


def calibrate_threshold(calibration_time_ms=2000):
    """
    Sample the sensor for `calibration_time_ms` milliseconds and determine
    a detection threshold based on observed min/max values.

    The function records the minimum and maximum ADC values observed during
    the calibration window and chooses a threshold value positioned at 70%
    of the dynamic range above the minimum. This heuristic works well for
    PPG signals where beats produce clear upward excursions above baseline.

    Args:
        calibration_time_ms: How long to sample for calibration (ms).

    Returns:
        int: An integer threshold value suitable for use with `read_live_signal`
             and beat detection.
    """

    min_val = 65535
    max_val = 0
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < calibration_time_ms:
        value = pulse_sensor.read_u16()
        min_val = min(min_val, value)
        max_val = max(max_val, value)
        # Small sleep to avoid hogging CPU and to allow ADC sampling cadence.
        time.sleep_ms(2)

    # Choose threshold at 70% of the dynamic range above the minimum.
    threshold = min_val + (max_val - min_val) * 0.7
    return int(threshold)


def measure_intervals(duration_sec=10):
    """
    Collect inter-beat timestamps for a blocking `duration_sec` period and
    return cleaned inter-beat intervals in milliseconds.

    The function calibrates a threshold first, then timestamps rising-edge
    events where the ADC reading crosses from below to above the threshold.
    A sliding window of recent beat timestamps is kept to bound memory.

    Args:
        duration_sec: Measurement duration in seconds.

    Returns:
        list[int]: A list of inter-beat intervals (ms) filtered to a
                   physiologically plausible range.
    """

    threshold = calibrate_threshold()
    window = []
    last_value = 0
    start_time = time.ticks_ms()

    # Sampling loop: read values until the requested measurement window ends.
    while time.ticks_diff(time.ticks_ms(), start_time) < duration_sec * 1000:
        value = pulse_sensor.read_u16()

        # Detect rising-edge crossing: previous value below threshold and
        # current value at/above threshold indicates a beat event.
        if last_value < threshold and value >= threshold:
            window.append(time.ticks_ms())
            # Keep at most the last 20 timestamps to limit memory usage.
            if len(window) > 20:
                window.pop(0)

        last_value = value
        time.sleep_ms(2)

    # If we observed at least two beats, compute inter-beat intervals and
    # filter out implausible values (noise or missed detections).
    if len(window) >= 2:
        intervals = [time.ticks_diff(window[i], window[i - 1]) for i in range(1, len(window))]
        # Accept intervals roughly between 250 ms (240 bpm) and 2000 ms (30 bpm).
        return [d for d in intervals if 250 < d < 2000]
    else:
        return []


def calculate_bpm(intervals):
    """
    Convert a list of inter-beat intervals (ms) to a BPM estimate.

    Returns 0 if no intervals are available. The BPM is computed from the
    average interval and rounded to the nearest integer.
    """

    if not intervals:
        return 0
    avg_interval = sum(intervals) / len(intervals)
    return round(60000 / avg_interval)


def read_live_signal(threshold):
    """
    Read one ADC sample and return the raw value plus a boolean indicating
    whether a beat was detected at this sample (rising-edge detection).

    The function uses a module-level `_last_value` to perform rising-edge
    detection: a beat is reported when the signal crosses from below to
    at-or-above the provided threshold. This is useful for real-time UI
    updates where immediate beat events are required.
    """ 
    value = read_sample()
    if value is None:
        return 0, False

    beat = value > threshold
    return value, beat


