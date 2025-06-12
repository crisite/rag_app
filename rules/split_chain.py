from typing import List, Dict, Any
from .split_base_rule import SplitRule


class SplitChain:
    """文件分割责任链管理类"""
    
    def __init__(self):
        self._rules: List[SplitRule] = []
    
    def add_rule(self, rule: SplitRule) -> None:
        """添加规则到责任链"""
        self._rules.append(rule)
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """处理内容，按顺序尝试每个规则"""
        for rule in self._rules:
            if rule.can_handle(content, file_type):
                return rule.process(content, file_type)
        
        # 如果没有规则可以处理，返回原始内容
        return [{
            "content": content,
            "type": file_type,
            "metadata": {}
        }]


class MarkdownSplitRule(SplitRule):
    """Markdown文件分割规则"""
    
    def can_handle(self, content: str, file_type: str) -> bool:
        return file_type.lower() == "markdown"
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        # TODO: 实现Markdown文件的具体分割逻辑
        chunks = content.split("\n\n")
        return [{
            "content": chunk.strip(),
            "type": file_type,
            "metadata": {"chunk_index": i}
        } for i, chunk in enumerate(chunks) if chunk.strip()]


class TextSplitRule(SplitRule):
    """文本文件分割规则"""
    
    def can_handle(self, content: str, file_type: str) -> bool:
        return file_type.lower() == "txt"
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        # TODO: 实现文本文件的具体分割逻辑
        chunks = content.split("\n")
        return [{
            "content": chunk.strip(),
            "type": file_type,
            "metadata": {"chunk_index": i}
        } for i, chunk in enumerate(chunks) if chunk.strip()]


class PDFSplitRule(SplitRule):
    """PDF文件分割规则"""
    
    def can_handle(self, content: str, file_type: str) -> bool:
        return file_type.lower() == "pdf"
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        # TODO: 实现PDF文件的具体分割逻辑
        # 这里需要先解析PDF内容，然后进行分割
        return [{
            "content": content,
            "type": file_type,
            "metadata": {"page": 1}
        }]


class DocxSplitRule(SplitRule):
    """Word文件分割规则"""
    
    def can_handle(self, content: str, file_type: str) -> bool:
        return file_type.lower() == "docx"
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        # TODO: 实现Word文件的具体分割逻辑
        # 这里需要先解析Word内容，然后进行分割
        return [{
            "content": content,
            "type": file_type,
            "metadata": {"section": 1}
        }] 