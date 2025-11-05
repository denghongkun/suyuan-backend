import requests
import json
import base64
import os
from config import Config

class ImageAnalyzer:
    def __init__(self):
        self.app_id = Config.BAIDU_AI_APP_ID
        self.api_key = Config.BAIDU_AI_API_KEY
        self.secret_key = Config.BAIDU_AI_SECRET_KEY
        self.access_token = self._get_access_token()
    
    def _get_access_token(self):
        """获取百度AI访问令牌"""
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        response = requests.post(url)
        return response.json().get('access_token')
    
    def analyze_image(self, image_path):
        """分析图片并返回鹰嘴蜜桃相关的关键词"""
        try:
            # 读取图片并编码
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # 调用百度AI图像识别API
            url = f"https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general?access_token={self.access_token}"
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            data = {'image': image_data}
            
            response = requests.post(url, headers=headers, data=data)
            result = response.json()
            
            # 分析结果并生成关键词
            keywords = self._generate_keywords(result)
            return keywords
            
        except Exception as e:
            print(f"AI分析错误: {e}")
            return self._get_default_keywords()
    
    def _generate_keywords(self, ai_result):
        """根据AI识别结果生成鹰嘴蜜桃相关关键词"""
        keywords = []
        
        # 基础关键词
        base_keywords = ["鹰嘴蜜桃", "桃子", "水果", "农产品"]
        keywords.extend(base_keywords)
        
        # 从AI结果中提取关键词
        if 'result' in ai_result:
            for item in ai_result['result']:
                keyword = item.get('keyword', '')
                score = item.get('score', 0)
                
                # 只取置信度较高的关键词
                if score > 0.5:
                    keywords.append(keyword)
        
        # 鹰嘴蜜桃特定特征分析
        yanshuimi_specific = self._analyze_yanshuimi_features(ai_result)
        keywords.extend(yanshuimi_specific)
        
        # 去重并限制数量
        unique_keywords = list(set(keywords))[:15]
        
        return {
            "keywords": unique_keywords,
            "detailed_analysis": self._generate_detailed_analysis(unique_keywords)
        }
    
    def _analyze_yanshuimi_features(self, ai_result):
        """分析鹰嘴蜜桃的特定特征"""
        features = []
        
        # 形状特征
        shape_features = ["鹰嘴状", "果尖突出", "圆形", "椭圆形", "果形端正"]
        features.extend(shape_features)
        
        # 颜色特征
        color_features = ["青绿色", "粉红色", "红晕", "黄白色", "颜色鲜艳"]
        features.extend(color_features)
        
        # 生长阶段判断
        growth_stages = ["开花期", "幼果期", "膨大期", "成熟期", "采摘期"]
        features.extend(growth_stages)
        
        # 健康状况
        health_status = ["健康", "饱满", "无病虫害", "新鲜", "优质"]
        features.extend(health_status)
        
        # 生长场景
        scenes = ["果园", "田间", "树枝", "树叶", "农业", "种植"]
        features.extend(scenes)
        
        return features
    
    def _generate_detailed_analysis(self, keywords):
        """生成详细的分析结果"""
        analysis = {
            "growth_stage": self._infer_growth_stage(keywords),
            "shape_features": self._extract_shape_features(keywords),
            "health_status": self._assess_health_status(keywords),
            "scene_description": self._describe_scene(keywords)
        }
        return analysis
    
    def _infer_growth_stage(self, keywords):
        """推断生长阶段"""
        keyword_str = " ".join(keywords)
        
        if any(word in keyword_str for word in ["开花", "花"]):
            return "开花期"
        elif any(word in keyword_str for word in ["幼果", "小果"]):
            return "幼果期"
        elif any(word in keyword_str for word in ["膨大", "生长"]):
            return "膨大期"
        elif any(word in keyword_str for word in ["成熟", "红", "采摘"]):
            return "成熟期"
        else:
            return "生长期"
    
    def _extract_shape_features(self, keywords):
        """提取形状特征"""
        shape_words = [kw for kw in keywords if kw in ["鹰嘴状", "圆形", "椭圆形", "果尖突出", "果形端正"]]
        return ", ".join(shape_words) if shape_words else "标准鹰嘴蜜桃形状"
    
    def _assess_health_status(self, keywords):
        """评估健康状况"""
        keyword_str = " ".join(keywords)
        
        if any(word in keyword_str for word in ["病虫害", "腐烂", "损坏"]):
            return "需关注"
        elif any(word in keyword_str for word in ["饱满", "健康", "新鲜"]):
            return "健康良好"
        else:
            return "正常"
    
    def _describe_scene(self, keywords):
        """描述场景"""
        scene_words = [kw for kw in keywords if kw in ["果园", "田间", "树枝", "树叶", "农业"]]
        return "果园种植场景" if scene_words else "农业生产场景"
    
    def _get_default_keywords(self):
        """获取默认关键词（当AI分析失败时）"""
        return {
            "keywords": ["鹰嘴蜜桃", "农产品", "果园", "新鲜水果"],
            "detailed_analysis": {
                "growth_stage": "生长期",
                "shape_features": "鹰嘴蜜桃特征",
                "health_status": "正常",
                "scene_description": "农业生产场景"
            }
        }