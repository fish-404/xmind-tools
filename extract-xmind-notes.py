import os
import re
import zipfile
import json  
import tkinter as tk  
from tkinter import filedialog

class XMindNoteExtractor:
    def __init__(self):
        # 创建Tkinter根窗口但隐藏它
        self.root = tk.Tk()  # 修改为使用tk.Tk()
        self.root.withdraw()
        
    def select_file(self):
        """打开文件选择对话框让用户选择XMind文件"""
        file_path = filedialog.askopenfilename(
            title="选择XMind文件",
            filetypes=[("XMind files", "*.xmind"), ("All files", "*.*")]
        )
        return file_path
    
    def extract_notes(self, xmind_file_path):
        """从XMind文件中提取所有notes及其对应的title"""
        result = []
        
        try:
            # 检查文件是否存在
            if not os.path.exists(xmind_file_path):
                print(f"错误：文件不存在 - {xmind_file_path}")
                return []
            
            # 打开XMind文件（本质是zip文件）
            with zipfile.ZipFile(xmind_file_path, 'r') as zip_ref:
                # 读取content.json文件
                try:
                    with zip_ref.open('content.json', 'r') as content_file:
                        content_data = json.load(content_file)
                except KeyError:
                    print("错误：无法找到content.json文件")
                    return []
            
            # 解析JSON数据，提取所有topics及其notes
            self._parse_topics(content_data, result)
            
            return result
            
        except Exception as e:
            print(f"处理文件时出错：{str(e)}")
            return []
    
    def _parse_topics(self, data, result, parent_title=""):
        """递归解析topics，提取title和notes"""
        # 处理根节点
        if isinstance(data, dict):
            # 检查是否有rootTopic
            if 'rootTopic' in data:
                self._parse_topics(data['rootTopic'], result)
            
            # 检查是否有title和notes
            if 'title' in data:
                current_title = data['title']
                # 如果有父标题，构建完整标题路径
                if parent_title:
                    full_title = f"{parent_title} > {current_title}"
                else:
                    full_title = current_title
                
                # 检查是否有notes
                if 'notes' in data and data['notes']:
                    # 获取plain格式的notes内容
                    notes_content = ""
                    if 'plain' in data['notes'] and 'content' in data['notes']['plain']:
                        notes_content = data['notes']['plain']['content']
                    
                    # 如果没有plain格式，则尝试从realHTML中提取
                    if 'realHTML' in data['notes'] and 'content' in data['notes']['realHTML']:
                        # 直接保留HTML格式，不再移除标签
                        notes_content = data['notes']['realHTML']['content']
                    
                    if notes_content:
                        result.append({"title": full_title, "notes": notes_content})
                
                # 递归处理子topics
                if 'children' in data and data['children'] and 'attached' in data['children']:
                    for child in data['children']['attached']:
                        self._parse_topics(child, result, full_title)
            
        # 处理数组
        elif isinstance(data, list):
            for item in data:
                self._parse_topics(item, result, parent_title)
    
    # 可以移除或修改_extract_text_from_html函数
    def _extract_text_from_html(self, html_content):
        """保留HTML格式"""
        return html_content  # 直接返回HTML内容，不再处理
    
    def save_to_markdown(self, xmind_file_path, notes_data):
        """将提取的notes保存为Markdown文件"""
        if not notes_data:
            print("没有提取到任何notes数据")
            return False
        
        # 生成输出文件路径
        base_name = os.path.splitext(xmind_file_path)[0]
        output_path = f"{base_name}_notes.md"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as md_file:
                md_file.write("# XMind Notes 提取结果\n\n")
                md_file.write(f"**文件来源**: {os.path.basename(xmind_file_path)}\n\n")
                md_file.write(f"**提取到的Notes数量**: {len(notes_data)}\n\n")
                md_file.write("---\n\n")
                
                # 写入每个note
                for i, note_item in enumerate(notes_data, 1):
                    md_file.write(f"{i}. {note_item['title']}{note_item['notes']}\n\n")
                    md_file.write("---\n\n")
            
            print(f"Notes已成功保存到: {output_path}")
            return True
        except Exception as e:
            print(f"保存Markdown文件时出错：{str(e)}")
            return False
    
    def run(self):
        """运行整个提取流程"""
        # 让用户选择文件
        xmind_file = self.select_file()
        if not xmind_file:
            print("未选择文件，程序退出")
            return
        
        print(f"正在处理文件: {xmind_file}")
        
        # 提取notes
        notes_data = self.extract_notes(xmind_file)
        
        # 保存为Markdown
        if notes_data:
            self.save_to_markdown(xmind_file, notes_data)
        
        print("处理完成！")

if __name__ == "__main__":
    extractor = XMindNoteExtractor()
    extractor.run()  # 添加这一行来执行程序