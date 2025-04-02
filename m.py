import re
import random;from curl_cffi import requests,CurlHttpVersion;from loguru import logger
from moviepy.editor import VideoFileClip, AudioFileClip
import os
def extract_content(text, markers):
    """
    从给定的字符串中提取指定标记之间的内容。

    参数:
    text (str): 要处理的字符串。
    markers (tuple): 一个包含两个元素的元组，第一个元素是起始标记，第二个元素是结束标记。

    返回:
    str: 起始和结束标记之间的内容。如果没有找到标记，则返回空字符串。
    """
    start_marker, end_marker = markers
    start_index = text.find(start_marker)
    if start_index == -1:
        return ''

    start_index += len(start_marker)
    end_index = text.find(end_marker, start_index)
    if end_index == -1:
        return ''

    return text[start_index:end_index]

class blbl():
    def __init__(self,url,proxy):
        self.s = requests.Session()
        self.s.http_version = CurlHttpVersion.V1_1
        impersonate_v = ['chrome99', 'chrome100', 'chrome101', 'chrome104', 'chrome107', 'chrome110', 'chrome116',
                         'chrome119', 'chrome120', 'chrome123', 'chrome124']
        self.s.impersonate = random.choice(impersonate_v)
        self.ua = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100, 133)}.0.0.0 Safari/537.36'
        self.url=url
        self.proxies = {'https': proxy, 'http': proxy}
        self.s.proxies = self.proxies
    def _video_get(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.ua,
        }

        r=self.s.get(self.url,headers=headers)
        print(r.text)
        self.low_q_video_url = extract_content(r.text, ('"backup_url":["', '",'))
        logger.debug(self.low_q_video_url)

        self.low_q_audio_url = extract_content(r.text, ('{"id":30216,"baseUrl":"', '",'))
        logger.debug(self.low_q_audio_url)

        self.title = extract_content(r.text, ('meta="true">', '_哔哩哔哩'))+'.mp4'
        logger.debug(self.title)
    def _video_save(self):
        headers = {
            'referer': 'https://www.bilibili.com/',
            'user-agent':self.ua,
        }
        video = self.s.get(self.low_q_video_url, headers=headers)
        with open("video.mp4", "wb") as f:
            f.write(video.content)
        print("视频下载完成！")
        audio = self.s.get(self.low_q_audio_url, headers=headers)
        with open("video.mp3", "wb") as f:
            f.write(audio.content)
    def _video_merge(self,video_file="video.mp4",audio_file="video.mp3"):
       # 转换为 MP4（H.264 + AAC）
       video = VideoFileClip(video_file)
       audio = AudioFileClip(audio_file)
       # 设置视频的音频
       video = video.set_audio(audio)
       # 导出合成后的视频
       video.write_videofile(self.title, codec="libx264", audio_codec="aac")
    def _video_delete(self):
        file_path = "video.mp4"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"{file_path} 不存在")
        file_path = "video.mp3"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"{file_path} 不存在")
    def _start(self):
        self._video_get()
        self._video_save()
        self._video_merge()
        self._video_delete()
        logger.success('视频保存成功')
        return True
if __name__ == '__main__':
    proxy=''
    url= input("输入链接：")
    blbl(url,proxy)._start()
