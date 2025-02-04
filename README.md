# dicom2csv

Scripts to get information from dicom tag and create a CSV file.

- You can list various subject attributes, scanner information, and imaging parameters from DICOM file data.
- For DTI dicom, you can get b values and shell_sizes using "mrinfo" command of MRtrix3.
- Subject directories are searched recursively.
- A series directory must have the name beginning with "SE000".
- When you have only raw dicom files, `dcm2csv_raw.py` works well.

example code: You can modify the path as needed.
```
git clone https://github.com/Kikubernetes/dicom2csv.git
cd your/path/to/dicom/directory
cp ~/git/dicom2csv/dcm2csv_raw.py .
./dcm2csv_raw.py
```

- If you have mixed files (DICOM and NIfTI, for example), you may want to organize dicom files into the directory named "org_data" and use `dcm2csv.py` (for all series) or `dti2csv.py` (DTI only).

### Requirements
- dcmdump
- MRtrix3(for DTI)
