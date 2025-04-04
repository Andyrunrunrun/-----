import os
import argparse
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup


def extract_download_links(url):
    if url.startswith("https://huggingface.co"):
        url = url.replace("huggingface.co", "hf-mirror.com")  # 替换成镜像网址
    # 发送GET请求获取网页内容
    response = requests.get(url)
    mirror_url = "https://hf-mirror.com"
    # 检查响应状态码
    if response.status_code == 200:
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有带有 "download" 关键字的链接
        download_links = []
        for link in soup.find_all('a', href=True):
            if 'download' in link['href']:
                download_link = mirror_url + link['href']
                download_links.append(download_link)

        return download_links
    else:
        print("Failed to fetch the page.")
        return []


def download_files(links, output_path):
    if not os.path.exists(output_path):
        print(f"create filepath: {output_path}")
        os.makedirs(output_path)
    for link in links:
        if output_path[-1] != '/':  # 防止出现路径错误
            output_path += '/'
        filename = output_path + link.split('/')[-1].split('?')[0]  # 从链接中提取文件名
        try:
            # 发送GET请求下载文件
            response = requests.get(link, stream=True)
            total_size = int(response.headers.get('content-length', 0))  # 获取文件总大小
            if response.status_code == 200:
                print(f"Downloading: {filename}")
                # 将文件内容写入本地文件
                with open(filename, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename, ascii=True) as pbar:
                        for data in response.iter_content(chunk_size=1024):
                            f.write(data)
                            pbar.update(len(data))
                print(f"download success: {filename}")
            else:
                print(f"download failure: {filename}")
        except Exception as e:
            print(f"下载出错: {filename}, 错误信息: {str(e)}")


if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="下载模型文件")
    parser.add_argument('-r', '--url', type=str, default="https://huggingface.co/google-bert/bert-base-chinese/tree/main",
                        help='要下载的文件的URL')
    parser.add_argument('-p', '--path', type=str, default="/home/cike/pre-trained/bert-base-chinese", help='要保存的文件路径')
    # 解析命令行参数
    args = parser.parse_args()

    # 检查是否提供了必要的参数
    if args.url and args.path:
        download_links = extract_download_links(args.url)
        download_files(download_links, args.path)
    else:
        print("请提供下载链接和保存路径。")

