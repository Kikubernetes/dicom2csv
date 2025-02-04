# dicom2csv

DICOMタグから情報を取得し、CSVファイルを作成するスクリプトです。  


- DICOMファイルの情報からさまざまな被験者属性、スキャナ情報、撮像パラメータを一覧にすることができます。
- DTIのDICOMについては、MRtrix3の `mrinfo` コマンドを使用して **b値** や **軸数** を取得できます。
- サブディレクトリは再帰的に検索されます。  
- シリーズのディレクトリ名は "SE000" で始まる必要があります。
- **DICOMファイルのみ** が存在する場合は `dcm2csv_raw.py` が適しています。
  
使用例：適宜パス名を変更してください。
```
git clone https://github.com/Kikubernetes/dicom2csv.git
cd your/path/to/dicom/directory
cp ~/git/dicom2csv/dcm2csv_raw.py .
./dcm2csv_raw.py
```
カレントディレクトリに"results.csv"が出力されます。

- **DICOMとNIfTIなど、ファイルが混在** している場合は、DICOMファイルを `org_data` という名前のディレクトリにまとめ、全シリーズの情報を使うには`dcm2csv.py` を、DTIのみほしい場合は `dti2csv.py` を使用してください。

## 必要なソフトウェア
- dcmdump  
- MRtrix3（DTI用）  
