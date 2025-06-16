from typing import List, Dict, Any
from .split_base_rule import SplitRule

class TxtSplitRule(SplitRule):
    """TXT文件切分规则"""
    
    def __init__(self, 
                 max_chunk_size: int = 1000,    # 最大块大小
                 min_chunk_size: int = 200,     # 最小块大小
                 sentence_threshold: int = 500): # 句子切分阈值
        """
        初始化TXT文件切分规则
        
        Args:
            max_chunk_size: 文本块的最大字符数
            min_chunk_size: 文本块的最小字符数
            sentence_threshold: 触发句子切分的阈值
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.sentence_threshold = sentence_threshold
    
    def can_handle(self, content: str, file_type: str) -> bool:
        """
        判断是否可以处理TXT文件
        
        Args:
            content: 文本内容
            file_type: 文件类型
            
        Returns:
            bool: 是否可以处理
        """
        return file_type.lower() == "txt"
    
    def _split_by_paragraphs(self, content: str) -> List[str]:
        """
        按段落分割文本
        
        Args:
            content: 文本内容
            
        Returns:
            List[str]: 段落列表
        """
        # 使用空行分割段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """
        按句子分割文本
        
        Args:
            text: 文本内容
            
        Returns:
            List[str]: 句子列表
        """
        # 定义句子结束符
        sentence_endings = ['. ', '。', '！', '？', '! ', '? ']
        sentences = []
        current_pos = 0
        
        while current_pos < len(text):
            # 查找最近的句子结束符
            next_pos = len(text)
            for ending in sentence_endings:
                pos = text.find(ending, current_pos)
                if pos != -1 and pos < next_pos:
                    next_pos = pos + len(ending)
            
            # 提取当前句子
            if next_pos > current_pos:
                sentence = text[current_pos:next_pos].strip()
                if sentence:
                    sentences.append(sentence)
            
            current_pos = next_pos
        
        # 如果还有剩余文本，添加到最后一个句子
        if current_pos < len(text):
            remaining = text[current_pos:].strip()
            if remaining:
                sentences.append(remaining)
        
        return sentences
    
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """
        处理TXT文件内容，实现动态切分策略
        
        Args:
            content: 文本内容
            file_type: 文件类型
            
        Returns:
            List[Dict[str, Any]]: 分割后的文本块列表
        """
        chunks = []
        chunk_index = 0
        
        # 1. 首先按段落分割
        paragraphs = self._split_by_paragraphs(content)
        
        for para in paragraphs:
            # 2. 如果段落长度超过阈值，按句子分割
            if len(para) > self.sentence_threshold:
                sentences = self._split_by_sentences(para)
                current_chunk = []
                current_length = 0
                
                for sentence in sentences:
                    # 如果当前块加上新句子超过最大长度，且当前块不为空，则保存当前块
                    if current_length + len(sentence) > self.max_chunk_size and current_chunk:
                        chunks.append({
                            "content": "".join(current_chunk),
                            "type": file_type,
                            "metadata": {
                                "chunk_index": chunk_index,
                                "split_type": "sentence",
                                "sentence_count": len(current_chunk)
                            }
                        })
                        chunk_index += 1
                        current_chunk = []
                        current_length = 0
                    
                    current_chunk.append(sentence)
                    current_length += len(sentence)
                
                # 保存最后一个块
                if current_chunk:
                    chunks.append({
                        "content": "".join(current_chunk),
                        "type": file_type,
                        "metadata": {
                            "chunk_index": chunk_index,
                            "split_type": "sentence",
                            "sentence_count": len(current_chunk)
                        }
                    })
                    chunk_index += 1
            else:
                # 3. 如果段落长度在合理范围内，直接作为一个块
                chunks.append({
                    "content": para,
                    "type": file_type,
                    "metadata": {
                        "chunk_index": chunk_index,
                        "split_type": "paragraph"
                    }
                })
                chunk_index += 1
        
        return chunks 