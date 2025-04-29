#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from urllib.parse import urlparse
import re
import sys
from readability import Document

def get_url_from_user():
    """Get URL from user input or stdin."""
    try:
        # Get data from stdin if available
        if not sys.stdin.isatty():
            
            url = sys.stdin.buffer.read()
            
            
            if isinstance(url, bytes):
                url = url.decode('utf-8', errors='replace')
            
            return url.strip()
        else:
            
            return input("").strip()
    except Exception as e:
        log_error(f"Error reading input: {e}")
        return ""

def is_valid_url(url):
    """Check if the given string is a valid URL."""
    if not url:
        return False
        
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    except Exception as e:
        log_error(f"Error validating URL: {e}")
        return False

def method1_bs4(url):
    """Parse main content from URL using BeautifulSoup."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаляем ненужные элементы
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # Search for main content
        article_content = ""
        
        # First, look for the article tag
        article_tag = soup.find('article')
        if article_tag:
            for p in article_tag.find_all('p'):
                article_content += p.get_text() + "\n\n"
            if article_content:
                return article_content.strip()
        
        # Search for divs with classes containing 'content' or 'article'
        content_divs = soup.find_all('div', class_=lambda c: c and ('content' in c.lower() or 'article' in c.lower()))
        for div in content_divs:
            for p in div.find_all('p'):
                article_content += p.get_text() + "\n\n"
            if article_content:
                return article_content.strip()
        
        # Simply collect all paragraphs
        if not article_content:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                article_content += p.get_text() + "\n\n"
        
        return article_content.strip()
    except Exception as e:
        return f"Error in method 1: {str(e)}"

def method2_newspaper(url):
    """Parse main content from URL using Newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text:
            return article.text.strip()
        else:
            return ""
    except Exception as e:
        return f"Error in method 2: {str(e)}"

def method3_readability(url):
    """Parse main content from URL using Readability."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        doc = Document(response.text)
        content = doc.summary()
        
        # Очистка от HTML тегов
        soup = BeautifulSoup(content, 'html.parser')
        clean_text = soup.get_text()
        
        # Normalize whitespace
        clean_text = re.sub(r'\n+', '\n\n', clean_text)
        clean_text = re.sub(r' +', ' ', clean_text)
        
        return clean_text.strip()
    except Exception as e:
        return f"Error in method 3: {str(e)}"

def method4_direct_extraction(url):
    """Direct extraction of text from all elements."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаляем ненужные элементы
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'aside']):
            tag.decompose()
        
        # Collect text from all elements
        all_text = soup.get_text(separator='\n')
        
        # Очистка текста
        clean_text = re.sub(r'\n+', '\n\n', all_text)
        clean_text = re.sub(r' +', ' ', clean_text)
        
        return clean_text.strip()
    except Exception as e:
        return f"Error in method 4: {str(e)}"

def compare_methods(url):
    """Compare different parsing methods and select the best result."""
    method1_result = method1_bs4(url)
    method2_result = method2_newspaper(url)
    method3_result = method3_readability(url)
    method4_result = method4_direct_extraction(url)
    
    results = [method1_result, method2_result, method3_result, method4_result]
    best_result = ""
    best_length = 0
    
    for result in results:
        # Skip results with errors or too short
        if result.startswith("Error") or len(result) < 100:
            continue
            
        if len(result) > best_length:
            best_length = len(result)
            best_result = result
    
    # If all methods failed, return the longest result
    if not best_result:
        best_result = max(results, key=len)
    
    return best_result

def clean_text(text):
    """Additional text cleaning from unwanted elements."""
    # Normalize whitespace
    text = re.sub(r'\n+', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove common ad and social media patterns
    patterns_to_remove = [
        r'Подписаться на.*',
        r'Читайте также:.*',
        r'Поделиться:.*',
        r'Share.*',
        r'Комментарии.*',
        r'Copyright ©.*',
        r'\d+ комментари(й|ев).*',
        r'Реклама.*',
        r'Advertisement.*',
        r'Загрузка комментариев.*',
        r'Популярное:.*',
        r'По теме:.*',
        r'Источник:.*',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def log_error(message):
    """Log error message to file."""
    try:
        with open("parser_error.log", "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except:
        pass  

def main():
    try:
        url = get_url_from_user()
        
        if not url:
            log_error("Empty URL received")
            return
            
        if not is_valid_url(url):
            log_error(f"Invalid URL: {url}")
            return
        
        # Try Readability method first for best results
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            doc = Document(response.text)
            content = doc.summary()
            
            # Extract text from HTML
            soup = BeautifulSoup(content, 'html.parser')
            article_text = soup.get_text()
            
            # Clean the extracted text
            clean_article = clean_text(article_text)
            
            
            if clean_article and len(clean_article) > 150:
                print(clean_article)
                return
        except Exception as e:
            log_error(f"Readability method failed: {str(e)}")
        
        # Fallback to other parsing methods if Readability fails
        best_text = compare_methods(url)
        
        if best_text:
            clean_result = clean_text(best_text)
            print(clean_result)
        else:
            log_error(f"All parsing methods failed for URL: {url}")
    
    except Exception as e:
        log_error(f"Unexpected error in main: {str(e)}")
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_error(f"Critical error: {str(e)}")