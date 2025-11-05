from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

from config import Config
from models import db, Material
from utils.cloud_storage import CloudStorage
from utils.doubao_ai_generator import DoubaoAIGenerator  # 导入豆包生成器

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

db.init_app(app)

# 初始化服务
try:
    cloud_storage = CloudStorage()
    ai_generator = DoubaoAIGenerator()  # 使用豆包AI生成器
    storage_available = True
except Exception as e:
    print(f"服务初始化失败: {e}")
    storage_available = False
    cloud_storage = None
    ai_generator = None

@app.route('/api/materials/<material_id>', methods=['GET'])
def get_material(material_id):
    """获取单个素材详情"""
    try:
        material = Material.query.get(material_id)
        
        if not material:
            return jsonify({'error': '素材不存在'}), 404
            
        return jsonify({
            'material': material.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_materials():
    """上传素材文件到云端并调用豆包大模型生成关键词"""
    if not storage_available:
        return jsonify({'error': '云存储服务不可用'}), 500
        
    try:
        if 'files' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        files = request.files.getlist('files')
        # 移除了 location 和 activity_type 的获取
        
        uploaded_materials = []
        
        for file in files:
            if file and file.filename:
                file_ext = os.path.splitext(file.filename)[1].lower()
                
                upload_result = cloud_storage.upload_file(file.stream, file_ext)
                if not upload_result['success']:
                    continue
                
                file_type = 'video' if file_ext in ['.mp4', '.mov', '.avi'] else 'image'
                
                if hasattr(file.stream, 'seek'):
                    file.stream.seek(0, 2)
                    file_size = file.stream.tell()
                    file.stream.seek(0)
                else:
                    file_size = 0
                
                # 创建记录（移除了 location 和 activity_type）
                material = Material(
                    filename=file.filename,
                    file_type=file_type,
                    file_path=upload_result['file_url'],
                    file_size=file_size
                    # 移除了 location 和 activity_type
                )
                
                # 调用豆包大模型生成关键词
                if ai_generator:
                    if file_type == 'image':
                        ai_result = ai_generator.generate_keywords_from_image_url(upload_result['file_url'])
                    else:
                        ai_result = ai_generator.generate_keywords_from_video(upload_result['file_url'])
                    
                    material.ai_keywords = ai_result['ai_keywords']
                else:
                    material.ai_keywords = '鹰嘴蜜桃，优质农产品，溯源素材'
                
                db.session.add(material)
                db.session.flush()
                uploaded_materials.append(material.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功上传 {len(uploaded_materials)} 个文件',
            'materials': uploaded_materials
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

# 删除单个素材（硬删除）
@app.route('/api/materials/<material_id>', methods=['DELETE'])
def delete_material(material_id):
    """删除素材（硬删除 - 直接从数据库删除）"""
    try:
        material = Material.query.get(material_id)
        
        if not material:
            return jsonify({'error': '素材不存在'}), 404
        
        # 如果配置了云存储，同时删除云端文件
        if storage_available and cloud_storage:
            try:
                # 从文件路径中提取文件名
                filename = material.file_path.split('/')[-1]
                cloud_storage.delete_file(f"materials/{filename}")
                print(f"🗑️ 已删除云端文件: {filename}")
            except Exception as e:
                print(f"⚠️ 云端文件删除失败: {e}")
        
        # 从数据库删除记录
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({
            'message': '删除成功',
            'material_id': material_id,
            'deleted_from_cloud': storage_available
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

# 批量硬删除
@app.route('/api/materials/batch', methods=['DELETE'])
def batch_delete_materials():
    """批量删除素材（硬删除）"""
    try:
        material_ids = request.json.get('material_ids', [])
        
        if not material_ids:
            return jsonify({'error': '请提供要删除的素材ID列表'}), 400
        
        # 查找所有素材
        materials = Material.query.filter(Material.id.in_(material_ids)).all()
        
        if not materials:
            return jsonify({'error': '未找到指定的素材'}), 404
        
        deleted_count = 0
        cloud_deleted_count = 0
        
        for material in materials:
            # 删除云端文件
            if storage_available and cloud_storage:
                try:
                    filename = material.file_path.split('/')[-1]
                    if cloud_storage.delete_file(f"materials/{filename}"):
                        cloud_deleted_count += 1
                except Exception as e:
                    print(f"⚠️ 云端文件删除失败: {e}")
            
            # 从数据库删除
            db.session.delete(material)
            deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除 {deleted_count} 个素材',
            'deleted_count': deleted_count,
            'cloud_deleted_count': cloud_deleted_count if storage_available else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500

# 清空所有素材
@app.route('/api/materials/clear', methods=['DELETE'])
def clear_all_materials():
    """清空所有素材（谨慎使用！）"""
    try:
        # 获取所有素材
        materials = Material.query.all()
        total_count = len(materials)
        
        if total_count == 0:
            return jsonify({'message': '没有素材可删除'}), 200
        
        cloud_deleted_count = 0
        
        # 删除所有素材
        for material in materials:
            # 删除云端文件
            if storage_available and cloud_storage:
                try:
                    filename = material.file_path.split('/')[-1]
                    if cloud_storage.delete_file(f"materials/{filename}"):
                        cloud_deleted_count += 1
                except Exception as e:
                    print(f"⚠️ 云端文件删除失败: {e}")
            
            # 从数据库删除
            db.session.delete(material)
        
        db.session.commit()
        
        return jsonify({
            'message': f'已清空所有 {total_count} 个素材',
            'total_deleted': total_count,
            'cloud_deleted_count': cloud_deleted_count if storage_available else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'清空失败: {str(e)}'}), 500

# 获取素材列表
@app.route('/api/materials', methods=['GET'])
def get_materials():
    """获取所有素材"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 直接查询所有素材，不需要过滤
        materials = Material.query.order_by(Material.upload_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'materials': [material.to_dict() for material in materials.items],
            'total': materials.total,
            'pages': materials.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'查询失败: {str(e)}'}), 500

# 时间线视图
@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    """获取时间线视图"""
    try:
        materials = Material.query.order_by(Material.upload_time.desc()).all()
        
        timeline_data = {}
        for material in materials:
            date_str = material.upload_time.strftime('%Y-%m-%d')
            if date_str not in timeline_data:
                timeline_data[date_str] = []
            timeline_data[date_str].append(material.to_dict())
        
        return jsonify({'timeline': timeline_data}), 200
        
    except Exception as e:
        return jsonify({'error': f'获取时间线失败: {str(e)}'}), 500

@app.route('/api/materials/<material_id>/reanalyze', methods=['POST'])
def reanalyze_material(material_id):
    """重新分析素材，生成新的关键词"""
    try:
        material = Material.query.filter_by(id=material_id, is_deleted=False).first()
        
        if not material:
            return jsonify({'error': '素材不存在'}), 404
        
        if ai_generator:
            if material.file_type == 'image':
                ai_result = ai_generator.generate_keywords_from_image_url(material.file_path)
            else:
                ai_result = ai_generator.generate_keywords_from_video(material.file_path)
            
            material.ai_keywords = ai_result['ai_keywords']
        
        db.session.commit()
        
        return jsonify({
            'message': '重新分析成功',
            'material': material.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'重新分析失败: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查（包含数据库连接状态）"""
    try:
        # 测试数据库连接 - 使用text()包装
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'storage_available': storage_available,
        'timestamp': datetime.now().isoformat()
    })

# app.py (修改启动部分)
if __name__ == '__main__':
    # 移除或注释掉在开发环境下的 db.drop_all() 和 db.create_all()
    with app.app_context():
        # 仅创建不存在的表
        db.create_all()
        print("✅ 数据库表已就绪")
    # 在生产环境中，我们通常不使用 app.run(), 而是用 Gunicorn
    app.run(debug=False, host='0.0.0.0', port=5000) # 设置 debug=False

# if __name__ == '__main__':
#     with app.app_context():
#         try:
#             # 创建所有表
#             db.create_all()
#             print("✅ 数据库表创建成功")
            
#             # 检查表数量 - 使用text()包装
#             from sqlalchemy import text
#             result = db.session.execute(text("SHOW TABLES"))
#             tables = [row[0] for row in result]
#             print(f"📊 数据库表: {tables}")
            
#         except Exception as e:
#             print(f"❌ 数据库连接失败: {e}")
#             print("请检查：")
#             print("1. 数据库连接字符串是否正确")
#             print("2. 数据库是否已启动")
#             print("3. 网络连接是否正常")
#             print("4. 安全组规则是否允许访问")
#             print(f"5. 连接字符串: {app.config['SQLALCHEMY_DATABASE_URI']}")  # 调试用
    
#     print("🚀 服务器启动在 http://localhost:5000")
#     app.run(debug=True, host='0.0.0.0', port=5000)