import os
import logging
from volcenginesdkarkruntime import Ark
from config import Config

class DoubaoAIGenerator:
    def __init__(self):
        self.api_key = Config.ARK_API_KEY
        self.model = Config.DOUBAO_MODEL
        self.base_url = Config.DOUBAO_BASE_URL
        
        if self.api_key and self.model:
            try:
                self.client = Ark(
                    base_url=self.base_url,
                    api_key=self.api_key
                )
                logging.info("✅ 豆包AI客户端初始化成功")
            except Exception as e:
                logging.error(f"❌ 豆包AI客户端初始化失败: {e}")
                self.client = None
        else:
            logging.warning("豆包API配置不完整")
            self.client = None

    def generate_keywords_from_image_url(self, image_url):
        """根据图片URL生成通用农作物关键词"""
        if not self.client:
            return self._get_fallback_keywords()

        try:
            logging.info(f"🖼️ 开始分析农作物图片: {image_url}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": """请详细分析这张农业图片，生成适合用于农产品溯源故事文案的关键词。

请重点关注：
1. 识别图片中的农作物种类（如：水稻、小麦、玉米、水果、蔬菜等）
2. 描述农作物的生长状况、形状特征、颜色、大小
3. 分析生长场景和环境特征（农田、果园、温室等）
4. 评估农作物的健康状况和品质特点
5. 描述相关的农业活动或种植过程

请生成15-20个准确描述图片内容的关键词，用中文逗号分隔，直接返回关键词字符串。"""
                            }
                        ]
                    }
                ],
                extra_headers={'x-is-encrypted': 'true'},
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logging.info(f"🤖 AI回复内容: {content}")
                cleaned_keywords = self._clean_keywords(content)
                return {
                    'success': True,
                    'ai_keywords': cleaned_keywords
                }
            else:
                logging.warning("AI返回空结果")
                return self._get_fallback_keywords()
                
        except Exception as e:
            logging.error(f"农作物图片分析失败: {e}")
            return self._get_fallback_keywords()

    def generate_keywords_from_video(self, video_url):
        """为农业视频生成通用关键词"""
        if not self.client:
            return self._get_fallback_keywords(video=True)
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"""请为农业视频生成适合溯源故事的关键词。

视频可能包含各种农作物的种植、生长、管理、采摘等农业活动。

请生成15-20个描述性关键词，涵盖：
- 农作物种类和特征
- 农业操作和活动
- 生长过程和阶段
- 环境场景特征
- 品质管理要点

用中文逗号分隔，直接返回关键词字符串。"""
                    }
                ],
                extra_headers={'x-is-encrypted': 'true'},
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                cleaned_keywords = self._clean_keywords(content)
                return {
                    'success': True,
                    'ai_keywords': cleaned_keywords
                }
            else:
                return self._get_fallback_keywords(video=True)
                
        except Exception as e:
            logging.error(f"农业视频关键词生成失败: {e}")
            return self._get_fallback_keywords(video=True)

    def _clean_keywords(self, keywords_text):
        """清理关键词"""
        # 移除可能的解释文字
        lines = keywords_text.split('\n')
        for line in lines:
            if '，' in line and len(line) > 10:
                keywords_text = line
                break
        
        keywords = [kw.strip() for kw in keywords_text.split('，') if kw.strip()]
        keywords = [kw for kw in keywords if len(kw) > 1]
        
        # 不再强制添加"鹰嘴蜜桃"，让AI自由识别
        return '，'.join(keywords[:20])

    def _get_fallback_keywords(self, video=False):
        """备用关键词（通用农业关键词）"""
        if video:
            keywords = [
                '农业视频', '生长记录', '农田管理', '种植过程',
                '农事操作', '品质管控', '自然生长', '生态种植', 
                '溯源记录', '农业技术', '丰收喜悦', '农耕文化'
            ]
        else:
            keywords = [
                '优质农产品', '农田种植', '自然生长', '农作物',
                '颜色鲜艳', '健康生长', '农业产品', '品质优良', 
                '新鲜采摘', '生态农业', '绿色种植', '丰收季节'
            ]
        
        return {
            'success': False,
            'ai_keywords': '，'.join(keywords)
        }