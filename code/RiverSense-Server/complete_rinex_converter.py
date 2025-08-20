#!/usr/bin/env python3
"""
Complete Android GNSS Raw Data to RINEX Converter and Analyzer

This script provides a complete solution for converting Android GNSS Logger
CSV data to RINEX format and performing basic analysis.

Requirements:
- android_rinex (https://github.com/rokubun/android_rinex)
- georinex (pip install georinex)
- pandas, matplotlib, numpy

Usage:
    python3 complete_rinex_converter.py input_csv_file output_rinex_file
"""

import pandas as pd
import numpy as np
import sys
import os
import subprocess
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt

try:
    import georinex as gr
    GEORINEX_AVAILABLE = True
except ImportError:
    GEORINEX_AVAILABLE = False
    print("Warning: georinex not available. RINEX analysis features will be limited.")

class AndroidGNSSToRINEX:
    """
    Class to handle conversion of Android GNSS Logger data to RINEX format
    """
    
    def __init__(self):
        self.constellation_map = {
            1: 'G',  # GPS
            3: 'R',  # GLONASS  
            5: 'C',  # QZSS (mapped to BeiDou for simplicity)
            6: 'E',  # Galileo
        }
    
    def parse_android_csv(self, input_file):
        """
        Parse Android GNSS Logger CSV file and extract different data types
        """
        print(f"Parsing Android GNSS Logger file: {input_file}")
        
        raw_measurements = []
        fix_data = []
        status_data = []
        
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('Raw,'):
                raw_measurements.append(line)
            elif line.startswith('Fix,'):
                fix_data.append(line)
            elif line.startswith('Status,') or (line and not line.startswith('#') and ',' in line):
                # Handle status data or other CSV data
                parts = line.split(',')
                if len(parts) >= 7 and parts[0].isdigit():  # Likely status data
                    status_data.append(line)
        
        print(f"Found:")
        print(f"  - {len(raw_measurements)} raw GNSS measurements")
        print(f"  - {len(fix_data)} position fixes")
        print(f"  - {len(status_data)} status records")
        
        return raw_measurements, fix_data, status_data
    
    def convert_to_android_rinex_format(self, raw_measurements, fix_data, output_file):
        """
        Convert parsed data to android_rinex compatible format
        """
        print(f"Converting to android_rinex format: {output_file}")
        
        with open(output_file, 'w') as f:
            # Write standard android_rinex header
            f.write("# \n")
            f.write("# Header Description:\n")
            f.write("# \n")
            f.write("# Version: 1.4.0.0, Platform: N\n")
            f.write("# \n")
            f.write("# Raw,ElapsedRealtimeMillis,TimeNanos,LeapSecond,TimeUncertaintyNanos,FullBiasNanos,BiasNanos,BiasUncertaintyNanos,DriftNanosPerSecond,DriftUncertaintyNanosPerSecond,HardwareClockDiscontinuityCount, Svid,TimeOffsetNanos,State,ReceivedSvTimeNanos,ReceivedSvTimeUncertaintyNanos,Cn0DbHz,PseudorangeRateMetersPerSecond,PseudorangeRateUncertaintyMetersPerSecond,AccumulatedDeltaRangeState,AccumulatedDeltaRangeMeters,AccumulatedDeltaRangeUncertaintyMeters,CarrierFrequencyHz,CarrierCycles,CarrierPhase,CarrierPhaseUncertainty,MultipathIndicator,SnrInDb,ConstellationType\n")
            f.write("# \n")
            f.write("# Fix,Provider,Latitude,Longitude,Altitude,Speed,Accuracy,(UTC)TimeInMs\n")
            f.write("# \n")
            f.write("# Nav,Svid,Type,Status,MessageId,Sub-messageId,Data(Bytes)\n")
            f.write("# \n")
            
            # Write Fix data
            for fix_line in fix_data:
                f.write(fix_line + '\n')
            
            # Write Raw measurements
            for raw_line in raw_measurements[1:]:
                parts = raw_line.split(',')
                if len(parts) >= 29:
                    # Map fields correctly (user's UTCTimeMillis -> ElapsedRealtimeMillis)
                    converted_line = f"Raw,{parts[1]},{parts[2]},{parts[3]},{parts[4]},{parts[5]},{parts[6]},{parts[7]},{parts[8]},{parts[9]},{parts[10]},{parts[11]},{parts[12]},{parts[13]},{parts[14]},{parts[15]},{parts[16]},{parts[17]},{parts[18]},{parts[19]},{parts[20]},{parts[21]},{parts[22]},{parts[23]},{parts[24]},{parts[25]},{parts[26]},{parts[27]},{parts[28]}"
                    f.write(converted_line + '\n')
    
    def convert_to_rinex(self, android_format_file, rinex_output_file, android_rinex_path="./android_rinex"):
        """
        Use android_rinex tool to convert to RINEX format
        """
        print(f"Converting to RINEX format: {rinex_output_file}")
        
        # Path to the android_rinex conversion script
        converter_script = os.path.join(android_rinex_path, "bin", "gnsslogger_to_rnx")
        
        if not os.path.exists(converter_script):
            raise FileNotFoundError(f"android_rinex converter not found at {converter_script}")
        
        # Run the conversion
        cmd = ["python", converter_script, "-o", rinex_output_file, android_format_file]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("RINEX conversion successful!")
                if result.stderr:
                    print("Warnings:")
                    print(result.stderr)
            else:
                print("RINEX conversion failed!")
                print("Error:", result.stderr)
                return False
                
        except Exception as e:
            print(f"Error running conversion: {e}")
            return False
        
        return True
    
    def analyze_rinex(self, rinex_file):
        """
        Analyze RINEX file using georinex (if available)
        """
        if not GEORINEX_AVAILABLE:
            print("georinex not available. Skipping RINEX analysis.")
            return
        
        print(f"Analyzing RINEX file: {rinex_file}")
        
        try:
            # Read RINEX observation file
            obs = gr.load(rinex_file)
            
            print("\nRINEX File Analysis:")
            print(f"  - Time span: {obs.time.min().values} to {obs.time.max().values}")
            print(f"  - Number of epochs: {len(obs.time)}")
            print(f"  - Satellite systems: {list(obs.sv.values)}")
            print(f"  - Observable types: {list(obs.data_vars)}")
            
            # Plot satellite visibility
            if len(obs.time) > 1:
                self.plot_satellite_visibility(obs, rinex_file)
            
        except Exception as e:
            print(f"Error analyzing RINEX file: {e}")
    
    def plot_satellite_visibility(self, obs, rinex_file):
        """
        Create satellite visibility plot
        """
        try:
            plt.figure(figsize=(12, 8))
            
            # Plot C/N0 for each satellite
            if 'S1C' in obs.data_vars:
                cn0_data = obs['S1C']
                
                for sv in obs.sv.values:
                    sv_data = cn0_data.sel(sv=sv).dropna('time')
                    if len(sv_data) > 0:
                        plt.plot(sv_data.time, sv_data.values, 'o-', label=sv, markersize=3)
            
            plt.xlabel('Time')
            plt.ylabel('C/N0 (dB-Hz)')
            plt.title('Satellite Signal Strength Over Time')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save plot
            plot_file = rinex_file.replace('.o', '_analysis.png').replace('.obs', '_analysis.png')
            plt.savefig(plot_file, dpi=150, bbox_inches='tight')
            print(f"Satellite visibility plot saved: {plot_file}")
            plt.close()
            
        except Exception as e:
            print(f"Error creating plot: {e}")
    
    def process_complete_conversion(self, input_csv, output_rinex, android_rinex_path="./android_rinex"):
        """
        Complete conversion process from CSV to RINEX
        """
        print("=== Android GNSS to RINEX Conversion ===")
        print(f"Input: {input_csv}")
        print(f"Output: {output_rinex}")
        print()
        
        # Step 1: Parse input CSV
        raw_measurements, fix_data, status_data = self.parse_android_csv(input_csv)
        
        if not raw_measurements:
            print("Error: No raw GNSS measurements found in input file")
            return False
        
        # Step 2: Convert to android_rinex format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            temp_android_file = tmp_file.name
        
        try:
            self.convert_to_android_rinex_format(raw_measurements, fix_data, temp_android_file)
            
            # Step 3: Convert to RINEX
            success = self.convert_to_rinex(temp_android_file, output_rinex, android_rinex_path)
            
            if success and os.path.exists(output_rinex):
                print(f"\nRINEX file successfully created: {output_rinex}")
                
                # Step 4: Analyze RINEX file
                self.analyze_rinex(output_rinex)
                
                return True
            else:
                print("Failed to create RINEX file")
                return False
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_android_file):
                os.unlink(temp_android_file)

def main():
    """
    Main function for command-line usage
    """
    if len(sys.argv) != 2:
        print("Usage: python3 complete_rinex_converter.py <input_folder>")
        print()
        print("Example:")
        print("  python3 complete_rinex_converter.py KAFI-20250817_194119")
        sys.exit(1)

    input_folder = sys.argv[1]
    if not os.path.isdir(input_folder):
        print(f"Error: Input folder {input_folder} does not exist or is not a directory.")
        sys.exit(1)

    input_csv = os.path.join(input_folder, "raw.csv")
    if not os.path.exists(input_csv):
        print(f"Error: 'raw.csv' not found in {input_folder}")
        sys.exit(1)

    # Generate output filename from folder name
    folder_name = os.path.basename(input_folder)
    output_rinex = f"{folder_name}.25o"
    
    # Initialize converter
    converter = AndroidGNSSToRINEX()
    
    # Find android_rinex path
    android_rinex_path = "./android_rinex"
    if not os.path.exists(android_rinex_path):
        android_rinex_path = "/home/ubuntu/android_rinex"
    
    if not os.path.exists(android_rinex_path):
        print("Error: android_rinex tool not found. Please install it first.")
        print("git clone https://github.com/rokubun/android_rinex.git")
        sys.exit(1)
    
    # Perform conversion
    success = converter.process_complete_conversion(input_csv, output_rinex, android_rinex_path)
    
    if success:
        print("\n=== Conversion completed successfully! ===")
        print(f"RINEX file: {output_rinex}")
        print("\nYou can now use this RINEX file with GNSS processing software like:")
        print("- RTKLib")
        print("- GIPSY-OASIS")
        print("- Bernese GNSS Software")
        print("- Any other RINEX-compatible software")
    else:
        print("\n=== Conversion failed ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
