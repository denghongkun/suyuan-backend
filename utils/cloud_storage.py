import uuid
from qcloud_cos import CosConfig, CosS3Client
from config import Config
import logging

class CloudStorage:
    def __init__(self):
        if not all([Config.COS_SECRET_ID, Config.COS_SECRET_KEY, Config.COS_BUCKET]):
            raise ValueError("腾讯云COS配置不完整")
            
        self.config = CosConfig(
            Region=Config.COS_REGION,
            SecretId=Config.COS_SECRET_ID,
            SecretKey=Config.COS_SECRET_KEY
        )
        self.client = CosS3Client(self.config)
        self.bucket = Config.COS_BUCKET
    
    def upload_file(self, file_obj, file_extension):
        """上传文件到腾讯云COS"""
        try:
            # 生成唯一文件名
            filename = f"materials/{uuid.uuid4().hex}{file_extension}"
            
            # 重置文件指针
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            # 上传文件
            response = self.client.put_object(
                Bucket=self.bucket,
                Body=file_obj,
                Key=filename,
                EnableMD5=False
            )
            
            # 返回文件URL
            file_url = f"https://{self.bucket}.cos.{Config.COS_REGION}.myqcloud.com/{filename}"
            return {
                'success': True,
                'file_url': file_url,
                'filename': filename
            }
            
        except Exception as e:
            logging.error(f"文件上传失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, filename):
        """从云端删除文件"""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=filename
            )
            return True
        except Exception as e:
            logging.error(f"文件删除失败: {str(e)}")
            return False