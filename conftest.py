import pytest
import os
from utils.log_util import LogUtil
from utils.file_util import FileUtil

def ensure_dirs_exist():
    """确保必要的目录存在"""
    dirs = [
        "logs",
        "reports",
        "data/files",
        "data/test_cases",
        "uploads",
        "uploads/dev",
        "uploads/test", 
        "uploads/prod"
    ]
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """测试环境初始化"""
    # 创建必要的目录
    ensure_dirs_exist()
    
    # 设置日志
    LogUtil.setup_logger()
    logger = LogUtil.get_logger()
    logger.info("测试环境初始化完成")

@pytest.fixture(scope="function")
def test_data():
    """测试数据"""
    return {
        "user": {
            "username": "test_user",
            "password": "test_password"
        },
        "order": {
            "order_id": "TEST_ORDER_001"
        }
    }

@pytest.fixture(scope="function")
def clean_test_data():
    """清理测试数据"""
    yield
    # 在这里添加清理测试数据的代码
    pass 