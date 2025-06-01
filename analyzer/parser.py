"""
Parser for .eml files to extract email content, links, and attachments
"""

import email
from email import policy
from typing import Dict, Any
import re

def extract_links(text: str) -> list:
    """
    Extract all URLs from text using regex
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def parse_email_file(file_path: str) -> Dict[str, Any]:
    """
    Parse an .eml file and extract relevant information.
    """
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            msg = email.message_from_file(f, policy=policy.default)

        email_data = {
            'subject': msg.get('subject', ''),
            'from': msg.get('from', ''),
            'to': msg.get('to', ''),
            'reply_to': msg.get('reply-to', ''),
            'content_type': msg.get('Content-Type', ''),
            'date': msg.get('date', ''),
            'headers': dict(msg.items()),
            'body': '',
            'attachments': [],
            'links': []
        }

        for part in msg.walk():
            if part.get_content_maintype() == 'text' and not email_data['body']:
                body_content = part.get_content()
                email_data['body'] = body_content
                email_data['links'].extend(extract_links(body_content))
            elif part.get_content_maintype() == 'multipart':
                continue
            elif part.get('Content-Disposition') is not None:
                email_data['attachments'].append({
                    'filename': part.get_filename(),
                    'content_type': part.get_content_type(),
                    'size': len(part.get_payload())
                })

        return email_data

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Email file not found: {file_path}") from e
    except Exception as e:
        raise ValueError(f"Error parsing email file: {str(e)}") from e

def main():
    """
    Main function to demonstrate email parsing
    """
    try:
        email_data = parse_email_file("sample.eml")
        print("Parsed Email Data:")
        print("-" * 50)
        print(f"From: {email_data['from']}")
        print(f"To: {email_data['to']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Date: {email_data['date']}")
        print(f"reply-to: {email_data['reply_to']}")
        print(f"Content-Type: {email_data['content_type']}")
        print("-" * 50)
        print("Body:")
        print(email_data['body'])
        print("-" * 50)
        if email_data['links']:
            print("Links found:")
            for link in email_data['links']:
                print(f"- {link}")
        print("-" * 50)
        if email_data['attachments']:
            print("Attachments:")
            for attachment in email_data['attachments']:
                print(f"- {attachment['filename']} ({attachment['content_type']})")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
