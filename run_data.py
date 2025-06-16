import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, # 可以根据需要修改为 logging.DEBUG, logging.WARNING, logging.ERROR, logging.CRITICAL
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

import os
import tomli
from typing import Dict, Any
from tools.data_processor import DataProcessor
import asyncio

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    with open("config/config.toml", "rb") as f:
        return tomli.load(f)

def process_single_file(file_path: str) -> None:
    """
    处理单个文件，并将其向量化后存储到向量数据库中。
    Args:
        file_path: 待处理的文件路径。
    """
    config = load_config()
    data_processor = DataProcessor(config_path="config/config.toml")
    collection_name = config["rag"]["collection_name"]
    data_processor.process_single_document(file_path, collection_name)

def process_directory(directory_path: str) -> None:
    """
    处理指定目录下的所有文档，并将其向量化后存储到向量数据库中。
    Args:
        directory_path: 待处理的目录路径。
    """
    config = load_config()
    data_processor = DataProcessor(config_path="config/config.toml")
    collection_name = config["rag"]["collection_name"]
    data_processor.process_document_directory(directory_path, collection_name)

if __name__ == '__main__':
    # 加载配置，获取文档目录
    config = load_config()
    doc_dir = config["rag"]["document"]["document_directory"]
    collection_name = config["rag"]["collection_name"]

    print("请选择操作模式:")
    print("1. 处理单个文件 (输入文件路径)")
    print("2. 处理整个文档目录")

    choice = input("请输入你的选择 (1 或 2): ")

    if choice == '1':
        file_path = input("请输入要处理的文件路径: ")
        if not os.path.exists(file_path):
            print(f"错误: 文件路径不存在: {file_path}")
        elif not os.path.isfile(file_path):
            print(f"错误: 指定路径不是一个文件: {file_path}")
        else:
            process_single_file(file_path)
    elif choice == '2':
        print(f"将处理配置中指定的文档目录: {doc_dir}")
        if not os.path.exists(doc_dir):
            print(f"文档目录不存在，将自动创建: {doc_dir}")
            os.makedirs(doc_dir)
        process_directory(doc_dir)
    else:
        print("无效的选择。请重新运行脚本并选择 1 或 2。")