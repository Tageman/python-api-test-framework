import yaml
import os
from typing import Dict, Any, List
from loguru import logger

class DataParser:
    @staticmethod
    def load_yaml(file_path: str) -> Dict:
        """加载YAML文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载YAML文件失败: {file_path}, 错误: {str(e)}")
            raise

    @staticmethod
    def get_current_env() -> str:
        """获取当前测试环境"""
        config_path = os.path.join("config", "config.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get("env", "dev")
        except Exception:
            return "dev"  # 默认返回开发环境

    @staticmethod
    def load_env_data(env: str = None) -> Dict:
        """加载环境配置数据"""
        if env is None:
            env = DataParser.get_current_env()
            
        env_path = os.path.join("config", f"env_{env}.yaml")
        return DataParser.load_yaml(env_path)

    @staticmethod
    def load_test_cases(case_file: str) -> List[Dict]:
        """加载测试用例"""
        file_path = os.path.join("data", "test_cases", case_file)
        data = DataParser.load_yaml(file_path)
        return data.get("test_cases", [])

    @staticmethod
    def parse_template(template: str, variables: Dict) -> str:
        """解析模板字符串"""
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.error(f"模板变量未定义: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"模板解析失败: {str(e)}")
            raise

    @staticmethod
    def extract_data(response_data: Dict, json_path: str) -> Any:
        """从响应数据中提取指定路径的值"""
        try:
            current = response_data
            for key in json_path.split("."):
                if isinstance(current, dict):
                    current = current[key]
                elif isinstance(current, list):
                    current = current[int(key)]
                else:
                    raise ValueError(f"无法在路径 {json_path} 处提取数据")
            return current
        except Exception as e:
            logger.error(f"数据提取失败: {str(e)}")
            raise

    @staticmethod
    def process_file_info(file_info: Dict, base_variables: Dict) -> Dict:
        """处理文件上传信息
        
        Args:
            file_info: 文件信息字典
            base_variables: 基础变量字典，用于模板替换
            
        Returns:
            处理后的文件信息
        """
        result = {}
        
        # 处理文件路径
        if "path" in file_info:
            file_path = file_info["path"]
            # 替换路径中可能的变量
            if "${" in file_path:
                file_path = DataParser.parse_template(file_path, base_variables)
            result["path"] = file_path
        
        # 处理字段名
        if "field_name" in file_info:
            field_name = file_info["field_name"]
            # 替换字段名中可能的变量
            if "${" in field_name:
                field_name = DataParser.parse_template(field_name, base_variables)
            result["field_name"] = field_name
        
        return result
        
    @staticmethod
    def get_env_test_data(env: str = None) -> Dict:
        """获取当前环境的测试数据
        
        Args:
            env: 环境名称，如果为None则使用当前环境
            
        Returns:
            测试数据字典
        """
        env_data = DataParser.load_env_data(env)
        return env_data.get("test_data", {}) 