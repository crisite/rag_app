from typing import List, Dict, Any
import PyPDF2
from .file_reader import BaseFileReader

class PDFReader(BaseFileReader):
    """PDF文件读取器"""
    
    def read(self) -> str:
        """
        读取PDF文件内容
        
        Returns:
            str: PDF文件内容
        """
        content = []
        with open(self.file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content.append(page.extract_text())
        return '\n'.join(content)
    
    def parse(self) -> List[Dict[str, Any]]:
        """
        解析PDF文件内容为结构化数据
        
        Returns:
            List[Dict[str, Any]]: 解析后的结构化数据列表
        """
        metadata = self.get_metadata()
        content = self.read()
        
        # 按页分割内容
        with open(self.file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pages = []
            for i, page in enumerate(pdf_reader.pages):
                pages.append({
                    "content": page.extract_text(),
                    "metadata": {
                        **metadata,
                        "page_number": i + 1,
                        "total_pages": len(pdf_reader.pages)
                    }
                })
        
        return pages 