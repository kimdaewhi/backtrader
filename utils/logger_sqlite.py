import sqlite3
import os
from typing import Dict, List
from config.config import PathConfig, backtesting_config


class SQLiteLogger:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(PathConfig.RESULT_DIR, f"{backtesting_config.SYMBOL}_{PathConfig.TODAY}_logs.sqlite")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # dict-like fetch
        self.cursor = self.conn.cursor()
        self._in_transaction = False

    def __enter__(self):
        """ with 문을 사용하여 SQLiteLogger를 사용할 수 있도록 합니다. """
        return self
    

    def __exit__(self, *args):
        """ with 문이 끝나면 자동으로 커밋하고 연결을 닫습니다. """
        if self._in_transaction:
            self.commit()
        self.close()

    
    def begin(self):
        """ 트랜잭션을 시작합니다. """
        if not self._in_transaction:
            self.conn.execute('BEGIN')
            self._in_transaction = True
        else:
            raise Exception("트랜잭션이 이미 시작되었습니다.")


    def commit(self):
        """ 현재 트랜잭션을 커밋합니다."""
        self.conn.commit()
        self._in_transaction = False


    def _ensure_table(self, table: str, data: Dict):
        """
        테이블이 존재하는지 확인하고, 없으면 생성합니다.
        """
        def infer_type(value):
            if isinstance(value, int):
                return 'INTEGER'
            elif isinstance(value, float):
                return 'REAL'
            else:
                return 'TEXT'
            
        cols = ', '.join([f'"{k}" TEXT' for k in data.keys()])
        sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({cols})'
        self.cursor.execute(sql)
        self.conn.commit()


    def _create_index(self, table: str, columns: str):
        """
        지정된 테이블에 인덱스를 자동으로 생성합니다.
        :param table: 테이블 이름
        :param columns: 인덱스를 생성할 열 이름 (콤마로 구분된 문자열)
        """
        self.cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{table}_{columns} ON "{table}"("{columns}")')


    def insert(self, table: str, data: Dict):
        """
        지정된 테이블에 데이터를 Insert합니다.
        :param table: 테이블 이름
        :param data: 데이터 (딕셔너리 형태)
        """
        # self._ensure_table(table, data)
        columns = ', '.join([f'"{k}"' for k in data.keys()])
        placeholders = ', '.join(['?'] * len(data))
        sql = f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(data.values()))
        self.conn.commit()


    def insert_many(self, table: str, data_list: List[Dict]):
        """
        지정된 테이블에 여러 개의 데이터를 Insert합니다.
        :param table: 테이블 이름
        :param data_list: 데이터 리스트 (딕셔너리 형태)
        """
        if not data_list:
            return
        
        self._ensure_table(table, data_list[0])
        colums = ', '.join([f'"{k}"' for k in data_list[0].keys()])
        placeholders = ', '.join(['?'] * len(data_list[0]))
        sql = f'INSERT INTO "{table}" ({colums}) VALUES ({placeholders})'
        self.cursor.executemany(sql, [list(d.values()) for d in data_list])
        if not self._in_transaction:
            self.conn.commit()


    def reset_table(self, table: str):
        """
        지정된 테이블을 초기화합니다.
        :param table: 테이블 이름
        """
        sql = f'DROP TABLE IF EXISTS "{table}"'
        self.cursor.execute(sql)
        self.conn.commit()
        print(f"🗑️  {table} 테이블이 초기화되었습니다.")

    
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