import requests
import yaml
import os
from typing import Dict, Any, Optional, List, Union
from loguru import logger

class APIClient:
    def __init__(self, env: str = None):
        self.session = requests.Session()
        self.config = self._load_global_config()
        
        # 如果未指定环境，则使用全局配置中的默认环境
        if env is None:
            env = self.config.get("env", "dev")
            
        self.env = env
        self.env_config = self._load_env_config(env)
        self.base_url = self.env_config.get("base_url", self.config.get("base_url", ""))
        self.timeout = self.config.get("timeout", 30)
        self.retry_times = self.config.get("retry_times", 3)
        self.retry_interval = self.config.get("retry_interval", 1)
        
        logger.info(f"初始化API客户端，环境: {env}, 基础URL: {self.base_url}")

    def _load_global_config(self) -> Dict:
        """加载全局配置文件"""
        config_path = os.path.join("config", "config.yaml")
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载全局配置失败: {str(e)}")
            return {}

    def _load_env_config(self, env: str) -> Dict:
        """加载环境配置文件"""
        env_path = os.path.join("config", f"env_{env}.yaml")
        
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载环境配置失败: {str(e)}")
            return {}

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        full_url = f"{self.base_url}{url}"
        logger.info(f"Request: {method} {full_url}")
        
        for i in range(self.retry_times):
            try:
                response = self.session.request(
                    method=method,
                    url=full_url,
                    timeout=self.timeout,
                    **kwargs
                )
                logger.info(f"Response: {response.status_code}")
                return response
            except Exception as e:
                if i == self.retry_times - 1:
                    raise
                logger.warning(f"Retry {i+1}/{self.retry_times} due to: {str(e)}")
                import time
                time.sleep(self.retry_interval)

    def get(self, url: str, **kwargs) -> requests.Response:
        """GET请求"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """POST请求"""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """PUT请求"""
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """DELETE请求"""
        return self.request("DELETE", url, **kwargs)
        
    def upload_file(self, url: str, file_paths: Union[str, List[str]], file_field_name: str = 'file', form_data: Dict = None, headers: Dict = None) -> requests.Response:
        """文件上传请求
        
        Args:
            url: API路径
            file_paths: 文件路径或路径列表
            file_field_name: 文件字段名，默认为'file'
            form_data: 其他表单数据
            headers: 请求头信息
            
        Returns:
            Response对象
        """
        if not headers:
            headers = {}
        
        if not form_data:
            form_data = {}
            
        files = {}
        
        # 获取当前环境的文件上传配置
        upload_config = self.env_config.get("upload", self.config.get("upload", {}))
        max_size = upload_config.get("max_file_size", 5 * 1024 * 1024)  # 默认5MB
        allowed_extensions = upload_config.get("allowed_extensions", [])
        
        # 处理单个文件或多个文件的情况
        if isinstance(file_paths, str):
            file_paths = [file_paths]
        
        # 验证文件
        for file_path in file_paths:
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
                
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            if max_size and file_size > max_size:
                raise ValueError(f"文件过大: {file_path}, 大小: {file_size}, 限制: {max_size}")
                
            # 验证文件类型
            if allowed_extensions:
                ext = os.path.splitext(file_path)[1].lower().lstrip('.')
                if ext not in allowed_extensions:
                    raise ValueError(f"不支持的文件类型: {file_path}, 类型: {ext}, 允许类型: {allowed_extensions}")
            
        # 如果只有一个文件，使用简单字段名
        if len(file_paths) == 1:
            file_path = file_paths[0]
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                files[file_field_name] = (file_name, f.read())
        # 如果有多个文件，使用数组格式的字段名
        else:
            for i, file_path in enumerate(file_paths):
                file_name = os.path.basename(file_path)
                with open(file_path, 'rb') as f:
                    files[f"{file_field_name}[{i}]"] = (file_name, f.read())
        
        logger.info(f"上传文件: {file_paths} 到 {url}")
        
        return self.post(
            url=url,
            files=files,
            data=form_data,
            headers=headers
        ) 