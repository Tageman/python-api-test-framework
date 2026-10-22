import pytest
import allure
from core.api_client import APIClient
from core.assert_tool import AssertTool
from core.data_parser import DataParser
from utils.log_util import LogUtil
import requests

# 设置日志
LogUtil.setup_logger()
logger = LogUtil.get_logger()

@allure.epic("API测试")
@allure.feature("订单API")
class TestOrderAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置条件"""
        self.api_client = APIClient()
        self.assert_tool = AssertTool()
        self.data_parser = DataParser()
        self.test_cases = self.data_parser.load_test_cases("order_api.yaml")
        logger.info("测试用例加载完成")

    @allure.story("创建订单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证创建订单接口的功能")
    @allure.title("测试创建订单API")
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.xfail(reason="API服务器不可用")
    def test_create_order(self):
        """测试创建订单"""
        case = next(c for c in self.test_cases if c["name"] == "测试创建订单")
        
        # 准备请求数据
        request_data = case["request"]
        data = request_data.get("data", {})
        
        with allure.step("准备请求数据"):
            allure.attach(str(data), "请求数据", allure.attachment_type.TEXT)
            allure.attach(request_data["url"], "请求URL", allure.attachment_type.TEXT)
            allure.attach(request_data["method"], "请求方法", allure.attachment_type.TEXT)
        
        try:
            # 发送请求
            with allure.step("发送API请求"):
                response = self.api_client.request(
                    method=request_data["method"],
                    url=request_data["url"],
                    headers=request_data.get("headers", {}),
                    json=data
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
        except (requests.RequestException, ConnectionError) as e:
            logger.error(f"请求失败: {str(e)}")
            allure.attach(str(e), "错误信息", allure.attachment_type.TEXT)
            pytest.skip(f"跳过测试: API服务器不可用 - {str(e)}")

    @allure.story("获取订单列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证获取订单列表接口的功能")
    @allure.title("测试获取订单列表API")
    @pytest.mark.api
    @pytest.mark.xfail(reason="API服务器不可用")
    def test_get_order_list(self):
        """测试获取订单列表"""
        case = next(c for c in self.test_cases if c["name"] == "测试获取订单列表")
        
        # 准备请求数据
        request_data = case["request"]
        params = request_data.get("params", {})
        
        with allure.step("准备请求数据"):
            allure.attach(str(params), "请求参数", allure.attachment_type.TEXT)
            allure.attach(request_data["url"], "请求URL", allure.attachment_type.TEXT)
            allure.attach(request_data["method"], "请求方法", allure.attachment_type.TEXT)
        
        try:
            # 发送请求
            with allure.step("发送API请求"):
                response = self.api_client.request(
                    method=request_data["method"],
                    url=request_data["url"],
                    headers=request_data.get("headers", {}),
                    params=params
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
                        elif validate_type == "list_length":
                            self.assert_tool.assert_list_length(response, validate_value)
                            allure.attach(str(validate_value), "期望列表长度", allure.attachment_type.TEXT)
        except (requests.RequestException, ConnectionError) as e:
            logger.error(f"请求失败: {str(e)}")
            allure.attach(str(e), "错误信息", allure.attachment_type.TEXT)
            pytest.skip(f"跳过测试: API服务器不可用 - {str(e)}") 