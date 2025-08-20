import os
import subprocess
import tempfile
from datetime import datetime

def convert_json_to_rinex(json_data):
    """
    Converts GNSS data from a JSON object to a RINEX .obs file.

    Args:
        json_data (dict): A dictionary containing 'raw' and 'fix' GNSS data.

    Returns:
        str: The file path to the generated RINEX .obs file, or None on failure.
    """
    raw_measurements = json_data.get('raw', [])
    fix_data = json_data.get('fix', [])

    if not raw_measurements:
        print("Error: No raw GNSS measurements found in JSON data.")
        return None

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, dir='/tmp') as tmp_file:
        temp_android_file = tmp_file.name
        
        # Write standard android_rinex header
        tmp_file.write("# \n")
        tmp_file.write("# Header Description:\n")
        tmp_file.write("# \n")
        tmp_file.write("# Version: 1.4.0.0, Platform: N\n")
        tmp_file.write("# \n")
        tmp_file.write("# Raw,ElapsedRealtimeMillis,TimeNanos,LeapSecond,TimeUncertaintyNanos,FullBiasNanos,BiasNanos,BiasUncertaintyNanos,DriftNanosPerSecond,DriftUncertaintyNanosPerSecond,HardwareClockDiscontinuityCount, Svid,TimeOffsetNanos,State,ReceivedSvTimeNanos,ReceivedSvTimeUncertaintyNanos,Cn0DbHz,PseudorangeRateMetersPerSecond,PseudorangeRateUncertaintyMetersPerSecond,AccumulatedDeltaRangeState,AccumulatedDeltaRangeMeters,AccumulatedDeltaRangeUncertaintyMeters,CarrierFrequencyHz,CarrierCycles,CarrierPhase,CarrierPhaseUncertainty,MultipathIndicator,SnrInDb,ConstellationType\n")
        tmp_file.write("# \n")
        tmp_file.write("# Fix,Provider,Latitude,Longitude,Altitude,Speed,Accuracy,(UTC)TimeInMs\n")
        tmp_file.write("# \n")
        tmp_file.write("# Nav,Svid,Type,Status,MessageId,Sub-messageId,Data(Bytes)\n")
        tmp_file.write("# \n")

        # Write Fix data
        for fix_line in fix_data:
            tmp_file.write(fix_line + '\n')
        
        # Write Raw measurements
        for raw_line in raw_measurements:
            tmp_file.write(raw_line + '\n')

    # Generate output filename
    output_dir = "/data/rinex_files"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    rinex_output_file = os.path.join(output_dir, f"gnss_data_{timestamp}.obs")

    # Path to the android_rinex conversion script
    android_rinex_path = "./android_rinex"
    if not os.path.exists(android_rinex_path):
        # A common alternative path in docker containers
        android_rinex_path = "/home/ubuntu/android_rinex" 
    
    converter_script = os.path.join(android_rinex_path, "bin", "gnsslogger_to_rnx")

    if not os.path.exists(converter_script):
        print(f"Error: android_rinex converter not found at {converter_script}")
        os.unlink(temp_android_file)
        return None

    # Run the conversion
    cmd = ["python3", converter_script, "-o", rinex_output_file, temp_android_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("RINEX conversion successful!")
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        
        if os.path.exists(rinex_output_file):
            return rinex_output_file
        else:
            print("Error: RINEX file was not created.")
            return None

    except subprocess.CalledProcessError as e:
        print("RINEX conversion failed!")
        print("Error:", e.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        # Clean up temporary file
        if os.path.exists(temp_android_file):
            os.unlink(temp_android_file)