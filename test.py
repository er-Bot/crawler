from crawler import Crawler
import os, shutil


if os.path.exists("sina"):
    shutil.rmtree("sina")
crawler = Crawler("sina", "https://www.sina.com.cn/")