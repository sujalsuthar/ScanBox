"""Slack integration for real-time threat notifications"""

import requests
import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SlackIntegration:
    """Integrate MailShield Pro with Slack for real-time alerts"""
    
    @staticmethod
    def send_threat_alert(webhook_url: str, threat_data: dict) -> bool:
        """Send a threat alert to Slack"""
        try:
            if not webhook_url:
                logger.warning("No Slack webhook URL provided")
                return False
            
            # Determine threat color
            risk_level = threat_data.get('risk_level', 'UNKNOWN')
            if risk_level == 'DANGER':
                color = '#ef4444'  # Red
                emoji = '🔴'
            elif risk_level == 'SUSPICIOUS':
                color = '#f59e0b'  # Orange
                emoji = '🟠'
            else:
                color = '#10b981'  # Green
                emoji = '🟢'
            
            # Build Slack message
            payload = {
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': f'{emoji} MailShield Pro - Threat Detected'
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f"*Risk Level*\n{risk_level}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Risk Score*\n{threat_data.get('risk_score', 'N/A')}/10"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*From*\n{threat_data.get('from', 'Unknown')}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Time*\n{threat_data.get('date', 'Unknown')}"
                            }
                        ]
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*Subject*\n{threat_data.get('subject', '(No Subject)')}"
                        }
                    },
                    {
                        'type': 'divider'
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*Threat Indicators*\n• URLs: {len(threat_data.get('urls', []))} found\n• Attachments: {len(threat_data.get('attachments', []))} found"
                        }
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"Email scanned at {threat_data.get('scanned_at', 'Unknown')}"
                            }
                        ]
                    }
                ],
                'attachments': [
                    {
                        'color': color,
                        'title': 'View in MailShield Pro',
                        'title_link': threat_data.get('scan_link', 'http://localhost:5000')
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Slack alert sent successfully")
                return True
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")
            return False
    
    @staticmethod
    def send_scan_summary(webhook_url: str, summary_data: dict) -> bool:
        """Send a scan summary to Slack"""
        try:
            if not webhook_url:
                logger.warning("No Slack webhook URL provided")
                return False
            
            payload = {
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': '📊 MailShield Pro - Scan Summary'
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f"*Total Emails*\n{summary_data.get('total_emails', 0)}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Safe*\n🟢 {summary_data.get('safe', 0)}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Suspicious*\n🟠 {summary_data.get('suspicious', 0)}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Dangerous*\n🔴 {summary_data.get('danger', 0)}"
                            }
                        ]
                    },
                    {
                        'type': 'context',
                        'elements': [
                            {
                                'type': 'mrkdwn',
                                'text': f"Scan completed at {summary_data.get('completed_at', 'Unknown')}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Slack summary sent successfully")
                return True
            else:
                logger.error(f"Failed to send Slack summary: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending Slack summary: {e}")
            return False
    
    @staticmethod
    def send_daily_report(webhook_url: str, report_data: dict) -> bool:
        """Send daily security report to Slack"""
        try:
            if not webhook_url:
                logger.warning("No Slack webhook URL provided")
                return False
            
            threat_trend = report_data.get('trend', 'stable')
            trend_emoji = {
                'increasing': '📈',
                'decreasing': '📉',
                'stable': '➡️'
            }.get(trend_emoji, '❓')
            
            payload = {
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': f'{trend_emoji} MailShield Pro - Daily Security Report'
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {
                                'type': 'mrkdwn',
                                'text': f"*Scans Today*\n{report_data.get('scans_today', 0)}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Threats Detected*\n{report_data.get('threats_today', 0)}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Overall Risk*\n{report_data.get('overall_risk', 'Low')}"
                            },
                            {
                                'type': 'mrkdwn',
                                'text': f"*Trend*\n{report_data.get('trend', 'Stable')}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Daily report sent to Slack")
                return True
            else:
                logger.error(f"Failed to send daily report: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
            return False
