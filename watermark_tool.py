#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具
功能：为图片添加基于拍摄时间的水印
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont, ExifTags
from datetime import datetime
import argparse

class WatermarkTool:
    def __init__(self):
        self.colors = {
            '1': ('白色', (255, 255, 255)),
            '2': ('黑色', (0, 0, 0)),
            '3': ('红色', (255, 0, 0)),
            '4': ('蓝色', (0, 0, 255)),
            '5': ('绿色', (0, 255, 0)),
            '6': ('黄色', (255, 255, 0))
        }
        
        self.positions = {
            '1': ('左上角', 'top-left'),
            '2': ('左下角', 'bottom-left'),
            '3': ('右上角', 'top-right'),
            '4': ('右下角', 'bottom-right'),
            '5': ('中间', 'center')
        }
        
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')

    def get_image_files(self, directory):
        """获取目录下所有支持的图片文件"""
        image_files = []
        try:
            for filename in os.listdir(directory):
                if filename.lower().endswith(self.supported_formats):
                    image_files.append(os.path.join(directory, filename))
        except Exception as e:
            print(f"读取目录失败: {e}")
            return []
        
        return image_files

    def get_exif_date(self, image_path):
        """从图片EXIF信息中提取拍摄时间"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data:
                    for tag, value in exif_data.items():
                        tag_name = ExifTags.TAGS.get(tag, tag)
                        if tag_name == 'DateTime':
                            # EXIF日期格式: "YYYY:MM:DD HH:MM:SS"
                            date_obj = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                            return date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"读取EXIF信息失败 {image_path}: {e}")
        
        # 如果无法获取EXIF时间，使用文件修改时间
        try:
            mtime = os.path.getmtime(image_path)
            date_obj = datetime.fromtimestamp(mtime)
            return date_obj.strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def get_user_preferences(self):
        """获取用户水印偏好设置"""
        print("\n=== 水印设置 ===")
        
        # 字体大小
        while True:
            try:
                font_size = int(input("请输入字体大小 (建议20-100): "))
                if 10 <= font_size <= 200:
                    break
                else:
                    print("字体大小应在10-200之间")
            except ValueError:
                print("请输入有效的数字")
        
        # 颜色选择
        print("\n颜色选项:")
        for key, (name, _) in self.colors.items():
            print(f"{key}. {name}")
        
        while True:
            color_choice = input("请选择颜色 (1-6): ")
            if color_choice in self.colors:
                color = self.colors[color_choice][1]
                break
            else:
                print("请输入有效的选项 (1-6)")
        
        # 位置选择
        print("\n位置选项:")
        for key, (name, _) in self.positions.items():
            print(f"{key}. {name}")
        
        while True:
            position_choice = input("请选择水印位置 (1-5): ")
            if position_choice in self.positions:
                position = self.positions[position_choice][1]
                break
            else:
                print("请输入有效的选项 (1-5)")
        
        return font_size, color, position

    def calculate_watermark_position(self, img_width, img_height, text_width, text_height, position):
        """计算水印位置坐标"""
        margin = 20  # 边距
        
        if position == 'top-left':
            return (margin, margin)
        elif position == 'top-right':
            return (img_width - text_width - margin, margin)
        elif position == 'bottom-left':
            return (margin, img_height - text_height - margin)
        elif position == 'bottom-right':
            return (img_width - text_width - margin, img_height - text_height - margin)
        elif position == 'center':
            return ((img_width - text_width) // 2, (img_height - text_height) // 2)
        else:
            return (margin, img_height - text_height - margin)  # 默认左下角

    def add_watermark(self, image_path, watermark_text, font_size, color, position, output_path):
        """为图片添加水印"""
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式以确保兼容性
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 创建绘图对象
                draw = ImageDraw.Draw(img)
                
                # 尝试使用系统字体，如果失败则使用默认字体
                try:
                    # macOS系统字体路径
                    font_paths = [
                        '/System/Library/Fonts/Arial.ttf',
                        '/System/Library/Fonts/Helvetica.ttc',
                        '/Library/Fonts/Arial.ttf'
                    ]
                    
                    font = None
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, font_size)
                            break
                    
                    if font is None:
                        font = ImageFont.load_default()
                        print("使用默认字体")
                except:
                    font = ImageFont.load_default()
                    print("使用默认字体")
                
                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算水印位置
                x, y = self.calculate_watermark_position(
                    img.width, img.height, text_width, text_height, position
                )
                
                # 添加半透明背景（可选）
                overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # 绘制半透明背景矩形
                padding = 5
                overlay_draw.rectangle(
                    [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                    fill=(0, 0, 0, 100)  # 半透明黑色背景
                )
                
                # 合并背景
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                
                # 绘制水印文字
                draw.text((x, y), watermark_text, font=font, fill=color)
                
                # 保存图片
                img.save(output_path, quality=95)
                return True
                
        except Exception as e:
            print(f"处理图片失败 {image_path}: {e}")
            return False

    def process_images(self, directory):
        """处理目录下的所有图片"""
        # 获取图片文件
        image_files = self.get_image_files(directory)
        if not image_files:
            print("未找到支持的图片文件")
            return
        
        print(f"找到 {len(image_files)} 个图片文件")
        
        # 获取用户偏好
        font_size, color, position = self.get_user_preferences()
        
        # 创建输出目录
        output_dir = os.path.join(directory, '_watermark')
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            return
        
        # 处理每个图片
        success_count = 0
        for image_path in image_files:
            filename = os.path.basename(image_path)
            output_path = os.path.join(output_dir, filename)
            
            # 获取拍摄日期作为水印
            watermark_text = self.get_exif_date(image_path)
            
            print(f"处理: {filename} (水印: {watermark_text})")
            
            if self.add_watermark(image_path, watermark_text, font_size, color, position, output_path):
                success_count += 1
                print(f"  ✓ 完成")
            else:
                print(f"  ✗ 失败")
        
        print(f"\n处理完成！成功处理 {success_count}/{len(image_files)} 个文件")
        print(f"输出目录: {output_dir}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片水印工具')
    parser.add_argument('directory', nargs='?', help='图片目录路径')
    args = parser.parse_args()
    
    # 获取目录路径
    if args.directory:
        directory = args.directory
    else:
        directory = input("请输入图片目录路径: ").strip()
    
    # 验证目录
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        sys.exit(1)
    
    if not os.path.isdir(directory):
        print(f"路径不是目录: {directory}")
        sys.exit(1)
    
    # 创建工具实例并处理图片
    tool = WatermarkTool()
    tool.process_images(directory)

if __name__ == '__main__':
    main()