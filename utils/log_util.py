import os
import yaml
from loguru import logger
from typing import Dict

class LogUtil:
    @staticmethod
    def setup_logger(env: str = "dev"):
        """配置日志"""
        # 加载日志配置
        config_path = os.path.join("config", "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        log_config = config.get("log", {})
        
        # 创建日志目录
        log_dir = os.path.dirname(log_config.get("file", "logs/test.log"))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 移除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sink=os.sys.stdout,
            format=log_config.get("format", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"),
            level=log_config.get("level", "INFO")
        )
        
        # 添加文件处理器
        logger.add(
            sink=log_config.get("file", "logs/test.log"),
            format=log_config.get("format", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"),
            level=log_config.get("level", "INFO"),
            rotation="500 MB",
            retention="10 days"
        )

    @staticmethod
    def get_logger():
        """获取日志记录器"""
        return logger 