from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Material(db.Model):
    __tablename__ = 'materials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    
    # 基础元数据
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # AI生成的关键词（现在支持所有农作物）
    ai_keywords = db.Column(db.Text, default='')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'upload_time': self.upload_time.isoformat(),
            'ai_keywords': self.ai_keywords
        }
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        if 'upload_time' not in kwargs:
            kwargs['upload_time'] = datetime.utcnow()
        super().__init__(**kwargs)