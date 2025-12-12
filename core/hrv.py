"""
HRV (heart rate variability) calculation helpers.

This module currently exposes a single function `calculate_hrv` which
computes a small set of summary statistics from a sequence of inter-beat
intervals (PPIs / R-R intervals). The function returns a tuple containing
the mean heart rate (bpm), mean PPI (ms), RMSSD, and SDNN. These metrics
are commonly used in simple HRV analyses.

Assumptions and units:
- `intervals` is expected to be a sequence of inter-beat intervals in
    milliseconds (ms).
- `mean_ppi` is computed in the same units (ms). `mean_hr` is derived from
    the mean interval using the relationship bpm = 60000 / mean_ppi.

Notes about statistics:
- RMSSD (root mean square of successive differences) is computed over the
    differences between consecutive intervals and uses N-1 in the denominator
    for the mean of squared differences (matching sample-based variance
    conventions used elsewhere in the codebase).
- SDNN (standard deviation of NN intervals) is computed using the sample
    standard deviation formula (denominator N-1).

The function is intentionally small and returns zeros when insufficient
data is available (fewer than 2 intervals) so callers can handle that case
explicitly (for example by showing an error or re-running the capture).
"""

def calculate_hrv(intervals):
    if len(intervals) < 2:
        return 0, 0, 0, 0
    mean_ppi = sum(intervals) / len(intervals)
    mean_hr = 60000 / mean_ppi
    rmssd = (sum((intervals[i] - intervals[i - 1]) ** 2 for i in range(1, len(intervals))) / (len(intervals) - 1)) ** 0.5
    sdnn = (sum((x - mean_ppi) ** 2 for x in intervals) / (len(intervals) - 1)) ** 0.5
    return mean_hr, mean_ppi, rmssd, sdnn

