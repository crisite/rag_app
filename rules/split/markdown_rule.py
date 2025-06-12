import re
from typing import List, Dict, Any
from .split_base_rule import SplitRule


class MarkdownSplitRule(SplitRule):
    """Markdown文件分割规则"""
    
    def __init__(self):
        # 标题正则表达式
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        # 代码块正则表达式
        self.code_block_pattern = re.compile(r'```[\s\S]*?```')
        # 列表项正则表达式
        self.list_item_pattern = re.compile(r'^[\s]*[-*+]\s+.+$', re.MULTILINE)
    
    def can_handle(self, content: str, file_type: str) -> bool:
        return file_type.lower() in ["markdown", "md"]
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        chunks = []
        
        # 1. 首先处理代码块，避免代码块内的内容被错误分割
        code_blocks = []
        for match in self.code_block_pattern.finditer(content):
            code_blocks.append({
                "content": match.group(0),
                "type": "code_block",
                "metadata": {
                    "start_pos": match.start(),
                    "end_pos": match.end()
                }
            })
            # 将代码块替换为占位符
            content = content[:match.start()] + f"CODE_BLOCK_{len(code_blocks)-1}" + content[match.end():]
        
        # 2. 按标题分割内容
        sections = self._split_by_headings(content)
        
        # 3. 处理每个部分
        for section in sections:
            # 还原代码块
            for i, code_block in enumerate(code_blocks):
                section["content"] = section["content"].replace(f"CODE_BLOCK_{i}", code_block["content"])
            
            # 如果部分内容为空，跳过
            if not section["content"].strip():
                continue
                
            # 进一步分割段落
            paragraphs = self._split_paragraphs(section["content"])
            
            for i, para in enumerate(paragraphs):
                if not para.strip():
                    continue
                    
                chunks.append({
                    "content": para.strip(),
                    "type": file_type,
                    "metadata": {
                        "heading_level": section["heading_level"],
                        "heading_text": section["heading_text"],
                        "paragraph_index": i,
                        "is_list_item": bool(self.list_item_pattern.match(para)),
                        "is_code_block": para.startswith("```")
                    }
                })
        
        return chunks
    
    def _split_by_headings(self, content: str) -> List[Dict[str, Any]]:
        """按标题分割内容"""
        sections = []
        lines = content.split('\n')
        current_section = {
            "content": "",
            "heading_level": 0,
            "heading_text": "Document"
        }
        
        for line in lines:
            heading_match = self.heading_pattern.match(line)
            if heading_match:
                # 保存当前部分
                if current_section["content"].strip():
                    sections.append(current_section)
                
                # 创建新部分
                current_section = {
                    "content": "",
                    "heading_level": len(heading_match.group(1)),
                    "heading_text": heading_match.group(2).strip()
                }
            else:
                current_section["content"] += line + "\n"
        
        # 添加最后一部分
        if current_section["content"].strip():
            sections.append(current_section)
            
        return sections
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """分割段落"""
        # 使用空行分割段落
        paragraphs = re.split(r'\n\s*\n', content)
        return [p.strip() for p in paragraphs if p.strip()] 