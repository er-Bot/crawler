import threading
from queue import Queue

from spider import Spider
import domain_manager, io_manager


class Crawler:
    
    PROJECT_NAME = ''
    HOMEPAGE = ''
    DOMAIN_NAME = ''
    QUEUE_FILE = ''
    CRAWLED_FILE = ''
    NUMBER_OF_THREADS = 8
    queue = Queue()
    
    def __init__(self, project_name, home_page):
        print("========= Starting Crawler =============")
        print("PROJECT_NAME = " + project_name)
        print("HOMEPAGE " + home_page) 
        print()
        Crawler.PROJECT_NAME = project_name
        Crawler.HOMEPAGE = home_page
        Crawler.DOMAIN_NAME = domain_manager.get_domain_name(Crawler.HOMEPAGE)
        Crawler.QUEUE_FILE = Crawler.PROJECT_NAME + '/queue.txt'
        Crawler.CRAWLED_FILE = Crawler.PROJECT_NAME + '/crawled.txt'
        
        # First spider (responsible for the creation of files)
        Spider(Crawler.PROJECT_NAME, Crawler.HOMEPAGE, Crawler.DOMAIN_NAME) 
        
        # Create worker threads (will die when main exits)
        for _ in range(Crawler.NUMBER_OF_THREADS):
            t = threading.Thread(target=Crawler.job)
            t.daemon = True
            t.start()
        Crawler.crawl()
        
    # Do the next job in the queue
    def job():
        while True:
            url = Crawler.queue.get()
            print(url)
            Spider.crawl_page(threading.current_thread().name, url)
            Crawler.queue.task_done()
    
    
    # Each queued link is a new job
    def create_jobs():
        for link in io_manager.file_to_set(Crawler.QUEUE_FILE):
            Crawler.queue.put(link)
        Crawler.queue.join()
        Crawler.crawl()
    
    
    # Check if there are items in the queue, if so crawl them
    def crawl():
        queued_links = io_manager.file_to_set(Crawler.QUEUE_FILE)
        if len(queued_links) > 0:
            print(str(len(queued_links)) + ' links in the queue')
            Crawler.create_jobs()