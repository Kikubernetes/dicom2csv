#!/usr/bin/env python3

# A script that gathers information from all DICOM files in the current directory
# and summarizes them into a CSV file for each series.
# It searches recursively through subdirectories.
# Conditions: 
#  1. DICOM files must be located under the "org_data" directory.
#  2. Series DICOM files must be inside a directory that starts with "SE000".

# 20250203 Kikuko Kaneko
import os
import glob
import csv
import subprocess
import re

def get_tag_value(dcmdump_text, tag):
    """
    Extracts the value within square brackets for the specified tag (e.g., "0010,0010")
    from the output of dcmdump.
    """
    pattern = re.compile(r'\(' + re.escape(tag) + r'\).*?\[(.*?)\]', re.IGNORECASE)
    m = pattern.search(dcmdump_text)
    return m.group(1).strip() if m else ""

def run_command(cmd):
    """
    Executes a command and returns the output string.
    """
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode("utf-8")
    except Exception:
        return ""

def get_first_file(directory):
    """
    Recursively searches a directory and returns the path of the first file found.
    """
    files = [f for f in glob.glob(os.path.join(directory, "**"), recursive=True)
             if os.path.isfile(f)]
    return files[0] if files else ""

def extract_mrinfo_axis(series_dir):
    """
    Extracts the last numerical value (number of axes) from the "Dimensions:" line
    in the output of `mrinfo <series_dir>`.
    Example: "Dimensions: 128 x 128 x 33 x 100" → "100"
    """
    mrinfo_text = run_command(["mrinfo", series_dir])
    axis = ""
    for line in mrinfo_text.splitlines():
        if "Dimensions:" in line:
            parts = line.split(":")[-1].strip().split("x")
            if parts:
                axis = re.sub(r'\D', '', parts[-1])
            break
    return axis

def extract_mrinfo_shells(series_dir):
    """
    Extracts b-values and the number of volumes for each shell from the output of
    `mrinfo <series_dir> -shell_sizes -shell_bvalues`.
    Example output:
      0 1200 
      1 64 
    - First line: b-values for each shell (e.g., shell 0 has b-value 0, shell 1 has b-value 1200)
    - Second line: number of volumes for each shell (e.g., shell 0 has 1 volume, shell 1 has 64 volumes)
    """
    shell_text = run_command(["mrinfo", series_dir, "-shell_sizes", "-shell_bvalues"])
    lines = [line.strip() for line in shell_text.splitlines() if re.match(r'^[0-9]', line)]
    if len(lines) >= 2:
        b_values    = ", ".join(lines[0].split())
        shell_sizes = ", ".join(lines[1].split())
        return b_values, shell_sizes
    else:
        return "", ""

def main():
    BASE_DIR = "."  # Top-level directory containing subject directories
    # Header for the output CSV (same columns as results.csv)
    header = [
        "SubjectDir", "PatientName", "PatientAge", "PatientSex", "StudyDate",
        "SeriesDir", "Manufacturer", "InstitutionName", "SeriesDescription",
        "ModelName", "EthnicGroup", "RepetitionTime", "EchoTime", "MagneticFieldStrength",
        "PixelBandwidth", "ProtocolName", "PhaseEncoding", "FlipAngle",
        "DTI_Axis", "DTI_bvalues", "DTI_ShellSizes"
    ]
    out_rows = []

    # Iterate through each subdirectory under BASE_DIR, treating them as subject directories
    for subj_dir in glob.glob(os.path.join(BASE_DIR, "*/")):
        org_data = os.path.join(subj_dir, "org_data")
        if not os.path.isdir(org_data):
            continue
        print(f"Processing subject: {subj_dir}")

        # Search for a subject-level DICOM file within the entire org_data directory
        subj_dcm = get_first_file(org_data)
        if not subj_dcm:
            continue
        dcmdump_text = run_command(["dcmdump", subj_dcm])
        patient_name = get_tag_value(dcmdump_text, "0010,0010")
        patient_age  = get_tag_value(dcmdump_text, "0010,1010")
        patient_sex  = get_tag_value(dcmdump_text, "0010,0040")
        study_date   = get_tag_value(dcmdump_text, "0008,0020")

        # Extract only the last directory name from the subject path (e.g., "1675428")
        subject_dir_short = os.path.basename(os.path.normpath(subj_dir))

        # Recursively search the org_data directory for series directories starting with "SE000"
        series_dirs = glob.glob(os.path.join(org_data, "**", "SE000*"), recursive=True)

        for series_dir in series_dirs:
            # Extract only the last directory name of each series
            series_dir_short = os.path.basename(os.path.normpath(series_dir))
            rep_dcm = get_first_file(series_dir)
            if not rep_dcm:
                continue
            rep_dump = run_command(["dcmdump", rep_dcm])
            # Extract relevant DICOM tags
            manufacturer      = get_tag_value(rep_dump, "0008,0070")
            institution       = get_tag_value(rep_dump, "0008,0080")
            series_description= get_tag_value(rep_dump, "0008,103E")
            model_name        = get_tag_value(rep_dump, "0008,1090")
            ethnic_group      = get_tag_value(rep_dump, "0010,2160")
            repetition_time   = get_tag_value(rep_dump, "0018,0080")
            echo_time         = get_tag_value(rep_dump, "0018,0081")
            magnetic_field    = get_tag_value(rep_dump, "0018,0087")
            pixel_bandwidth   = get_tag_value(rep_dump, "0018,0095")
            protocol_name     = get_tag_value(rep_dump, "0018,1030")
            phase_encoding    = get_tag_value(rep_dump, "0018,1312")
            flip_angle        = get_tag_value(rep_dump, "0018,1314")

            # Determine if the series is DTI: Skip if neither Series Description nor Protocol Name contains "DTI" (case insensitive)
            keywords = ["dti", "diff", "ep2d", "dki","dwi"]
            desc_lower = series_description.lower()
            proto_lower = protocol_name.lower()
            is_dti = any(keyword in desc_lower or keyword in proto_lower for keyword in keywords)

            # Use mrinfo to retrieve DTI-specific information
            dti_axis = extract_mrinfo_axis(series_dir)
            dti_bvalues, dti_shellsizes = extract_mrinfo_shells(series_dir)

            row = [
                subject_dir_short, patient_name, patient_age, patient_sex, study_date,
                series_dir_short, manufacturer, institution, series_description,
                model_name, ethnic_group, repetition_time, echo_time, magnetic_field,
                pixel_bandwidth, protocol_name, phase_encoding, flip_angle,
                dti_axis, dti_bvalues, dti_shellsizes
            ]
            out_rows.append(row)

    # Output the collected DICOM information to "results.csv"
    output_csv = "results.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(out_rows)
    print(f"CSV output completed: {output_csv}")

if __name__ == "__main__":
    main()
