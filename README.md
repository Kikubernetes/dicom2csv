# dicom2csv

Scripts to gather information from dicom tag and summarize them into a CSV file for each series.

- You can list various subject attributes, scanner information, and imaging parameters from DICOM file data.
- For DTI dicom, you can also get b values and shell_sizes(MRtrix3 is required).
- Subdirectories are searched recursively.
- Series DICOM files must be inside a directory that starts with "SE".

example code: You can modify the path as needed.
```
git clone https://github.com/Kikubernetes/dicom2csv.git
cd path/to/dicom2csv
./dcm2csv_raw.py your/path/to/dicom/directory
```
- Output the collected DICOM information to "results.csv".
  
- If you want csv of DTI only, you can run dti2csv_raw.py. If you want csv of T1w only, t1w2csv_raw.py is suitable.
- If you have mixed files (DICOM and NIfTI, for example), you may want to organize dicom files into the directory named "org_data" and use `dcm2csv.py` (for all series) or `dti2csv.py` (DTI only).

### Requirements
- dcmdump
- MRtrix3(for b value)
