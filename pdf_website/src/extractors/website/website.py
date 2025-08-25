import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from urllib.robotparser import RobotFileParser
from typing import Dict

class WebsiteCrawler:
    def __init__(self):
        self.delay = 1
        self.chunk_size = 1024
        self.overlap_percentage = 20
    
    def input_and_extraction(self):
        """Get URL from user and extract text with chunking and metadata"""
        url = input("Enter website URL: ").strip()
        max_pages = int(input("Enter max pages to crawl (default 5): ").strip() or "5")
        
        print(f"\nProcessing website: {url}")
        crawled_data = self.crawl(url, max_pages)
        
        if not crawled_data:
            print("No content extracted from website")
            return []
        
        # Create chunks with URL metadata
        chunks_with_metadata = []
        for page_url, content in crawled_data.items():
            page_chunks = self._create_chunks_with_metadata(content, page_url)
            chunks_with_metadata.extend(page_chunks)
        
        print(f"Created {len(chunks_with_metadata)} overlapping chunks from website content")
        return chunks_with_metadata
    
    def _create_chunks_with_metadata(self, text, metadata):
        """Create overlapping chunks with metadata"""
        chunks = []
        overlap_size = int(self.chunk_size * self.overlap_percentage / 100)
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            
            if len(chunk) > 50:
                chunks.append((chunk, metadata))
            
            start = end - overlap_size
            if end >= len(text):
                break
        
        return chunks
    
    def crawl(self, start_url: str, max_pages: int = 20) -> Dict[str, str]:
        """Crawl website and return extracted content"""
        start_url = self._normalize_url(start_url)
        domain = urlparse(start_url).netloc
        visited_urls = set()
        urls_to_visit = deque([start_url])
        crawled_pages = {}
        
        # Load robots.txt
        rp = RobotFileParser()
        robots_url = urljoin(start_url, "/robots.txt")
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception as e:
            print(f"Could not read robots.txt for {domain}: {e}")
        
        page_count = 0
        
        while urls_to_visit and page_count < max_pages:
            current_url = urls_to_visit.popleft()
            
            if current_url in visited_urls:
                continue
            
            if not rp.can_fetch("*", current_url):
                print(f"Skipping {current_url} due to robots.txt exclusion")
                visited_urls.add(current_url)
                continue
            
            print(f"Crawling: {current_url}")
            visited_urls.add(current_url)
            
            try:
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()
                time.sleep(self.delay)
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = self._extract_clean_text(soup)
                crawled_pages[current_url] = page_text
                page_count += 1
                
                # Find new links - prioritize same topic/related pages
                base_topic = self._extract_topic_from_url(start_url)
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    absolute_url = urljoin(current_url, href)
                    parsed_url = urlparse(absolute_url)
                    
                    if (parsed_url.netloc == domain and 
                        absolute_url not in visited_urls and 
                        absolute_url not in urls_to_visit and
                        not parsed_url.scheme.startswith(('mailto', 'tel')) and
                        not absolute_url.lower().endswith(('.pdf', '.jpg', '.png', '.gif', '.zip')) and
                        self._is_related_page(absolute_url, base_topic)):
                        urls_to_visit.append(absolute_url)
                        
            except requests.exceptions.RequestException as e:
                print(f"Error crawling {current_url}: {e}")
            except Exception as e:
                print(f"Unexpected error for {current_url}: {e}")
        
        print(f"Finished crawling. Total pages: {len(crawled_pages)}")
        return crawled_pages
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL by adding https if no scheme"""
        if not urlparse(url).scheme:
            url = "https://" + url
        return urljoin(url, urlparse(url).path)
    
    def _extract_clean_text(self, soup) -> str:
        """Extract clean text from BeautifulSoup object"""
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    
    def _extract_topic_from_url(self, url):
        """Extract main topic from URL"""
        # For Wikipedia: extract main article name
        if 'wikipedia.org/wiki/' in url:
            topic = url.split('/wiki/')[-1].split('#')[0]
            return topic.lower()
        # For other sites: use domain + first path segment
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        return f"{parsed.netloc}/{path_parts[0] if path_parts else ''}".lower()
    
    def _is_related_page(self, url, base_topic):
        """Check if URL is related to base topic"""
        url_lower = url.lower()
        
        # For Wikipedia: allow same article sections and related topics
        if 'wikipedia.org/wiki/' in url_lower:
            if base_topic in url_lower:  # Same article or its sections
                return True
            # Skip common Wikipedia navigation pages
            skip_pages = ['main_page', 'special:', 'wikipedia:', 'portal:', 'help:', 'category:']
            return not any(skip in url_lower for skip in skip_pages)
        
        # For other sites: stay within same domain and topic area
        return base_topic.split('/')[0] in url_lower