import sqlite3
import os
from typing import Dict
from datetime import datetime
from config.config import PathConfig


class SQLiteLogger:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(PathConfig.RESULT_DIR, "strategy_logs.sqlite")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # dict-like fetch
        self.cursor = self.conn.cursor()


    def _ensure_table(self, table: str, data: Dict):
        """
        테이블이 존재하는지 확인하고, 없으면 생성합니다.
        """
        cols = ', '.join([f'"{k}" TEXT' for k in data.keys()])
        sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({cols})'
        self.cursor.execute(sql)
        self.conn.commit()


    def insert(self, table: str, data: Dict):
        """
        지정된 테이블에 데이터를 Insert합니다.
        :param table: 테이블 이름
        :param data: 데이터 (딕셔너리 형태)
        """
        self._ensure_table(table, data)
        columns = ', '.join([f'"{k}"' for k in data.keys()])
        placeholders = ', '.join(['?'] * len(data))
        sql = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(data.values()))
        self.conn.commit()


    
    def close(self):
        """
        데이터베이스 연결을 닫습니다.
        """
        self.conn.close()


# 전역 인스턴스 생성
sqlite_logger = SQLiteLogger()


# 테이블명 정의

# 로그 테이블
LOG_TABLES = {
    "score": "score_log",
    "trade": "trading_log",
    "regime": "regime_log",
    "error": "error_log",
}