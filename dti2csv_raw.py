#!/usr/bin/env python3

# カレントディレクトリにあるDTIのDICOMファイルの情報をCSVにまとめるスクリプト
# サブディレクトリを含めて検索してくれる
# 条件はSEではじまるディレクトリ内にDICOMファイルがあること
# DTI判定はSeries Description または Protocol Name に以下があること
# "dti", "diff", "ep2d", "dki","dwi"
# 20250219　Kikuko Kaneko

import os
import glob
import csv
import subprocess
import re
import argparse

def get_tag_value(dcmdump_text, tag):
    """
    dcmdump の出力から指定タグ（例："0010,0010"）の角括弧内の値を抽出する
    """
    pattern = re.compile(r'\(' + re.escape(tag) + r'\).*?\[(.*?)\]', re.IGNORECASE)
    m = pattern.search(dcmdump_text)
    return m.group(1).strip() if m else ""

def run_command(cmd):
    """
    コマンドを実行し、出力文字列を返す
    """
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode("utf-8")
    except Exception:
        return ""

def get_first_file(directory):
    """
    ディレクトリ内を再帰的に検索し、最初に見つかったファイルのパスを返す
    """
    files = [f for f in glob.glob(os.path.join(directory, "**"), recursive=True)
             if os.path.isfile(f)]
    return files[0] if files else ""

def extract_mrinfo_axis(series_dir):
    """
    mrinfo <series_dir> の出力から "Dimensions:" 行の最後の数値（軸数）を抽出する
    例: "Dimensions: 128 x 128 x 33 x 100" → "100"
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
    mrinfo <series_dir> -shell_sizes -shell_bvalues の出力から、各シェルの b 値とボリューム数を抽出する
    出力例:
      0 1200 
      1 64 
    ※ 1行目：各シェルの b 値（例：シェル 0 の b 値は 0、シェル 1 の b 値は 1200）
       2行目：各シェルのボリューム数（例：シェル 0 は 1 枚、シェル 1 は 64 枚）
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
    parser = argparse.ArgumentParser(description="DTIのDICOMファイル情報をCSVにまとめるスクリプト")
    parser.add_argument("base_dir", help="被験者ディレクトリが存在するトップディレクトリ")
    args = parser.parse_args()
    if not args.base_dir:
        parser.print_usage()
        exit(1)

    # 出力する CSV のヘッダー
    header = [
        "SubjectDir", "PatientName", "PatientAge", "PatientSex", "StudyDate",
        "SeriesDir", "Manufacturer", "InstitutionName", "SeriesDescription",
        "ModelName", "EthnicGroup", "RepetitionTime", "EchoTime", "MagneticFieldStrength",
        "PixelBandwidth", "ProtocolName", "PhaseEncoding", "FlipAngle",
        "DTI_Axis", "DTI_bvalues", "DTI_ShellSizes",
        "PixelSpacing", "SliceThickness"
    ]
    out_rows = []

    # base_dir 直下の各サブディレクトリを被験者ディレクトリとする
    base_dir = args.base_dir
    for subj_dir in glob.glob(os.path.join(base_dir, "*/")):
        print(f"処理中の被験者: {subj_dir}")

        # 被験者ディレクトリ以下を再帰検索して "SE*" で始まるシリーズディレクトリを取得
        series_dirs = glob.glob(os.path.join(subj_dir, "**", "SE*"), recursive=True)
        for series_dir in series_dirs:
            series_dir_short = os.path.basename(os.path.normpath(series_dir))
            rep_dcm = get_first_file(series_dir)
            if not rep_dcm:
                continue
            rep_dump = run_command(["dcmdump", rep_dcm])

            # 患者情報および撮影条件をDTIのDICOMから取得
            patient_name = get_tag_value(rep_dump, "0010,0010")
            patient_age  = get_tag_value(rep_dump, "0010,1010")
            patient_sex  = get_tag_value(rep_dump, "0010,0040")
            study_date   = get_tag_value(rep_dump, "0008,0020")

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
            pixel_spacing     = get_tag_value(rep_dump, "0028,0030")
            slice_thickness   = get_tag_value(rep_dump, "0018,0050")

            # DTI判定：Series Description または Protocol Name に
            # 指定のキーワードが含まれていなければスキップ
            keywords = ["dti", "diff", "ep2d", "dki","dwi"]
            desc_lower = series_description.lower()
            proto_lower = protocol_name.lower()
            is_dti = any(keyword in desc_lower or keyword in proto_lower for keyword in keywords)
            if not is_dti:
                continue

            # mrinfo を用いて DTI 固有の情報を取得
            dti_axis = extract_mrinfo_axis(series_dir)
            dti_bvalues, dti_shellsizes = extract_mrinfo_shells(series_dir)

            subject_dir_short = os.path.basename(os.path.normpath(subj_dir))
            row = [
                subject_dir_short, patient_name, patient_age, patient_sex, study_date,
                series_dir_short, manufacturer, institution, series_description,
                model_name, ethnic_group, repetition_time, echo_time, magnetic_field,
                pixel_bandwidth, protocol_name, phase_encoding, flip_angle,
                dti_axis, dti_bvalues, dti_shellsizes,
                pixel_spacing, slice_thickness
            ]
            out_rows.append(row)

    # DTI の情報のみをまとめた CSV を "dti_results.csv" として出力
    output_csv = "dti_results.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(out_rows)
    print(f"CSV出力完了: {output_csv}")

if __name__ == "__main__":
    main()

