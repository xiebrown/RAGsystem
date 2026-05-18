"""数据库配置模块

本模块定义了数据库相关的配置类，包括向量数据库Milvus和缓存数据库Redis的配置。
"""

from pydantic_settings import BaseSettings
from settings import settings


class DatabaseSettings(BaseSettings):
    """数据库配置类
    
    用于集中管理项目中使用的各种数据库连接配置，包括：
    - Milvus向量数据库：用于存储和检索向量数据
    - Redis缓存数据库：用于缓存和Celery任务队列
    - 可选的元数据SQL数据库
    
    所有配置项均从全局settings对象中读取。
    
    Attributes:
        MILVUS_HOST (str): Milvus服务器主机地址
        MILVUS_PORT (int): Milvus服务器端口号
        MILVUS_COLLECTION_NAME (str): Milvus集合名称，用于存储向量数据
        MILVUS_DIMENSION (int): Milvus向量维度，定义嵌入向量的维度大小
        REDIS_URL (str): Redis数据库连接URL，用于缓存和消息队列
    """
    
    # Milvus Configuration
    MILVUS_HOST: str = settings.MILVUS_HOST
    MILVUS_PORT: int = settings.MILVUS_PORT
    MILVUS_COLLECTION_NAME: str = settings.MILVUS_COLLECTION_NAME
    MILVUS_DIMENSION: int = settings.MILVUS_DIMENSION
    
    # Redis Configuration (Cache & Celery)
    REDIS_URL: str = settings.REDIS_URL

    # Metadata DB (Optional, if using SQL database for metadata)
    # DATABASE_URL: str = "sqlite:///./data/metadata.db"


# 创建数据库配置实例，供其他模块导入使用
db_settings = DatabaseSettings()
