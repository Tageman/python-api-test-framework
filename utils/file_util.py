import os
import shutil
import json
import mimetypes
import hashlib
from typing import Dict, Any, List, Tuple
from loguru import logger

class FileUtil:
    @staticmethod
    def ensure_dir(directory: str):
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"创建目录: {directory}")

    @staticmethod
    def read_json(file_path: str) -> Dict:
        """读取JSON文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取JSON文件失败: {file_path}, 错误: {str(e)}")
            raise

    @staticmethod
    def write_json(file_path: str, data: Dict):
        """写入JSON文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"写入JSON文件成功: {file_path}")
        except Exception as e:
            logger.error(f"写入JSON文件失败: {file_path}, 错误: {str(e)}")
            raise

    @staticmethod
    def copy_file(src: str, dst: str):
        """复制文件"""
        try:
            shutil.copy2(src, dst)
            logger.info(f"复制文件成功: {src} -> {dst}")
        except Exception as e:
            logger.error(f"复制文件失败: {src} -> {dst}, 错误: {str(e)}")
            raise

    @staticmethod
    def delete_file(file_path: str):
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"删除文件成功: {file_path}")
        except Exception as e:
            logger.error(f"删除文件失败: {file_path}, 错误: {str(e)}")
            raise

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"获取文件大小失败: {file_path}, 错误: {str(e)}")
            raise
            
    @staticmethod
    def get_file_mime_type(file_path: str) -> str:
        """获取文件的MIME类型"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # 如果无法确定，返回默认类型
            return 'application/octet-stream'
        return mime_type
    
    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法，支持'md5'、'sha1'、'sha256'
            
        Returns:
            文件哈希值的十六进制字符串
        """
        try:
            hash_obj = None
            if algorithm.lower() == 'md5':
                hash_obj = hashlib.md5()
            elif algorithm.lower() == 'sha1':
                hash_obj = hashlib.sha1()
            elif algorithm.lower() == 'sha256':
                hash_obj = hashlib.sha256()
            else:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
                
            with open(file_path, 'rb') as f:
                # 分块读取以处理大文件
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
                    
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"计算文件哈希值失败: {file_path}, 错误: {str(e)}")
            raise
            
    @staticmethod
    def create_test_file(file_path: str, content: str = None, size_bytes: int = None):
        """创建测试文件
        
        Args:
            file_path: 文件路径
            content: 文件内容，如果未指定则根据size_bytes生成随机内容
            size_bytes: 文件大小（字节），仅当content未指定时有效
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'wb') as f:
                if content:
                    f.write(content.encode('utf-8'))
                elif size_bytes:
                    # 生成指定大小的随机内容
                    chunk_size = min(size_bytes, 8192)
                    remaining = size_bytes
                    
                    while remaining > 0:
                        write_size = min(remaining, chunk_size)
                        f.write(os.urandom(write_size))
                        remaining -= write_size
                else:
                    # 默认创建1KB的随机内容
                    f.write(os.urandom(1024))
                    
            logger.info(f"创建测试文件成功: {file_path}")
        except Exception as e:
            logger.error(f"创建测试文件失败: {file_path}, 错误: {str(e)}")
            raise 