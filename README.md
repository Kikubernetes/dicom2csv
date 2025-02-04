# dicom2csv

Scripts to gather information from dicom tag and summarize them into a CSV file for each series.

- You can list various subject attributes, scanner information, and imaging parameters from DICOM file data.
- For DTI dicom, you can also get b values and shell_sizes using "mrinfo" command of MRtrix3.
- Subdirectories are searched recursively.
- Series DICOM files must be inside a directory that starts with "SE000".
- When you have only raw dicom files, `dcm2csv_raw.py` works well.

example code: You can modify the path as needed.
```
git clone https://github.com/Kikubernetes/dicom2csv.git
cd your/path/to/dicom/directory
cp ~/git/dicom2csv/dcm2csv_raw.py .
./dcm2csv_raw.py
```
- Output the collected DICOM information to "results.csv".
  
- If you have mixed files (DICOM and NIfTI, for example), you may want to organize dicom files into the directory named "org_data" and use `dcm2csv.py` (for all series) or `dti2csv.py` (DTI only).

### Requirements
- dcmdump
- MRtrix3(for DTI)
