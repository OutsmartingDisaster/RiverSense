Stage 2: Data Validation & Pre-processing (Inside the Worker)
Before heavy analysis, the worker performs a deeper validation.
RINEX Quality Control (QC): Use a standard tool like gfzrnx from GFZ Potsdam to check the RINEX file for completeness, consistency, and quality.
This can identify issues like missing epochs, header problems, or a low number of tracked satellites.
Telemetry Triage: This is where your detailed telemetry becomes invaluable.
Check for red flags in the PhoneTelemetry data:
gnssStatus.errorCount > 0
appPerformance.crashCount > 0
systemHealth.thermalState is CRITICAL
deploymentInfo.siteConditions is not OPEN_SKY
This telemetry-based QC can assign a quality score to the raw data file before processing, helping to explain anomalous results later.
Update Metadata DB: The worker updates a PostgreSQL database table with the file's metadata, including the path, stationId, timestamp, and the initial QC score.
Stage 3: Core GNSS-Reflectometry (gnsrefl) Calculation
This is the scientific core of the pipeline, performed by the background worker. The goal is to calculate the vertical distance between the GNSS antenna and the reflecting surface (the water).
Step 3.1: SNR Data Extraction
The primary data for GNSS-R is not the position, but the Signal-to-Noise Ratio (SNR) of the satellite signals.
Tool: Use gfzrnx. It is the industry standard for this task.
Process: The worker executes a command like:
 code Bash
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
      gfzrnx -finp /path/to/downloaded.obs -fout /path/to/output.snr -snr -prn G07 -elv_lim 5 30
   
This command extracts SNR data for a specific satellite (e.g., GPS 07) when it's at a low elevation angle (between 5 and 30 degrees), where reflections are strongest.
The worker iterates this process for all visible satellites during the hour. The output is a simple text file with columns like elevation | azimuth | SNR1 | SNR2 | SNR5.
Step 3.2: Periodicity Analysis (Lomb-Scargle Periodogram)
The interference between the direct and reflected satellite signal creates oscillations in the SNR data. We need to find the frequency of these oscillations.
Problem: The SNR data is sampled at irregular intervals with respect to the satellite's elevation angle. A standard Fast Fourier Transform (FFT) is not suitable.
Solution: Use the Lomb-Scargle Periodogram (LSP), which is designed for finding frequencies in unevenly sampled data.
Process:
For each satellite pass extracted in the previous step, take the SNR data (e.g., for the L1 signal).
The "time" axis for the LSP is not time, but the sine of the elevation angle (sin(e)).
Apply the LSP algorithm to the (sin(e), SNR) data.
Find the highest peak in the resulting periodogram. The location of this peak is the dominant frequency (f) of the SNR oscillations.
Step 3.3: Reflector Height Calculation
The dominant frequency is directly related to the reflector height.
Formula: h = (λ * f) / 2
h: The reflector height (the vertical distance we want to measure).
λ: The wavelength of the GNSS signal being analyzed (e.g., GPS L1 is ~19 cm).
f: The dominant frequency from the LSP.
The worker calculates one h value for each valid satellite pass.
Stage 4: Post-Processing and Analysis
A single height measurement can be noisy. This stage refines the results.
Outlier Rejection: In a given time window (e.g., one hour), you will have multiple h values from different satellites. Some may be incorrect due to multipath, poor geometry, etc. Use a robust statistical method like Median Absolute Deviation (MAD) or a simple median filter to discard outliers and compute a single, robust reflector height for that hour.
Time Series Generation: Store this final hourly height value in the PostgreSQL database, linked to the stationId and timestamp. Over time, this builds up a precise time series of the water level.
Correlation Analysis:
Environmental: Correlate the water level time series with external data, like rainfall from a weather API.
Telemetry-Driven: Correlate data quality with device health. For example: Does the standard deviation of the reflector height increase when batteryStatus.temperature exceeds 40°C? This provides powerful diagnostic capabilities.
Stage 5: Data Serving & Visualization
The final stage is making the data accessible.
API Server: A simple API that queries the PostgreSQL database to provide the water level time series for a given station and date range.
Dashboard: Use a tool like Grafana or a custom web app to visualize the data from the API.
Key Visuals:
A plot of Water Level vs. Time for each station.
A map showing station locations and their latest status (from telemetry).
Diagnostic plots: Raw SNR vs. sin(e) and the corresponding LSP for any given satellite pass, which is essential for troubleshooting.
Alerting: Set up alerts (e.g., in Grafana or via a separate service) for critical conditions:
Water level exceeds a threshold.
A station stops sending data.
A station's batteryStatus.level drops below 15%.

