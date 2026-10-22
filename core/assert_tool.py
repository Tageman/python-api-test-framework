from typing import Any, Dict, List
import json
from loguru import logger

class AssertTool:
    @staticmethod
    def assert_status_code(response, expected_code: int):
        """断言状态码"""
        assert response.status_code == expected_code, \
            f"状态码不匹配，期望: {expected_code}, 实际: {response.status_code}"

    @staticmethod
    def assert_json_contains(response, expected_data: Dict):
        """断言JSON响应包含指定数据"""
        response_data = response.json()
        for key, value in expected_data.items():
            assert key in response_data, f"响应中缺少键: {key}"
            assert response_data[key] == value, \
                f"值不匹配，键: {key}, 期望: {value}, 实际: {response_data[key]}"

    @staticmethod
    def assert_json_schema(response, schema: Dict):
        """断言JSON响应符合指定schema"""
        response_data = response.json()
        for key, value_type in schema.items():
            assert key in response_data, f"响应中缺少键: {key}"
            assert isinstance(response_data[key], value_type), \
                f"类型不匹配，键: {key}, 期望类型: {value_type}, 实际类型: {type(response_data[key])}"

    @staticmethod
    def assert_list_length(response, expected_length: int):
        """断言列表长度"""
        response_data = response.json()
        assert isinstance(response_data, list), "响应不是列表类型"
        assert len(response_data) == expected_length, \
            f"列表长度不匹配，期望: {expected_length}, 实际: {len(response_data)}"

    @staticmethod
    def assert_response_time(response, max_time: float):
        """断言响应时间"""
        assert response.elapsed.total_seconds() <= max_time, \
            f"响应时间超过限制，最大允许: {max_time}秒, 实际: {response.elapsed.total_seconds()}秒" 