class APIError(Exception):
    """API相关异常基类"""
    pass

class RequestError(APIError):
    """请求异常"""
    pass

class ResponseError(APIError):
    """响应异常"""
    pass

class AssertError(APIError):
    """断言异常"""
    pass

class ConfigError(APIError):
    """配置异常"""
    pass

class DataError(APIError):
    """数据异常"""
    pass 