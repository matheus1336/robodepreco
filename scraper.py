import requests
from bs4 import BeautifulSoup
import random
import re
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

def scrape_product(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_selectors = [
            '.product-price .price', 
            '.productPrice',
            '.skuBestPrice',
            '.valor-por',
            '.price-current',
            '[data-testid="price"]',
            '.price',
            '.product-page-price',
            '.instant-price'
        ]
        
        for selector in price_selectors:
            price_element = soup.select_one(selector)
            if price_element:
                price_text = price_element.text.strip()
                price_text = re.sub(r'[^\d,]', '', price_text).replace(',', '.')
                try:
                    price = float(price_text)
                    
                    product_name = None
                    title_selectors = [
                        'h1.product-name', 
                        '.productName',
                        '.product-title',
                        '[data-testid="product-title"]'
                    ]
                    
                    for title_selector in title_selectors:
                        title_element = soup.select_one(title_selector)
                        if title_element:
                            product_name = title_element.text.strip()
                            break
                    
                    if not product_name:
                        product_name = url.split('/')[-1].replace('-', ' ').title()
                    
                    return {
                        'price': price,
                        'product_name': product_name,
                        'url': url,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'timestamp': datetime.now().timestamp()
                    }
                except ValueError:
                    continue
        
        return None
    except requests.Timeout:
        logging.error("Timeout ao tentar acessar a página.")
        raise Exception("Timeout ao acessar a página")
    except requests.RequestException as e:
        logging.error(f"Erro ao acessar a página: {e}")
        raise Exception(f"Erro ao acessar a página: {str(e)}")
