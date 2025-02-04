# dicom2csv

Scripts to get information from dicom tag and create a CSV file under the current directory.
- Sub directories are searched recursively.
- A series directory must have the name beginning with "SE000"
- For DTI dicom, you can get b values and shell_sizes using "mrinfo" command of MRtrix3.
- When you have only raw dicom files, dcm2csv_raw.py works well.
- If you have mixed files(DICOM and NIfTI, for example), you may want to get dicom files into org_data directory and use dcm2csv.py(for all series) or dti2csv.py(DTI only).

### prerequisite
- dcmdump
- MRtrix3(for DTI)
