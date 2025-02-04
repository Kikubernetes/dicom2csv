# dicom2csv

DICOMタグから情報を取得し、現在のディレクトリにCSVファイルを作成するスクリプトです。  

- サブディレクトリは再帰的に検索されます。  
- シリーズのディレクトリ名は `"SE000"` で始まる必要があります。  
- DTIのDICOMについては、MRtrix3の `mrinfo` コマンドを使用して **b値** や **shell_sizes** を取得できます。  
- **DICOMファイルのみ** が存在する場合は `dcm2csv_raw.py` が適しています。  
- **DICOMとNIfTIなどが混在** している場合は、DICOMファイルを `org_data` ディレクトリにまとめ、全シリーズの情報を使うには`dcm2csv.py` を、DTIのみほしい場合は `dti2csv.py` を使用します。

## 必要なソフトウェア
- `dcmdump`  
- MRtrix3（DTI用）  
