"""URL Intelligence and threat checking module"""

import re
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class URLIntelligence:
    """Advanced URL threat detection and intelligence"""
    
    # Known phishing keywords
    PHISHING_KEYWORDS = [
        'verify', 'confirm', 'update', 'validate', 'secure', 'urgent',
        'action', 'click', 'login', 'password', 'account', 'suspended',
        'limited', 'unusual', 'unauthorized', 'suspicious', 'compromise'
    ]
    
    # Suspicious TLDs
    SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.info', '.bid', '.xyz']
    
    @staticmethod
    def check_url_reputation(url: str) -> dict:
        """Check URL reputation against threat databases"""
        try:
            # Parse URL
            parsed = urlparse(url)
            domain = parsed.netloc
            
            threat_score = 0
            indicators = []
            
            # Check for suspicious patterns
            if URLIntelligence._has_phishing_keywords(url):
                threat_score += 3
                indicators.append('Phishing keywords detected')
            
            # Check domain reputation
            if URLIntelligence._is_suspicious_domain(domain):
                threat_score += 2
                indicators.append('Suspicious domain pattern')
            
            # Check for homograph attacks
            if URLIntelligence._has_homograph_chars(domain):
                threat_score += 2
                indicators.append('Homograph attack indicators')
            
            # Check URL shortener
            if URLIntelligence._is_url_shortener(domain):
                threat_score += 1
                indicators.append('URL shortener detected')
            
            # Check for suspicious TLD
            if any(domain.endswith(tld) for tld in URLIntelligence.SUSPICIOUS_TLDS):
                threat_score += 2
                indicators.append('Suspicious TLD detected')
            
            # Determine risk level
            if threat_score >= 5:
                risk_level = 'DANGER'
            elif threat_score >= 3:
                risk_level = 'SUSPICIOUS'
            else:
                risk_level = 'SAFE'
            
            return {
                'url': url,
                'domain': domain,
                'threat_score': min(threat_score, 10),
                'risk_level': risk_level,
                'indicators': indicators,
                'is_safe': risk_level == 'SAFE'
            }
            
        except Exception as e:
            logger.error(f"Error checking URL reputation: {e}")
            return {
                'url': url,
                'threat_score': 0,
                'risk_level': 'UNKNOWN',
                'indicators': ['Analysis error'],
                'is_safe': False
            }
    
    @staticmethod
    def _has_phishing_keywords(url: str) -> bool:
        """Check if URL contains phishing keywords"""
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in URLIntelligence.PHISHING_KEYWORDS)
    
    @staticmethod
    def _is_suspicious_domain(domain: str) -> bool:
        """Check if domain has suspicious patterns"""
        # Check for typosquatting (misspelled popular domains)
        popular_domains = ['amazon', 'apple', 'google', 'facebook', 'microsoft', 'paypal']
        
        for popular in popular_domains:
            # Check for common misspellings
            if popular in domain and domain != f'{popular}.com':
                # More suspicious if it's a typo-like variation
                if len(domain) - len(popular) <= 3:
                    return True
        
        # Check for too many hyphens or underscores
        if domain.count('-') >= 3 or domain.count('_') >= 1:
            return True
        
        # Check for numbers replacing letters (l33t)
        if re.search(r'[0O]', domain) and re.search(r'[l1I]', domain):
            return True
        
        return False
    
    @staticmethod
    def _has_homograph_chars(domain: str) -> bool:
        """Check for homograph attack attempts (lookalike characters)"""
        # Cyrillic 'a' looks like Latin 'a'
        homoglyph_patterns = [
            r'[а-яё]',  # Cyrillic
            r'[0Оo].*[0Оo]',  # Multiple zero/O variations
            r'[1l|I].*[1l|I]',  # Multiple one/l variations
        ]
        
        for pattern in homoglyph_patterns:
            if re.search(pattern, domain):
                return True
        
        return False
    
    @staticmethod
    def _is_url_shortener(domain: str) -> bool:
        """Check if URL uses a shortener service"""
        shorteners = ['bit.ly', 'tinyurl', 'ow.ly', 'goo.gl', 'short.link', 'rebrand.ly']
        return any(shortener in domain for shortener in shorteners)
    
    @staticmethod
    def check_domain_age(domain: str) -> dict:
        """Check approximate domain age (simplified version)"""
        try:
            # This is a simplified check - in production, use WHOIS API
            # For now, return placeholder
            return {
                'domain': domain,
                'estimated_age': 'Unknown',
                'is_new': False,
                'risk_indicator': 'Low'
            }
            
        except Exception as e:
            logger.error(f"Error checking domain age: {e}")
            return {
                'domain': domain,
                'estimated_age': 'Unknown',
                'is_new': False,
                'risk_indicator': 'Unknown'
            }
    
    @staticmethod
    def get_url_preview(url: str) -> dict:
        """Get preview information about URL destination"""
        try:
            # This would fetch page title, description, etc.
            # For now, return basic info
            parsed = urlparse(url)
            
            return {
                'url': url,
                'domain': parsed.netloc,
                'protocol': parsed.scheme,
                'path': parsed.path,
                'query': parsed.query
            }
            
        except Exception as e:
            logger.error(f"Error getting URL preview: {e}")
            return {
                'url': url,
                'error': str(e)
            }
