import logging
import os
import csv
from datetime import datetime
from config.config import PathConfig



def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)

    # Log 폴더 없으면 생성
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def write_log(message: str, filename: str):
    """
    로그 메시지를 텍스트 파일에 기록합니다.
    :param message: 로그 메시지
    :param filename: 로그 파일 이름
    """
    os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)

    # ✅ log_dir과 filename을 합쳐서 경로 구성
    file_path = os.path.join(PathConfig.RESULT_DIR, filename)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def write_log_csv(row:dict, filename: str):
    """
    로그 메시지를 CSV 파일에 기록합니다.
    :param row: 로그 메시지 (딕셔너리 형태)
    :param filename: 로그 파일 이름
    """
    os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)

    # ✅ log_dir과 filename을 합쳐서 경로 구성
    file_path = os.path.join(PathConfig.RESULT_DIR, filename)

    # CSV 파일에 헤더가 없으면 추가
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode='a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# def write_log_csv(data, filename: str):
#     """
#     stats(Series/_Stats) 또는 일반 dict 데이터를 세로형 CSV로 저장
#     """
#     from pandas import Series

#     os.makedirs(PathConfig.RESULT_DIR, exist_ok=True)
#     path = os.path.join(PathConfig.RESULT_DIR, filename)

#     # dict 또는 Series 처리
#     if isinstance(data, dict):
#         series_data = Series(data)
#     elif hasattr(data, "to_dict"):
#         series_data = Series(data.to_dict())
#     else:
#         raise ValueError("지원하지 않는 타입입니다. stats, Series, dict만 허용됩니다.")

#     df = series_data.reset_index()
#     df.columns = ["항목", "값"]
#     df.to_csv(path, index=False, encoding="utf-8-sig")
