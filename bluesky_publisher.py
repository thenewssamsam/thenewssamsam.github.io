"""
Bluesky Publisher - 自動發布文章到 Bluesky
整合到文章發布流程中，自動生成社群文案並推送到 Bluesky

改進：加入品質控制系統，確保貼文格式正確、無 HTML 殘留、符合 Bluesky 限制
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
import re
from pathlib import Path
import json
import random
from quality_control import QualityControl, QualityReport

try:
    from atproto import Client, models
    ATPROTO_AVAILABLE = True
except ImportError:
    ATPROTO_AVAILABLE = False
    print("⚠️  atproto 庫未安裝，將執行: pip install atproto")


@dataclass
class BlueskyConfig:
    """Bluesky 配置"""
    handle: str  # 例如：johnthenews.bsky.social
    app_password: str  # App Password
    enabled: bool = True
    reply_restriction: str = "following"  # 回復限制：following（只允許追蹤者）、none（無限制）、disabled（關閉所有回覆）、mention（只能被提及）


@dataclass
class SocialPost:
    """社群文案"""
    text: str
    hashtags: list[str]
    url: str
    char_count: int


class BlueskyPublisher:
    """Bluesky 發布器"""
    
    def __init__(self, config: BlueskyConfig):
        self.config = config
        self.client = None
        self.is_authenticated = False
        self.qc = QualityControl(strict_mode=False)  # 品質控制系統
        
        if not ATPROTO_AVAILABLE:
            raise ImportError("atproto 庫未安裝，請執行: pip install atproto")

    
    def authenticate(self) -> bool:
        """認證 Bluesky"""
        try:
            self.client = Client()
            self.client.login(self.config.handle, self.config.app_password)
            self.is_authenticated = True
            print(f"✅ Bluesky 認證成功：{self.config.handle}")
            return True
        except Exception as e:
            print(f"❌ Bluesky 認證失敗：{str(e)}")
            return False
    
    def create_url_facets(self, text: str) -> list:
        """
        為文本中的 URL 創建 Facets（讓 URL 可點擊）
        
        Args:
            text: 包含 URL 的文本
        
        Returns:
            Facets 列表
        """
        try:
            from atproto import models
            
            facets = []
            url_pattern = r'https?://[^\s]+'
            
            for match in re.finditer(url_pattern, text):
                url = match.group()
                start_byte = match.start()
                end_byte = match.end()
                
                # 🆕 使用正確的 atproto API
                # AppBskyRichtextFacet.Main = Facet 對象
                # AppBskyRichtextFacet.ByteSlice = 字節位置
                # AppBskyRichtextFacet.Link = 超連結特性
                facet = models.AppBskyRichtextFacet.Main(
                    index=models.AppBskyRichtextFacet.ByteSlice(
                        byte_start=start_byte,
                        byte_end=end_byte
                    ),
                    features=[models.AppBskyRichtextFacet.Link(uri=url)]
                )
                facets.append(facet)
            
            return facets
        except Exception as e:
            print(f"⚠️  Facets 構造異常：{str(e)[:60]}")
            # 如果出錯，返回空列表（atproto 的 send_post 可以處理 None 的 facets）
            return []
    
    def generate_social_post(self, article_title: str, article_url: str, source_url: str = "", article_summary: str = "") -> SocialPost:
        """
        生成適合 Bluesky 的社群文案
        
        新格式：
        [主旨摘要 150-200 字符]
        
        read more 看留言
        
        總字符：≤ 300 字符
        
        Args:
            article_title: 文章標題（不使用）
            article_url: 你的文章 URL（不顯示在主貼文，只在評論中使用）
            source_url: 來源文章 URL（已廢棄，不使用）
            article_summary: 文章摘要（會自動清理 HTML）
        
        Returns:
            SocialPost 物件
        """
        # Bluesky 最大字符限制
        MAX_CHARS = 300
        
        # 清理摘要中的 HTML 和垃圾內容（重要！）
        if article_summary:
            # 使用品質控制系統的 HTML 清理方法（更徹底）
            article_summary = self.qc.clean_html(article_summary)
        
        # 構建 "read more 看留言" 行
        read_more_line = "read more 看留言"
        urls_length = len(read_more_line)
        
        # 計算摘要可用空間
        available_for_summary = MAX_CHARS - urls_length - 2  # -2 為換行符
        
        # 摘要部分 - 盡量用滿 150-200 字符
        summary_text = ""
        if article_summary:
            words = article_summary.split()
            
            # 先嘗試填滿可用空間
            current_text = ""
            for word in words:
                test_text = current_text + " " + word if current_text else word
                if len(test_text) <= available_for_summary:
                    current_text = test_text
                else:
                    break
            
            summary_text = current_text
        
        # 如果摘要為空，使用標題作為摘要
        if not summary_text and article_title:
            summary_text = article_title[:available_for_summary]
        
        # 組合最終文案
        post_text = f"{summary_text}\n\nread more 看留言"
        
        # 最終檢查 - 確保不超過 300 字符
        if len(post_text) > MAX_CHARS:
            # 從摘要末尾移除單字直到符合限制
            words = summary_text.split()
            while len(words) > 5 and len(f"{' '.join(words)}\n\nread more 看留言") > MAX_CHARS:
                words.pop()
            summary_text = ' '.join(words)
            post_text = f"{summary_text}\n\nread more 看留言"
        
        # 提取 hashtags
        hashtags = re.findall(r'#(\w+)', post_text)
        
        # 確保最終字符數不超過 300
        final_char_count = len(post_text)
        
        return SocialPost(
            text=post_text,
            hashtags=hashtags,
            url=article_url,  # 保留 URL 用於後續處理，但不顯示在主貼文
            char_count=final_char_count
        )
    
    def generate_social_post_with_ai(self, article_title: str, article_url: str, source_url: str = "", article_content: str = "") -> SocialPost:
        """
        使用 AI 生成社群文案摘要（從文章內容提取）
        
        格式：
        📰 標題
        
        摘要（230+ 英文單字）
        
        URL1
        URL2
        
        Args:
            article_title: 文章標題
            article_url: 文章 URL
            source_url: 來源文章 URL
            article_content: 文章內容
        
        Returns:
            SocialPost 物件
        """
        try:
            from google import genai
            from dotenv import load_dotenv
            import os
            
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            load_dotenv(env_path)
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("⚠️  未找到 Gemini API Key，使用基本文案生成")
                return self.generate_social_post(article_title, article_url, source_url)
            
            # 如果沒有文章內容，也用基本方法
            if not article_content or len(article_content.strip()) < 100:
                print("⚠️  文章內容不足，使用基本文案生成")
                return self.generate_social_post(article_title, article_url, source_url)
            
            # AI 提示詞：提取摘要
            prompt = f"""Extract a concise summary from this article for a Bluesky post. 

Article Title: {article_title}

Article Content (first 2000 chars):
{article_content[:2000]}

Requirements:
- Write 200-250 English words
- Conversational, accessible tone
- Key points and insights only
- No AI jargon ("delve", "revolutionize", "leverage", etc.)
- Focus on what readers should know

Output ONLY the summary text, nothing else."""
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="models/gemini-3.5-flash-lite",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=400,
                )
            )
            
            summary = response.text.strip() if response.text else ""
            
            if summary and len(summary) > 50:
                # 使用提取的摘要
                return self.generate_social_post(
                    article_title=article_title,
                    article_url=article_url,
                    source_url=source_url,
                    article_summary=summary
                )
            else:
                print("⚠️  AI 摘要生成失敗，使用基本文案生成")
                return self.generate_social_post(article_title, article_url, source_url)
        
        except Exception as e:
            print(f"⚠️  AI 生成失敗：{str(e)[:40]}，使用基本生成")
            return self.generate_social_post(article_title, article_url, source_url)
                
        except Exception as e:
            print(f"⚠️  AI 生成失敗：{str(e)}，使用基本生成")
            return self.generate_social_post(article_title, article_url)
    
    def publish_post(self, social_post: SocialPost) -> Dict[str, any]:
        """
        發布文案到 Bluesky（含品質驗證）
        
        Args:
            social_post: SocialPost 物件
        
        Returns:
            發布結果字典
        """
        if not self.is_authenticated:
            if not self.authenticate():
                return {
                    'success': False,
                    'error': '認證失敗'
                }
        
        try:
            # 🆕 品質驗證步驟
            print(f"\n📋 進行品質檢查...")
            qc_report = self.qc.validate_bluesky_post(social_post.text)
            
            print(f"   字符數：{qc_report.details.get('cleaned_length', 0)}/300")
            print(f"   HTML 已清理：{qc_report.details.get('html_removed', 0)} 字符")
            
            if not qc_report.is_valid:
                print(f"   ❌ 品質檢查未通過 (分數：{qc_report.score}/100)")
                for error in qc_report.errors:
                    print(f"      ❌ {error}")
                return {
                    'success': False,
                    'error': f"品質檢查失敗：{'; '.join(qc_report.errors)}",
                    'qc_report': qc_report
                }
            
            if qc_report.warnings:
                print(f"   ⚠️  警告 (分數：{qc_report.score}/100)")
                for warning in qc_report.warnings:
                    print(f"      ⚠️  {warning}")
            else:
                print(f"   ✅ 品質檢查通過 (分數：{qc_report.score}/100)")
            
            # 使用清理後的文本
            cleaned_text = self.qc.clean_html(social_post.text)
            
            # 創建 URL Facets（讓 URL 可點擊）
            facets = self.create_url_facets(cleaned_text)
            print(f"   📎 建立 {len(facets)} 個 URL Facet（可點擊連結）")
            
            # 發布到 Bluesky
            print(f"   📤 發布到 Bluesky...")
            response = self.client.send_post(
                text=cleaned_text,
                facets=facets if facets else None
            )
            
            print(f"   ✅ 發布成功！")
            
            return {
                'success': True,
                'post_uri': response.uri,
                'post_cid': response.cid,
                'char_count': len(cleaned_text),
                'hashtags': social_post.hashtags,
                'url_facets_count': len(facets) if facets else 0,
                'facets': facets if facets else [],
                'qc_score': qc_report.score,
                'text': cleaned_text,  # 添加文本字段供後續使用
                'note': '✅ 品質檢查通過，Facets（可點擊連結）已成功設置！'
            }
        except Exception as e:
            print(f"   ❌ 發布失敗：{str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def publish_post_with_comments(self, post_text: str, article_url: str = "", summary: str = "", use_existing_post: bool = False, existing_post_uri: str = "", existing_post_cid: str = "") -> Dict[str, any]:
        """
        發布貼文 + 聯盟評論到 Bluesky
        
        評論作為回覆發布，延遲 5 分鐘後發布
        
        Args:
            post_text: 主要貼文文本
            article_url: 文章 URL（用於建立連結）
            summary: 摘要（用於品質檢查）
            use_existing_post: 是否使用現有的貼文（只發布評論）
            existing_post_uri: 現有貼文的 URI
            existing_post_cid: 現有貼文的 CID
        
        Returns:
            發布結果字典
        """
        import time
        
        if not self.is_authenticated:
            if not self.authenticate():
                return {
                    'success': False,
                    'error': '認證失敗',
                    'comment_urls': []
                }
        
        try:
            # 初始化變數
            qc_report = None
            cleaned_text = None
            
            # 1️⃣ 發布主貼文或使用現有貼文
            if use_existing_post and existing_post_uri and existing_post_cid:
                print(f"   📮 使用現有貼文：{existing_post_uri[:50]}...")
                main_post_uri = existing_post_uri
                main_post_cid = existing_post_cid
                print(f"      ✅ 使用現有貼文成功")
            else:
                print(f"   📮 發布主貼文...")
                
                # 品質檢查
                qc_report = self.qc.validate_bluesky_post(post_text)
                
                if not qc_report.is_valid:
                    print(f"   ❌ 品質檢查失敗")
                    for error in qc_report.errors:
                        print(f"      - {error}")
                    return {
                        'success': False,
                        'error': f"品質檢查失敗：{'; '.join(qc_report.errors)}",
                        'comment_urls': []
                    }
                
                # 清理文本
                cleaned_text = self.qc.clean_html(post_text)
                
                # 創建 Facets
                facets = self.create_url_facets(cleaned_text)
                
                # 發布主貼文
                response = self.client.send_post(
                    text=cleaned_text,
                    facets=facets if facets else None
                )
                
                main_post_uri = response.uri
                main_post_cid = response.cid
                print(f"      ✅ 主貼文發布成功")
            
            # 2️⃣ 發布聯盟評論
            print(f"   💬 開始發布聯盟評論...")
            
            comment_urls = []
            
            try:
                # 加載聯盟產品
                config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'affiliate_products.json')
                
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        affiliate_config = json.load(f)
                    
                    all_products = []
                    for category, products in affiliate_config.get('products', {}).items():
                        all_products.extend(products)
                    
                    # 隨機選擇 7 個產品
                    num_comments = 7
                    selected_products = random.sample(all_products, min(num_comments, len(all_products)))
                    
                    # 簡短介紹字典
                    descriptions = {
                        'water': 'Keeps your drinks cold and fresh all day long',
                        'skincare': 'Professional-grade care for healthy, glowing skin',
                        'cerave': 'Professional-grade care for healthy, glowing skin',
                        'cleanser': 'Professional-grade care for healthy, glowing skin',
                        'backpack': 'Durable and comfortable for any adventure',
                        'keyboard': 'Smooth typing experience with excellent build quality',
                        'mouse': 'Precise and responsive for work or gaming',
                        'headphone': 'Crystal-clear sound with comfortable fit',
                        'tablet': 'Perfect for entertainment and productivity',
                        'cookware': 'Non-stick cooking made easy and healthy',
                        'monitor': 'Stunning display for work and entertainment',
                        'hard_drive': 'Fast and reliable storage for your files',
                    }
                    
                    # 構建 ReplyRef
                    from atproto import models
                    strong_ref = models.ComAtprotoRepoStrongRef.Main(
                        uri=main_post_uri,
                        cid=main_post_cid
                    )
                    reply_ref = models.AppBskyFeedPost.ReplyRef(
                        root=strong_ref,
                        parent=strong_ref
                    )
                    
                    # 先發布一則評論包含文章連結
                    if article_url:
                        try:
                            article_comment_text = f"📖 閱讀完整文章：{article_url}"
                            article_comment_facets = self.create_url_facets(article_comment_text)
                            
                            article_comment_response = self.client.send_post(
                                text=article_comment_text,
                                reply_to=reply_ref,
                                facets=article_comment_facets if article_comment_facets else None
                            )
                            
                            comment_urls.append(article_comment_response.uri)
                            print(f"      ✅ [文章連結] 評論回覆發布成功")
                            
                            # 隨機等待 1-5 秒
                            random_interval = random.randint(1, 5)
                            time.sleep(random_interval)
                        except Exception as e:
                            print(f"      ⚠️  文章連結評論發布失敗：{str(e)[:60]}")
                    
                    # 為每個產品發布評論作為回覆
                    for i, product in enumerate(selected_products, 1):
                        try:
                            # 提取資訊
                            product_title = product.get('title', 'Product')
                            product_url = product.get('link', '') or product.get('url', '')
                            
                            # 簡單驗證
                            if not product_url:
                                print(f"      ⚠️  [{i}/{num_comments}] 跳過無效產品：{product_title[:30]}")
                                continue
                            
                            # 選擇介紹文字
                            description = descriptions.get('keyboard', 'High-quality product you will love')
                            for key in descriptions:
                                if key.lower() in product_title.lower():
                                    description = descriptions[key]
                                    break
                            
                            # 評論格式：產品名稱 - 介紹\n連結
                            comment_text = f"{product_title} - {description}\n{product_url}"
                            
                            # 創建 URL Facet
                            comment_facets = self.create_url_facets(comment_text)
                            
                            # 發布評論作為回覆
                            comment_response = self.client.send_post(
                                text=comment_text,
                                reply_to=reply_ref,
                                facets=comment_facets if comment_facets else None
                            )
                            
                            comment_urls.append(comment_response.uri)
                            print(f"      ✅ [{i}/{num_comments}] 評論回覆發布成功：{product_title[:40]}")
                            
                            # 每則評論之間隨機間隔 1-5 秒
                            if i < len(selected_products):
                                random_interval = random.randint(1, 5)
                                time.sleep(random_interval)
                            
                        except Exception as e:
                            error_msg = str(e)[:80]
                            print(f"      ⚠️  [{i}/{num_comments}] 評論發布失敗：{error_msg}")
                            continue
                    
                    print(f"   📊 共發布 {len(comment_urls)} 條評論回覆")
                
            except Exception as e:
                print(f"   ⚠️  評論系統出現問題：{str(e)[:60]}")
                # 主貼文已成功，所以仍返回 success
            
            return {
                'success': True,
                'post_uri': main_post_uri,
                'post_cid': main_post_cid,
                'comment_urls': comment_urls,
                'qc_score': qc_report.score if qc_report else 'N/A',
                'char_count': len(cleaned_text) if cleaned_text else 'N/A',
                'note': f'✅ 發布成功：1 個主貼文 + {len(comment_urls)} 條評論回覆'
            }
        
        except Exception as e:
            print(f"   ❌ 主貼文發布失敗：{str(e)}")
            return {
                'success': False,
                'error': str(e),
                'comment_urls': []
            }
    
    def publish_article(self, article_title: str, article_url: str, source_url: str = "", article_content: str = "", use_ai: bool = True) -> Dict[str, any]:
        """
        一鍵發布文章到 Bluesky（完整流程 + 品質驗證）
        
        Args:
            article_title: 文章標題
            article_url: 文章 URL
            article_content: 文章內容（用於 AI 生成）
            use_ai: 是否使用 AI 生成文案
        
        Returns:
            發布結果字典
        """
        if not self.config.enabled:
            return {
                'success': False,
                'error': 'Bluesky 發布已禁用'
            }
        
        print(f"\n📝 發布文章到 Bluesky：{article_title[:50]}")
        
        # 生成社群文案
        if use_ai:
            social_post = self.generate_social_post_with_ai(article_title, article_url, source_url, article_content)
        else:
            social_post = self.generate_social_post(article_title, article_url, source_url)
        
        print(f"   📄 生成文案：{social_post.char_count} 字元")
        
        # 發布
        result = self.publish_post(social_post)
        
        if result['success']:
            print(f"   ✅ Bluesky 發布成功：{result['post_uri']}")
            print(f"   📊 品質分數：{result.get('qc_score', 'N/A')}/100")
        else:
            print(f"   ❌ Bluesky 發布失敗：{result['error']}")
        
        return result


def get_bluesky_publisher() -> Optional[BlueskyPublisher]:
    """
    從環境變數獲取 Bluesky 發布器
    
    Returns:
        BlueskyPublisher 實例或 None
    """
    try:
        from dotenv import load_dotenv
        import os
        
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        load_dotenv(env_path)
        
        handle = os.getenv('BLUESKY_HANDLE')
        app_password = os.getenv('BLUESKY_APP_PASSWORD')
        reply_restriction = os.getenv('BLUESKY_REPLY_RESTRICTION', 'following')  # 默認只允許追蹤者回復
        
        if not handle or not app_password:
            print("⚠️  未找到 Bluesky 憑證（BLUESKY_HANDLE, BLUESKY_APP_PASSWORD）")
            return None
        
        config = BlueskyConfig(
            handle=handle,
            app_password=app_password,
            enabled=True,
            reply_restriction=reply_restriction
        )
        
        return BlueskyPublisher(config)
        
    except Exception as e:
        print(f"⚠️  初始化 Bluesky 發布器失敗：{str(e)}")
        return None


if __name__ == "__main__":
    # 測試
    print("Bluesky Publisher 模組測試")
    
    # 檢查依賴
    if not ATPROTO_AVAILABLE:
        print("安裝依賴：pip install atproto")
    else:
        print("✅ atproto 庫已安裝")
    
    # 測試配置加載
    publisher = get_bluesky_publisher()
    if publisher:
        print("✅ Bluesky 發布器初始化成功")
        
        # 測試文案生成
        test_post = publisher.generate_social_post(
            "Breaking: Major Policy Change Announced",
            "https://example.com/article",
            "This is a test article about policy changes that affect millions of people."
        )
        print(f"📝 測試文案：{test_post.char_count} 字元")
        print(f"   {test_post.text}")
    else:
        print("❌ Bluesky 發布器初始化失敗")