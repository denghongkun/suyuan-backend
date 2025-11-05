import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yanshuimitao-secret-key'
    
    # 云数据库MySQL配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 豆包API配置
    ARK_API_KEY = os.environ.get('ARK_API_KEY')
    DOUBAO_MODEL = os.environ.get('DOUBAO_MODEL')
    DOUBAO_BASE_URL = os.environ.get('DOUBAO_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
    
    # 腾讯云COS配置
    COS_SECRET_ID = os.environ.get('COS_SECRET_ID')
    COS_SECRET_KEY = os.environ.get('COS_SECRET_KEY')
    COS_REGION = os.environ.get('COS_REGION', 'ap-guangzhou')
    COS_BUCKET = os.environ.get('COS_BUCKET')