"""Advanced AI Email Analyzer - All 4 Detectors"""

import logging
import re
import json
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AdvancedEmailAnalyzer:
    """Advanced AI analyzer with 4 detection methods"""
    
    def __init__(self):
        """Initialize analyzer with threat patterns"""
        
        # Phishing patterns
        self.phishing_keywords = [
            "verify", "confirm", "urgent", "immediately", "click here", 
            "update account", "login", "password reset", "suspended",
            "unauthorized access", "action required", "alert", "security notice"
        ]
        
        self.phishing_urgency = [
            "immediately", "urgent", "right now", "asap", "limited time",
            "expire", "24 hours", "act now", "don't delay"
        ]
        
        # Malware patterns
        self.malware_extensions = [
            '.exe', '.bat', '.com', '.scr', '.vbs', '.js',
            '.jar', '.zip', '.rar', '.msi', '.dll', '.pif'
        ]
        
        self.dangerous_keywords = [
            "executable", "run this", "install", "activate", "enable macro",
            "download attachment", "open attachment"
        ]
        
        # Sender spoofing patterns
        self.suspicious_domains = [
            'company.fake', 'bank-secure', 'verify-account', 'login-',
            'confirm-identity', 'update-password'
        ]
        
        # Legitimate domain keywords (for comparison)
        self.legitimate_tlds = ['.com', '.org', '.gov', '.edu', '.net', '.co.uk']
    
    def analyze_email(self, email_data: Dict) -> Dict:
        """
        Comprehensive email analysis
        
        Args:
            email_data: {
                'from': sender email,
                'subject': email subject,
                'body_preview': email body,
                'has_attachment': bool,
                'attachments': list of attachment names
            }
        
        Returns:
            {
                'threat_level': 'safe'|'warning'|'danger',
                'risk_score': 0-100,
                'threats_detected': list,
                'ai_explanation': str,
                'recommendations': list
            }
        """
        try:
            # Run all 5 analyzers (including new link detection)
            phishing_score, phishing_threats = self._detect_phishing(email_data)
            malware_score, malware_threats = self._detect_malware(email_data)
            sender_score, sender_threats = self._analyze_sender(email_data)
            urgency_score, urgency_threats = self._detect_urgency(email_data)
            link_score, link_threats = self._detect_dangerous_links(email_data)
            
            # Combine scores with weighted average (normalized)
            # Use higher weights on more confident detections
            total_score = (
                phishing_score * 0.25 +    # Phishing (25%)
                malware_score * 0.25 +     # Malware (25%)
                link_score * 0.40 +        # Dangerous links (40% - PRIMARY!)
                sender_score * 0.10 +      # Sender analysis (10%)
                urgency_score * 0.00       # Urgency disabled (0%)
            )
            
            risk_score = min(100, int(total_score))
            
            # Determine threat level with adjusted thresholds
            if risk_score >= 45:
                threat_level = 'danger'
            elif risk_score >= 25:
                threat_level = 'warning'
            else:
                threat_level = 'safe'
            
            # Combine all threats
            all_threats = (phishing_threats + malware_threats + 
                          link_threats + sender_threats + urgency_threats)
            
            # Generate explanation
            explanation = self._generate_explanation(
                threat_level, all_threats, risk_score, email_data
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                all_threats, threat_level, email_data
            )
            
            return {
                'threat_level': threat_level,
                'risk_score': risk_score,
                'threats_detected': list(set(all_threats)),
                'ai_explanation': explanation,
                'recommendations': recommendations,
                'analyzed_at': datetime.utcnow().isoformat(),
                'confidence': min(100, risk_score + 10)
            }
        
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}", exc_info=True)
            return {
                'threat_level': 'unknown',
                'risk_score': 50,
                'threats_detected': ['Analysis Error'],
                'ai_explanation': 'Could not analyze email',
                'recommendations': [],
                'analyzed_at': datetime.utcnow().isoformat()
            }
    
    def _detect_phishing(self, email_data: Dict) -> Tuple[int, List[str]]:
        """Detect phishing attempts (35% weight)"""
        score = 0
        threats = []
        
        subject = (email_data.get('subject') or '').lower()
        body = (email_data.get('body_preview') or '').lower()
        from_addr = (email_data.get('from') or '').lower()
        
        text = f"{subject} {body}"
        
        # Phishing keyword detection
        phishing_count = sum(1 for kw in self.phishing_keywords if kw in text)
        if phishing_count >= 3:
            score += 45
            threats.append("Phishing Keywords Detected")
        elif phishing_count >= 2:
            score += 25
            threats.append("Phishing Keywords Detected")
        elif phishing_count == 1:
            score += 10
        
        # Suspicious phrases (weighted heavily)
        suspicious_phrases = [
            ("click here immediately", 30),
            ("verify your account", 25),
            ("confirm your password", 25),
            ("update your information", 20),
            ("unusual activity detected", 20),
            ("verify account", 20),
            ("confirm password", 20)
        ]
        
        for phrase, weight in suspicious_phrases:
            if phrase in text:
                score += weight
                threats.append("Suspicious Phrase")
                break
        
        # All caps in subject (urgency tactic)
        if subject and len(subject) > 5 and subject.isupper():
            score += 15
            threats.append("Urgency Tactic (ALL CAPS)")
        
        # Excessive punctuation
        if text.count('!!') > 0:
            score += 15
        elif text.count('!') >= 3:
            score += 10
        
        return min(100, score), threats
    
    def _detect_malware(self, email_data: Dict) -> Tuple[int, List[str]]:
        """Detect malware/dangerous attachments (30% weight)"""
        score = 0
        threats = []
        
        has_attachment = email_data.get('has_attachment', 0)
        attachments = email_data.get('attachments', [])
        body = (email_data.get('body_preview') or '').lower()
        
        # Check attachments (highest weight)
        if has_attachment and attachments:
            for attachment in attachments:
                attachment_lower = attachment.lower()
                
                # Check for executable extensions (highest risk)
                for ext in self.malware_extensions:
                    if attachment_lower.endswith(ext):
                        score += 50  # Dangerous executable
                        threats.append(f"Dangerous Attachment: {attachment}")
                        break
                
                # Check for archive files (zip, rar, 7z) - can hide executables
                archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz']
                for ext in archive_extensions:
                    if attachment_lower.endswith(ext):
                        score += 55  # Archives can hide malware - CRITICAL
                        threats.append(f"CRITICAL: Archive File Detected - May Contain Malware: {attachment}")
                        break
            
            # If any attachment present, add baseline risk
            score += 15
            threats.append(f"Attachment Present ({len(attachments)} file(s))")
        
        # Malware keywords in body
        dangerous_keywords = [
            "enable macro", "run this", "install", "activate",
            "download attachment", "open attachment"
        ]
        
        # Keywords suggesting attachment execution
        attachment_execution = [
            "open.*attachment", "run.*attachment", "download.*zip",
            "extract.*file", "unzip", "open.*file", "run.*file"
        ]
        
        for kw in dangerous_keywords + attachment_execution:
            if kw in body:
                score += 35  # Increased - execution requests are critical
                threats.append("Malware Indicators in Text")
                break
        
        # Encoded content (suspicious)
        if re.search(r'%[0-9a-fA-F]{2}', body) or 'base64' in body:
            score += 15
            threats.append("Encoded/Obfuscated Content")
        
        return min(100, score), threats
    
    def _analyze_sender(self, email_data: Dict) -> Tuple[int, List[str]]:
        """Analyze sender reputation (20% weight)"""
        score = 0
        threats = []
        
        from_addr = (email_data.get('from') or '').lower()
        attachments = email_data.get('attachments', []) or []
        
        if not from_addr:
            score += 20
            threats.append("Missing Sender Information")
            return score, threats
        
        # CRITICAL: Unknown sender + attachments (especially archives) is very suspicious
        has_archive = any(att.lower().endswith(ext) for att in attachments 
                         for ext in ['.zip', '.rar', '.7z', '.tar', '.gz'])
        if has_archive and ('unknown' in from_addr or 'suspicious' in from_addr or from_addr.count('@') != 1):
            score += 40
            threats.append("CRITICAL: Unknown Sender + Archive File = Likely Malware")
        
        # Extract domain
        try:
            domain = from_addr.split('@')[1].split('>')[0]
        except:
            score += 30
            threats.append("Invalid Email Format")
            return min(100, score), threats
        
        # Check for spoofing patterns (impersonating legitimate companies)
        spoofing_patterns = [
            ('bank', 35),
            ('paypal', 35),
            ('amazon', 35),
            ('apple', 35),
            ('microsoft', 35),
            ('google', 30),
            ('instagram', 30),
            ('facebook', 30),
            ('verify', 25),
            ('confirm', 25),
            ('secure', 20)
        ]
        
        sender_name = from_addr.split('@')[0].lower()
        for pattern, weight in spoofing_patterns:
            if pattern in domain and pattern not in sender_name:
                score += weight
                threats.append(f"Sender Spoofing (Impersonating {pattern})")
                break
        
        # Suspicious domain characteristics
        if any(sus in domain for sus in self.suspicious_domains):
            score += 25
            threats.append("Suspicious Domain")
        
        # Free email providers (higher risk when impersonating companies)
        free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'gmx.com']
        if domain in free_providers and not any(x in sender_name for x in ['admin', 'support', 'noreply']):
            score += 10
        
        return min(100, score), threats
    
    def _detect_urgency(self, email_data: Dict) -> Tuple[int, List[str]]:
        """Detect urgency-based manipulation (15% weight)"""
        score = 0
        threats = []
        
        subject = (email_data.get('subject') or '').lower()
        body = (email_data.get('body_preview') or '').lower()
        text = f"{subject} {body}"
        
        # Urgency keywords (weighted)
        urgency_keywords = [
            ("immediately", 20),
            ("urgent", 20),
            ("asap", 15),
            ("right now", 20),
            ("limited time", 20),
            ("24 hours", 15),
            ("act now", 15),
            ("don't delay", 15)
        ]
        
        for keyword, weight in urgency_keywords:
            if keyword in text:
                score += weight
                threats.append("High Urgency Language")
                break  # Count once
        
        # Time pressure ("expires", "deadline", etc)
        time_pressure = re.search(r'(\d+\s+hours?|expire|deadline|limited)', text)
        if time_pressure:
            score += 20
            threats.append(f"Time Pressure: {time_pressure.group()}")
        
        # Emotional manipulation keywords
        emotional_words = [
            ('worried', 15),
            ('concerned', 15),
            ('security', 10),
            ('alert', 10),
            ('danger', 15),
            ('breach', 20)
        ]
        
        emotional_count = 0
        for word, weight in emotional_words:
            if word in text:
                score += weight
                emotional_count += 1
        
        if emotional_count >= 2:
            threats.append("Emotional Manipulation")
        
        return min(100, score), threats
    
    def _detect_dangerous_links(self, email_data: Dict) -> Tuple[int, List[str]]:
        """Detect suspicious download links and file shares (Drive, Dropbox, etc)"""
        
        body = email_data.get('body_preview', '').lower()
        subject = email_data.get('subject', '').lower()
        text = f"{subject} {body}"
        
        score = 0
        threats = []
        
        # Google Drive links (especially downloads)
        if 'drive.google.com' in text:
            score += 75  # MASSIVE INCREASE - Trojan vector
            threats.append("Google Drive Link Detected - Common Malware Vector")
            
            # Drive links with download context
            if 'download' in text or '/d/' in text or '/view' in text:
                score += 50  # CRITICAL - Drive downloads are high risk
                threats.append("Drive File Download Link - HIGH RISK")
        
        # Dropbox links
        if 'dropbox.com' in text or 'dl.dropboxusercontent.com' in text:
            score += 30
            threats.append("Dropbox Link Detected")
        
        # OneDrive/SharePoint
        if 'onedrive.live.com' in text or 'sharepoint.com' in text:
            score += 25
            threats.append("OneDrive/SharePoint Link")
        
        # Short URL services (often hide malware)
        short_url_patterns = [
            r'bit\.ly', r'tinyurl\.com', r'short\.link', r'goo\.gl',
            r'tiny\.cc', r'ow\.ly', r'tr\.im'
        ]
        for pattern in short_url_patterns:
            if re.search(pattern, text):
                score += 50  # DOUBLED - Short URLs hide trojans
                threats.append(f"Suspicious Short URL ({pattern})")
                break
        
        # IP addresses instead of domain (very suspicious)
        if re.search(r'https?://\d+\.\d+\.\d+\.\d+', text):
            score += 40
            threats.append("IP Address URL (Highly Suspicious)")
        
        # Suspicious file extensions in URLs
        dangerous_extensions_in_url = [
            r'\.exe\b', r'\.bat\b', r'\.cmd\b', r'\.scr\b',
            r'\.vbs\b', r'\.msi\b', r'\.zip\b', r'\.rar\b'
        ]
        for ext in dangerous_extensions_in_url:
            if re.search(ext, text):
                score += 80  # CRITICAL - .exe/.bat in URL is trojan
                threats.append(f"Dangerous File Extension in URL: {ext}")
                break
        
        # Download-related context phrases
        download_phrases = [
            r'click.*download', r'download.*file', r'execute.*file',
            r'run.*file', r'install.*now', r'download.*attachment'
        ]
        for phrase in download_phrases:
            if re.search(phrase, text):
                score += 60  # TRIPLED - Download request + link = trojan
                threats.append("Download/Execution Request Detected")
                break
        
        # Suspicious domains hosting files
        suspicious_file_hosts = [
            r'mediafire\.com', r'mega\.nz', r'zippyshare\.com',
            r'4shared\.com', r'rapidshare\.com'
        ]
        for host in suspicious_file_hosts:
            if re.search(host, text):
                score += 35
                threats.append(f"Suspicious File Hosting: {host}")
                break
        
        # Context clues: file + download + link
        if ('file' in text and 'download' in text) or ('drive' in text and 'link' in text):
            if score > 0:  # Only boost if already has some risk
                score += 15
                threats.append("Suspicious File Download Pattern")
        
        # Any file sharing + unknown sender is very suspicious
        has_file_sharing = any(x in text for x in ['drive.google', 'dropbox', 'onedrive', 'mediafire'])
        if has_file_sharing and score > 15:  # Only if already suspicious
            score += 10
            threats.append("File Sharing from Unknown Sender")
        
        # CRITICAL: File sharing + install/free keywords = almost always trojan
        trojan_keywords = ['install', 'free', 'download', 'activate', 'enable', 'setup', 'server']
        has_trojan_keywords = any(kw in text for kw in trojan_keywords)
        if has_file_sharing and has_trojan_keywords:
            score += 35  # MASSIVE BOOST - Classic trojan pattern
            threats.append("TROJAN PATTERN: File Sharing + Install Request = HIGH RISK")
        
        return score, threats
    
    def _generate_explanation(self, threat_level: str, threats: List[str], 
                             risk_score: int, email_data: Dict) -> str:
        """Generate AI explanation for the threat"""
        
        from_addr = email_data.get('from', 'Unknown')
        subject = email_data.get('subject', '(No Subject)')
        
        if threat_level == 'danger':
            return (
                f"🚨 CRITICAL THREAT DETECTED\n\n"
                f"This email from {from_addr} with subject '{subject}' has been "
                f"classified as DANGEROUS (Risk: {risk_score}%).\n\n"
                f"Detected Issues:\n" + 
                "\n".join(f"• {t}" for t in threats[:3]) +
                f"\n\nThis email appears designed to trick you into revealing information "
                f"or downloading malware. DO NOT click links or download attachments."
            )
        
        elif threat_level == 'warning':
            return (
                f"⚠️ WARNING - SUSPICIOUS EMAIL\n\n"
                f"This email from {from_addr} has suspicious characteristics (Risk: {risk_score}%).\n\n"
                f"Concerns:\n" +
                "\n".join(f"• {t}" for t in threats[:2]) +
                f"\n\nReview carefully before interacting with this email. "
                f"Verify requests independently if needed."
            )
        
        else:
            return (
                f"✅ EMAIL APPEARS SAFE\n\n"
                f"This email from {from_addr} with subject '{subject}' "
                f"appears legitimate (Risk: {risk_score}%).\n\n"
                f"You can open this email with confidence."
            )
    
    def _generate_recommendations(self, threats: List[str], threat_level: str, 
                                 email_data: Dict) -> List[str]:
        """Generate recommendations for user"""
        
        recommendations = []
        
        if threat_level == 'danger':
            recommendations = [
                "🚫 DO NOT click any links in this email",
                "🚫 DO NOT download or open attachments",
                "🚫 DO NOT reply with any information",
                "🗑️ Delete this email immediately",
                "⚠️ Report to your IT department",
                "🔐 If you clicked a link, change your password immediately"
            ]
        
        elif threat_level == 'warning':
            recommendations = [
                "⚠️ Review the sender email address carefully",
                "🔍 Verify any requests by contacting sender directly",
                "⚠️ Do NOT open attachments unless expected",
                "🔐 Never share passwords or sensitive info via email",
                "📧 Consider flagging as spam if unsure"
            ]
        
        else:
            recommendations = [
                "✅ This email appears safe to open",
                "🔒 Still review links before clicking",
                "📎 Be cautious with unexpected attachments"
            ]
        
        # Add specific recommendations based on threats
        if "Attachment" in str(threats):
            if "DO NOT download" not in recommendations:
                recommendations.append("📎 Do not download attachments from unknown senders")
        
        if "Sender Spoof" in str(threats):
            recommendations.insert(0, "🚨 Email sender appears to be forged/spoofed")
        
        return recommendations[:5]  # Return top 5 recommendations
