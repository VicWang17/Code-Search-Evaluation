# -*- coding: utf-8 -*-
"""
代码检索API客户端
用于调用http://localhost:8000/api/search/code_by_hyde接口
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Any

class CodeSearchAPIClient:
    """代码检索API客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化API客户端
        
        Args:
            config: API配置字典，包含base_url, endpoint, timeout等
        """
        self.base_url = config.get("base_url", "http://localhost:8000")
        self.endpoint = config.get("endpoint", "/api/search/code_by_hyde")
        self.project_id = config.get("project_id", "5")
        self.limit = config.get("limit", 10)
        self.timeout = config.get("timeout", 30)
        
        # 构建完整的API URL
        self.api_url = f"{self.base_url}{self.endpoint}"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CodeSearchEvaluator/1.0'
        })
    
    def search_code(self, query: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        执行代码检索
        
        Args:
            query: 搜索查询语句
            limit: 返回结果数量限制
            
        Returns:
            Dict: API返回的结果
        """
        # 准备请求参数
        params = {
            "q": query,
            "limit": limit or self.limit,
            "project_id": self.project_id
        }
        
        try:
            self.logger.info(f"发起代码检索请求: {query}")
            self.logger.debug(f"请求参数: {params}")
            
            # 发送POST请求
            response = self.session.post(
                self.api_url,
                json=params,
                timeout=self.timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            self.logger.info(f"检索成功，返回 {len(result.get('results', []))} 个结果")
            return result
            
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {query}")
            return {"error": "请求超时", "results": []}
            
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接错误: 无法连接到 {self.api_url}")
            return {"error": "连接错误", "results": []}
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP错误 {e.response.status_code}: {query}")
            return {"error": f"HTTP错误 {e.response.status_code}", "results": []}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求异常: {e}")
            return {"error": str(e), "results": []}
            
        except ValueError as e:
            self.logger.error(f"JSON解析错误: {e}")
            return {"error": "响应格式错误", "results": []}
    
    def search_code_with_retry(self, query: str, max_retries: int = 3, 
                              retry_delay: float = 1.0) -> Dict[str, Any]:
        """
        带重试机制的代码检索
        
        Args:
            query: 搜索查询语句
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
            
        Returns:
            Dict: API返回的结果
        """
        for attempt in range(max_retries + 1):
            result = self.search_code(query)
            
            # 如果成功或者是最后一次尝试，直接返回
            if "error" not in result or attempt == max_retries:
                return result
            
            # 等待后重试
            self.logger.warning(f"第 {attempt + 1} 次请求失败，{retry_delay}秒后重试")
            time.sleep(retry_delay)
        
        return result
    
    def batch_search(self, queries: List[str], 
                    delay_between_requests: float = 0.5) -> List[Dict[str, Any]]:
        """
        批量代码检索
        
        Args:
            queries: 查询列表
            delay_between_requests: 请求间隔时间（秒）
            
        Returns:
            List[Dict]: 批量检索结果
        """
        results = []
        
        for i, query in enumerate(queries):
            self.logger.info(f"执行批量检索 {i+1}/{len(queries)}: {query}")
            
            result = self.search_code_with_retry(query)
            results.append({
                "query": query,
                "result": result,
                "timestamp": time.time()
            })
            
            # 避免请求过于频繁
            if i < len(queries) - 1:
                time.sleep(delay_between_requests)
        
        return results
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 发送一个简单的测试请求
            test_result = self.search_code("test", limit=1)
            
            if "error" not in test_result:
                self.logger.info("API连接测试成功")
                return True
            else:
                self.logger.error(f"API连接测试失败: {test_result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"API连接测试异常: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, str]:
        """
        获取API信息
        
        Returns:
            Dict: API配置信息
        """
        return {
            "api_url": self.api_url,
            "project_id": self.project_id,
            "limit": str(self.limit),
            "timeout": f"{self.timeout}s"
        }

# 工厂函数
def create_api_client(config: Dict[str, Any]) -> CodeSearchAPIClient:
    """
    创建API客户端实例
    
    Args:
        config: API配置
        
    Returns:
        CodeSearchAPIClient: 客户端实例
    """
    return CodeSearchAPIClient(config)

if __name__ == "__main__":
    # 测试代码
    test_config = {
        "base_url": "http://localhost:8000",
        "endpoint": "/api/search/code_by_hyde",
        "project_id": "5",
        "limit": 10,
        "timeout": 30
    }
    
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建客户端
    client = create_api_client(test_config)
    
    # 测试连接
    if client.test_connection():
        print("API连接正常")
        
        # 测试检索
        result = client.search_code("积分商品列表样式")
        print(f"检索结果: {len(result.get('results', []))} 个")
    else:
        print("API连接失败") 