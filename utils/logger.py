import logging
import os
from datetime import datetime


today = datetime.now().strftime("%Y%m%d")

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
    from datetime import datetime
    import os

    today = datetime.now().strftime("%Y%m%d")
    log_dir = os.path.join("results", f"result_{today}")  # ✅ result_20250328
    os.makedirs(log_dir, exist_ok=True)

    # ✅ log_dir과 filename을 합쳐서 경로 구성
    file_path = os.path.join(log_dir, filename)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")