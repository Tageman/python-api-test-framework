import pymysql
import yaml
import os
from typing import Dict, List, Any
from loguru import logger

class DBClient:
    def __init__(self, env: str = "dev"):
        self.connection = None
        self._load_config(env)

    def _load_config(self, env: str):
        """加载数据库配置"""
        config_path = os.path.join("config", f"env_{env}.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        self.db_config = config.get("db", {})

    def connect(self):
        """连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.db_config.get("host"),
                port=self.db_config.get("port"),
                user=self.db_config.get("user"),
                password=self.db_config.get("password"),
                database=self.db_config.get("database"),
                charset="utf8mb4"
            )
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")

    def execute_query(self, sql: str, params: tuple = None) -> List[Dict]:
        """执行查询SQL"""
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"SQL执行失败: {str(e)}")
            raise

    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新SQL"""
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                self.connection.commit()
                return affected_rows
        except Exception as e:
            self.connection.rollback()
            logger.error(f"SQL执行失败: {str(e)}")
            raise

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect() 