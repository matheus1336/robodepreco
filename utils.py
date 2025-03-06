import pandas as pd
import os
from datetime import datetime
import json

def validate_url(url):
    """Validate if the URL is in the correct format and from supported domains"""
    supported_domains = ['meritocomercial.com.br']  # Add more domains as needed
    
    if not url.startswith(('http://', 'https://')):
        return False, "URL deve começar com http:// ou https://"
        
    domain = url.split('/')[2]
    if not any(supported in domain for supported in supported_domains):
        return False, "Domínio não suportado"
        
    return True, ""

def load_products():
    """Load products from CSV file"""
    if not os.path.exists('products.csv'):
        return pd.DataFrame(columns=['url', 'product_name', 'last_price', 'last_check'])
    return pd.read_csv('products.csv')

def save_products(df):
    """Save products to CSV file"""
    df.to_csv('products.csv', index=False)

def load_price_history(url):
    """Load price history for a specific product"""
    filename = f"price_history/{hash(url)}.csv"
    if not os.path.exists(filename):
        return pd.DataFrame(columns=['date', 'price'])
    return pd.read_csv(filename)

def save_price_history(url, price_data):
    """Save price history for a specific product"""
    os.makedirs('price_history', exist_ok=True)
    filename = f"price_history/{hash(url)}.csv"
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=['date', 'price'])
    
    new_row = pd.DataFrame({
        'date': [price_data['date']],
        'price': [price_data['price']]
    })
    
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(filename, index=False)

def format_price(price):
    """Format price in Brazilian Real format"""
    return f"R$ {price:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
