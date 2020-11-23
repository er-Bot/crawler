from urllib.request import Request, urlopen
import io_manager
import domain_manager

from html.parser import HTMLParser
from urllib import parse

#a spider is an instance of workers to navigate a websie and get it's source code
class Spider:
    
    # shared among all instances
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    
    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)
        
    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        io_manager.create_project_dir(Spider.project_name)
        io_manager.create_data_files(Spider.project_name, Spider.base_url)
        print("=============== Booting ==================")
        print("Boot Queue File : " + Spider.queue_file)
        
        Spider.queue = io_manager.file_to_set(Spider.queue_file)
        
        print("Boot Queue : " + str(Spider.queue))
        print("Boot Crawled File : " + Spider.crawled_file)
        
        Spider.crawled = io_manager.file_to_set(Spider.crawled_file)
        
        print("Boot Crawled : " + str(Spider.crawled))
        print("==========================================")
        
        
    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        hdr = {'User-Agent':'Mozilla/5.0',}
        req = Request(page_url, headers=hdr)
        try:
            response = urlopen(req)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkParser(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != domain_manager.get_domain_name(url):
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        io_manager.set_to_file(Spider.queue, Spider.queue_file)
        io_manager.set_to_file(Spider.crawled, Spider.crawled_file)
        
class LinkParser(HTMLParser):
    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links
        
    def error(self, message):
        pass