from arxiv_api import ArxivPaperCrawler
import os
import fitz  # PyMuPDF

def save_processed_pdf(pdf_path: str, output_dir: str):
    """保存预处理后的PDF文本到指定目录"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    """
    等效于
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    """
    
    # 使用ArxivPaperCrawler的提取方法
    crawler = ArxivPaperCrawler([])  # 空查询列表
    processed_text = crawler.extract_main_content(pdf_path)
    
    # 生成输出文件名
    base_name = os.path.basename(pdf_path).replace('.pdf', '_processed.txt')
    output_path = os.path.join(output_dir, base_name)
    
    # 保存处理后的文本
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(processed_text)
    
    print(f"已保存预处理文本到: {output_path}")
    return output_path

if __name__ == "__main__":
    # 示例PDF路径
    pdf_path = r"C:\Users\wusi\source\repos\Crawler_warehouse\result\graph neural network_Trajectory prediction\original_dir\2025-03-26\2503.18911v1.pdf"
    
    # 输出目录
    output_dir = r"C:\Users\wusi\source\repos\Crawler_warehouse\result\processed_texts"
    
    # 调用处理函数
    processed_file = save_processed_pdf(pdf_path, output_dir)
    
    # 可选：打印前500字符验证
    with open(processed_file, 'r', encoding='utf-8') as f:
        print(f.read()[:500])