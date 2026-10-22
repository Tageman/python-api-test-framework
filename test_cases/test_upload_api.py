import pytest
import allure
import os
from core.api_client import APIClient
from core.assert_tool import AssertTool
from core.data_parser import DataParser
from utils.log_util import LogUtil
from utils.file_util import FileUtil
import requests

# 设置日志
LogUtil.setup_logger()
logger = LogUtil.get_logger()

@allure.epic("API测试")
@allure.feature("文件上传API")
class TestUploadAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件"""
        # 获取当前环境
        self.env = DataParser.get_current_env()
        logger.info(f"当前测试环境: {self.env}")
        
        # 初始化客户端和工具
        self.api_client = APIClient(env=self.env)
        self.assert_tool = AssertTool()
        self.data_parser = DataParser()
        self.test_cases = self.data_parser.load_test_cases("upload_api.yaml")
        
        # 确保测试文件目录存在
        FileUtil.ensure_dir("data/files")
        
        # 获取环境配置
        self.env_config = self.data_parser.load_env_data(self.env)
        self.upload_config = self.env_config.get("upload", {})
        
        # 创建测试文件（如果不存在）
        self._prepare_test_files()
        logger.info("测试用例加载完成")
        
        # 模拟获取token
        self.mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token_for_testing"
    
    @allure.step("准备测试文件")
    def _prepare_test_files(self):
        """准备测试文件"""
        # 创建测试文本文件
        text_file_path = "data/files/test_file.txt"
        if not os.path.exists(text_file_path):
            with open(text_file_path, "w", encoding="utf-8") as f:
                f.write("This is a test file for upload testing.")
            logger.info(f"创建测试文件: {text_file_path}")
            allure.attach("This is a test file for upload testing.", "测试文本文件内容", allure.attachment_type.TEXT)
        
        # 模拟创建测试图片文件（实际使用时请替换为真实图片）
        image_files = ["data/files/image1.jpg", "data/files/image2.jpg"]
        for image_file in image_files:
            if not os.path.exists(image_file):
                with open(image_file, "wb") as f:
                    # 写入简单的伪JPG文件头和内容
                    f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xFF\xDB\x00\x43\x00')
                    f.write(b'A' * 1024)  # 添加一些内容
                logger.info(f"创建测试图片文件: {image_file}")
                allure.attach(f"创建测试图片文件: {image_file}", "测试图片文件", allure.attachment_type.TEXT)
        
        # 检查上传目录是否存在
        upload_dir = self.upload_config.get("upload_dir", "uploads")
        FileUtil.ensure_dir(upload_dir)
        logger.info(f"确保上传目录存在: {upload_dir}")
        allure.attach(f"上传目录路径: {upload_dir}", "上传目录", allure.attachment_type.TEXT)

    @allure.story("单文件上传")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证单文件上传接口的功能")
    @allure.title("测试单文件上传API")
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.xfail(reason="API服务器不可用")
    def test_single_file_upload(self):
        """测试单文件上传"""
        case = next(c for c in self.test_cases if c["name"] == "测试单文件上传")
        
        # 准备请求数据
        request_data = case["request"]
        data = request_data.get("data", {})
        headers = request_data.get("headers", {}).copy()
        
        with allure.step("准备请求数据"):
            # 获取环境变量
            env_test_data = self.data_parser.get_env_test_data(self.env)
            
            # 添加模拟token
            env_vars = {**env_test_data, "token": self.mock_token}
            
            # 替换请求数据中的变量
            for key, value in headers.items():
                if isinstance(value, str) and "${" in value:
                    try:
                        headers[key] = self.data_parser.parse_template(value, env_vars)
                    except KeyError as e:
                        logger.warning(f"变量未定义: {str(e)}, 使用默认值")
                        headers[key] = f"Bearer {self.mock_token}"
            
            allure.attach(str(data), "表单数据", allure.attachment_type.TEXT)
            allure.attach(str(headers), "请求头", allure.attachment_type.TEXT)
            allure.attach(request_data["url"], "请求URL", allure.attachment_type.TEXT)
        
        # 获取文件信息
        file_info = request_data.get("file", {})
        file_path = file_info.get("path")
        field_name = file_info.get("field_name", "file")
        
        with allure.step("准备文件数据"):
            allure.attach(file_path, "文件路径", allure.attachment_type.TEXT)
            allure.attach(field_name, "文件字段名", allure.attachment_type.TEXT)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                allure.attach(str(file_size), "文件大小", allure.attachment_type.TEXT)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read(200)  # 只读取前200个字符
                    allure.attach(file_content, "文件内容预览", allure.attachment_type.TEXT)
        
        try:
            # 发送文件上传请求
            with allure.step("发送文件上传请求"):
                response = self.api_client.upload_file(
                    url=request_data["url"],
                    file_paths=file_path,
                    file_field_name=field_name,
                    form_data=data,
                    headers=headers
                )
                if hasattr(response, 'text'):
                    allure.attach(response.text, "响应内容", allure.attachment_type.TEXT)
            
            # 验证响应
            with allure.step("验证响应结果"):
                for validate in case["validate"]:
                    validate_type = validate["type"]
                    validate_value = validate["value"]
                    
                    with allure.step(f"验证 {validate_type}"):
                        if validate_type == "status_code":
                            self.assert_tool.assert_status_code(response, validate_value)
                            allure.attach(str(response.status_code), "状态码", allure.attachment_type.TEXT)
                        elif validate_type == "json_contains":
                            self.assert_tool.assert_json_contains(response, validate_value)
                        elif validate_type == "json_schema":
                            self.assert_tool.assert_json_schema(response, validate_value)
        except (requests.RequestException, ConnectionError, FileNotFoundError) as e:
            logger.error(f"请求失败: {str(e)}")
            allure.attach(str(e), "错误信息", allure.attachment_type.TEXT)
            pytest.skip(f"跳过测试: {str(e)}")

    @allure.story("多文件上传")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证多文件批量上传接口的功能")
    @allure.title("测试多文件上传API")
    @pytest.mark.api
    @pytest.mark.xfail(reason="API服务器不可用")
    def test_multiple_files_upload(self):
        """测试多文件上传"""
        case = next(c for c in self.test_cases if c["name"] == "测试多文件上传")
        
        # 准备请求数据
        request_data = case["request"]
        data = request_data.get("data", {})
        headers = request_data.get("headers", {}).copy()
        
        with allure.step("准备请求数据"):
            # 获取环境变量
            env_test_data = self.data_parser.get_env_test_data(self.env)
            
            # 添加模拟token
            env_vars = {**env_test_data, "token": self.mock_token}
            
            # 替换请求数据中的变量
            for key, value in headers.items():
                if isinstance(value, str) and "${" in value:
                    try:
                        headers[key] = self.data_parser.parse_template(value, env_vars)
                    except KeyError as e:
                        logger.warning(f"变量未定义: {str(e)}, 使用默认值")
                        headers[key] = f"Bearer {self.mock_token}"
            
            allure.attach(str(data), "表单数据", allure.attachment_type.TEXT)
            allure.attach(str(headers), "请求头", allure.attachment_type.TEXT)
            allure.attach(request_data["url"], "请求URL", allure.attachment_type.TEXT)
        
        # 获取多文件信息
        files_info = request_data.get("files", [])
        file_paths = [file_info.get("path") for file_info in files_info]
        
        # 所有文件使用相同字段名
        field_name = files_info[0].get("field_name", "files") if files_info else "files"
        
        with allure.step("准备文件数据"):
            allure.attach(str(file_paths), "文件路径列表", allure.attachment_type.TEXT)
            allure.attach(field_name, "文件字段名", allure.attachment_type.TEXT)
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    allure.attach(f"{file_path}: {file_size} 字节", f"{os.path.basename(file_path)}大小", allure.attachment_type.TEXT)
        
        try:
            # 发送多文件上传请求
            with allure.step("发送多文件上传请求"):
                response = self.api_client.upload_file(
                    url=request_data["url"],
                    file_paths=file_paths,
                    file_field_name=field_name,
                    form_data=data,
                    headers=headers
                )
                if hasattr(response, 'text'):
                    allure.attach(response.text, "响应内容", allure.attachment_type.TEXT)
            
            # 验证响应
            with allure.step("验证响应结果"):
                for validate in case["validate"]:
                    validate_type = validate["type"]
                    validate_value = validate["value"]
                    
                    with allure.step(f"验证 {validate_type}"):
                        if validate_type == "status_code":
                            self.assert_tool.assert_status_code(response, validate_value)
                            allure.attach(str(response.status_code), "状态码", allure.attachment_type.TEXT)
                        elif validate_type == "json_contains":
                            self.assert_tool.assert_json_contains(response, validate_value)
                        elif validate_type == "json_schema":
                            self.assert_tool.assert_json_schema(response, validate_value)
        except (requests.RequestException, ConnectionError, FileNotFoundError) as e:
            logger.error(f"请求失败: {str(e)}")
            allure.attach(str(e), "错误信息", allure.attachment_type.TEXT)
            pytest.skip(f"跳过测试: {str(e)}") 