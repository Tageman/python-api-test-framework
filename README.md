# API 接口测试框架

一个基于 Python 的通用型接口测试框架，支持多环境配置、数据驱动测试和文件上传测试。

## 特性

- **多环境支持**：开发环境、测试环境和生产环境的配置分离
- **数据驱动测试**：使用 YAML 文件管理测试用例和测试数据
- **文件上传测试**：支持单文件和多文件上传测试
- **灵活的配置**：支持全局配置和环境特定配置
- **丰富的断言**：提供多种断言方式验证 API 响应
- **美观的报告**：支持 Allure 报告和 HTML 报告
- **日志管理**：完整的日志记录功能
- **可扩展性**：易于添加新的测试用例和功能

## 目录结构

```
api_test_framework/
├── config/                   # 配置目录
│   ├── config.yaml          # 全局配置
│   ├── env_dev.yaml         # 开发环境配置
│   ├── env_test.yaml        # 测试环境配置
│   └── env_prod.yaml        # 生产环境配置
├── data/                     # 测试数据
│   ├── files/               # 测试文件
│   └── test_cases/          # YAML用例数据
│       ├── user_api.yaml
│       ├── order_api.yaml
│       └── upload_api.yaml
├── test_cases/              # pytest测试用例
│   ├── __init__.py
│   ├── test_user_api.py
│   ├── test_order_api.py
│   └── test_upload_api.py
├── core/                    # 框架核心组件
│   ├── __init__.py
│   ├── api_client.py        # 请求封装
│   ├── assert_tool.py       # 断言工具
│   ├── data_parser.py       # 数据解析器
│   └── exception.py         # 自定义异常
├── utils/                   # 工具类
│   ├── __init__.py
│   ├── db_client.py         # 数据库操作
│   ├── log_util.py          # 日志工具
│   └── file_util.py         # 文件操作
├── conftest.py              # pytest fixture
├── pytest.ini               # pytest配置
├── run_tests.py             # 测试运行脚本
├── requirements.txt         # 依赖库
└── reports/                 # 测试报告（自动生成）
    ├── report.html          # HTML测试报告
    ├── allure-results/      # Allure测试结果
    └── allure-report/       # Allure测试报告
```

## 安装依赖

```bash
pip install -r requirements.txt
```

此外，如需生成 Allure 报告，需要安装 Allure 命令行工具：
- 访问 https://docs.qameta.io/allure/ 了解安装方法

## 运行测试

### 命令行运行

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest test_cases/test_user_api.py

# 使用标记运行测试
pytest -m smoke
```

### 使用运行脚本

```bash
# 运行所有测试（默认开发环境）
python run_tests.py

# 指定环境
python run_tests.py --env test

# 指定运行标记
python run_tests.py --markers smoke

# 指定报告路径
python run_tests.py --report-path custom_reports
```

## 添加新的测试用例

1. 在 `data/test_cases/` 目录下创建或编辑 YAML 文件
2. 按照以下格式定义测试用例：

```yaml
test_cases:
  - name: "测试用例名称"
    description: "测试用例描述"
    request:
      method: "GET/POST/PUT/DELETE"
      url: "/api/path"
      headers:
        Content-Type: "application/json"
      data:
        key: "value"
    validate:
      - type: "status_code"
        value: 200
      - type: "json_contains"
        value:
          key: "expected_value"
```

3. 在 `test_cases/` 目录下创建或编辑对应的测试类和方法

## 配置管理

### 全局配置 (config.yaml)

```yaml
# 全局配置
base_url: "http://api.example.com"
timeout: 30
retry_times: 3

# 环境配置
env: "dev"  # 默认环境，可选：dev, test, prod

# 日志配置
log:
  level: "INFO"
  file: "logs/test.log"
```

### 环境特定配置 (env_dev.yaml, env_test.yaml, env_prod.yaml)

```yaml
# 环境配置
base_url: "http://dev-api.example.com"

# 数据库配置
db:
  host: "localhost"
  port: 3306
  user: "test_user"
  password: "${TEST_PASSWORD}"
  
# 测试数据
test_data:
  user:
    username: "test_user"
```

## 测试报告

运行测试后，报告将自动生成在 `reports/` 目录下：

- `reports/report.html`：HTML 报告
- `reports/allure-report/`：Allure 报告（需要安装 Allure 命令行工具）

## 编写测试

### 基本测试示例

```python
@allure.story("用户登录")
@pytest.mark.api
def test_user_login(self):
    """测试用户登录"""
    case = next(c for c in self.test_cases if c["name"] == "测试用户登录")
    
    # 准备请求数据
    request_data = case["request"]
    data = request_data.get("data", {})
    
    # 发送请求
    response = self.api_client.request(
        method=request_data["method"],
        url=request_data["url"],
        headers=request_data.get("headers", {}),
        json=data
    )
    
    # 验证响应
    for validate in case["validate"]:
        validate_type = validate["type"]
        validate_value = validate["value"]
        
        if validate_type == "status_code":
            self.assert_tool.assert_status_code(response, validate_value)
        elif validate_type == "json_contains":
            self.assert_tool.assert_json_contains(response, validate_value)
```

### 文件上传测试示例

```python
def test_file_upload(self):
    """测试文件上传"""
    response = self.api_client.upload_file(
        url="/api/upload",
        file_paths="data/files/test_file.txt",
        file_field_name="file",
        form_data={"description": "测试文件"},
        headers={"Authorization": "Bearer token"}
    )
    
    self.assert_tool.assert_status_code(response, 200)
```

## 许可证

MIT 
