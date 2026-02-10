"""
Smart URL Detection Service
Intelligently detects if a URL points to data or documentation
and routes users to the appropriate feature.
"""

import re
from typing import Tuple, Optional
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup


class URLType:
    """Types of URLs"""
    DATA_FILE = "data_file"  # Direct link to CSV, JSON, etc.
    DOCUMENTATION = "documentation"  # Guide, README, description
    DATASET_PAGE = "dataset_page"  # Kaggle, GitHub, etc. dataset page
    INVALID = "invalid"


class SmartURLDetector:
    """Intelligently detect URL type and extract information"""

    # Supported data file extensions
    DATA_EXTENSIONS = ['.csv', '.json', '.xlsx', '.xls', '.parquet', '.tsv']

    # Known documentation platforms
    DOC_PLATFORMS = {
        'docs.google.com': 'Google Docs',
        'notion.so': 'Notion',
        'github.com': 'GitHub',
        'raw.githubusercontent.com': 'GitHub',
        'gitlab.com': 'GitLab',
        'confluence': 'Confluence',
        'medium.com': 'Medium',
        'substack.com': 'Substack',
        'readthedocs': 'Read the Docs',
        'wikipedia.org': 'Wikipedia',
        'docs.python.org': 'Python Docs',
        'pandas.pydata.org': 'Pandas Docs',
        'scikit-learn.org': 'Scikit-learn Docs',
        'pytorch.org/docs': 'PyTorch Docs',
        'tensorflow.org': 'TensorFlow Docs',
        'docs.': 'Documentation Site',  # Generic docs subdomain
    }

    # Known dataset platforms
    DATASET_PLATFORMS = {
        'kaggle.com/datasets': 'Kaggle',
        'data.world': 'Data.world',
        'github.com': 'GitHub',
        'huggingface.co/datasets': 'Hugging Face',
        'zenodo.org': 'Zenodo',
        'figshare.com': 'Figshare',
    }

    @classmethod
    def detect_url_type(cls, url: str) -> Tuple[str, Optional[str], dict]:
        """
        Detect what type of URL this is.

        Returns:
            (url_type, platform, metadata)
        """
        url_lower = url.lower()
        parsed = urlparse(url)

        # Check for data file extension
        if any(url_lower.endswith(ext) for ext in cls.DATA_EXTENSIONS):
            return URLType.DATA_FILE, None, {
                "file_type": cls._get_file_extension(url),
                "can_import": True
            }

        # Check for documentation platforms
        for domain, platform in cls.DOC_PLATFORMS.items():
            if domain in url_lower:
                return URLType.DOCUMENTATION, platform, {
                    "platform": platform,
                    "can_import": False,
                    "suggestion": "Use this as context documentation"
                }

        # Check for dataset platforms
        for pattern, platform in cls.DATASET_PLATFORMS.items():
            if pattern in url_lower:
                return URLType.DATASET_PAGE, platform, {
                    "platform": platform,
                    "can_import": False,
                    "suggestion": "This is a dataset page. Look for 'Download' button to get direct data URL"
                }

        # Unknown - might be data or not
        return URLType.INVALID, None, {
            "can_import": False,
            "needs_inspection": True
        }

    @classmethod
    async def inspect_url_content(cls, url: str, max_size: int = 5000) -> dict:
        """
        Fetch and inspect URL content to determine if it's data or documentation.

        Args:
            url: URL to inspect
            max_size: Maximum bytes to fetch (default 5KB for inspection)

        Returns:
            Dictionary with inspection results
        """
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "type": URLType.INVALID
                        }

                    content_type = response.headers.get('Content-Type', '').lower()

                    # Check content type
                    if any(t in content_type for t in ['text/csv', 'application/json', 'application/vnd.ms-excel']):
                        return {
                            "success": True,
                            "type": URLType.DATA_FILE,
                            "content_type": content_type,
                            "message": "This URL points to a data file"
                        }

                    # Fetch small sample
                    sample = await response.content.read(max_size)

                    # Check if HTML (likely documentation)
                    if 'text/html' in content_type:
                        return cls._analyze_html_content(sample.decode('utf-8', errors='ignore'), url)

                    # Try to detect CSV structure
                    if cls._looks_like_csv(sample):
                        return {
                            "success": True,
                            "type": URLType.DATA_FILE,
                            "message": "Content looks like CSV data"
                        }

                    # Try to detect JSON structure
                    if cls._looks_like_json(sample):
                        return {
                            "success": True,
                            "type": URLType.DATA_FILE,
                            "message": "Content looks like JSON data"
                        }

                    # Probably documentation or unstructured text
                    return {
                        "success": True,
                        "type": URLType.DOCUMENTATION,
                        "message": "Content appears to be documentation or text"
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "type": URLType.INVALID
            }

    @classmethod
    def _analyze_html_content(cls, html: str, url: str) -> dict:
        """Analyze HTML to determine if it's a dataset page or documentation"""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text().lower()

        # Keywords indicating dataset page
        dataset_keywords = ['download', 'dataset', 'data file', 'csv', 'json', 'excel', 'download data']
        dataset_score = sum(1 for keyword in dataset_keywords if keyword in text)

        # Keywords indicating documentation
        doc_keywords = ['readme', 'documentation', 'guide', 'tutorial', 'about this dataset', 'overview']
        doc_score = sum(1 for keyword in doc_keywords if keyword in text)

        # Check for download links
        has_download_links = any(
            link.get('href', '').endswith(tuple(cls.DATA_EXTENSIONS))
            for link in soup.find_all('a')
        )

        if has_download_links:
            return {
                "success": True,
                "type": URLType.DATASET_PAGE,
                "message": "This is a dataset page with download links",
                "has_download_links": True,
                "suggestion": "Look for 'Download' button or link to get the actual data file"
            }

        if dataset_score > doc_score and dataset_score > 2:
            return {
                "success": True,
                "type": URLType.DATASET_PAGE,
                "message": "This appears to be a dataset description page",
                "suggestion": "This page describes a dataset. Use it as context documentation, and find the actual data download link."
            }

        return {
            "success": True,
            "type": URLType.DOCUMENTATION,
            "message": "This appears to be documentation or a guide",
            "suggestion": "Use this as context documentation for your dataset"
        }

    @classmethod
    def _looks_like_csv(cls, content: bytes) -> bool:
        """Check if content looks like CSV data"""
        try:
            text = content.decode('utf-8', errors='ignore')
            lines = text.strip().split('\n')[:5]

            if len(lines) < 2:
                return False

            # Check if has comma-separated values
            first_line_commas = lines[0].count(',')
            if first_line_commas < 1:
                return False

            # Check consistency across lines
            for line in lines[1:]:
                if abs(line.count(',') - first_line_commas) > 1:
                    return False

            return True
        except Exception:
            return False

    @classmethod
    def _looks_like_json(cls, content: bytes) -> bool:
        """Check if content looks like JSON data"""
        try:
            text = content.decode('utf-8', errors='ignore').strip()
            return (text.startswith('{') or text.startswith('[')) and \
                   ('"' in text or "'" in text)
        except Exception:
            return False

    @classmethod
    def _get_file_extension(cls, url: str) -> str:
        """Extract file extension from URL"""
        for ext in cls.DATA_EXTENSIONS:
            if url.lower().endswith(ext):
                return ext.lstrip('.')
        return 'unknown'

    @classmethod
    def generate_user_message(cls, url_type: str, platform: Optional[str], metadata: dict) -> dict:
        """
        Generate user-friendly message based on URL type.

        Returns:
            Dictionary with message and suggested action
        """
        if url_type == URLType.DATA_FILE:
            return {
                "type": "success",
                "title": "✅ Data File Detected",
                "message": f"This URL points to a {metadata.get('file_type', 'data')} file and can be imported.",
                "action": "import_data",
                "action_label": "Import Data"
            }

        elif url_type == URLType.DOCUMENTATION:
            return {
                "type": "info",
                "title": "📚 Documentation Detected",
                "message": f"This is a {platform} documentation page. Would you like to use this as context documentation for your dataset?",
                "action": "create_context",
                "action_label": "Create Context from Documentation",
                "details": "Context files help the AI understand your dataset better by providing business knowledge, column descriptions, and relationships."
            }

        elif url_type == URLType.DATASET_PAGE:
            return {
                "type": "info",
                "title": "📊 Dataset Page Detected",
                "message": f"This is a {platform} dataset page. You can import the data or use the description as context.",
                "action": "both",
                "action_label": "Choose Action",
                "details": "Import Data: Downloads the dataset. Create Context: Uses the page description to help understand the data."
            }

        else:
            return {
                "type": "error",
                "title": "❓ Unknown URL Type",
                "message": "Cannot determine if this is a data file or documentation.",
                "action": "inspect",
                "action_label": "Inspect URL",
                "details": "We'll fetch the URL and analyze its content to help you."
            }

    @classmethod
    async def extract_documentation_from_url(cls, url: str) -> Optional[str]:
        """
        Extract documentation content from URL and convert to markdown.
        Special handling for dataset platforms like Kaggle.

        Returns:
            Markdown content suitable for context creation
        """
        try:
            # Check if this is a Kaggle URL
            if 'kaggle.com' in url.lower():
                return await cls._extract_kaggle_context(url)

            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract title
                    title = soup.find('h1')
                    title_text = title.get_text().strip() if title else "Dataset Documentation"

                    # Remove script, style, nav, footer
                    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                        element.decompose()

                    # Extract main content
                    main_content = soup.find('main') or soup.find('article') or soup.find('body')

                    if not main_content:
                        return None

                    # Convert to simple markdown
                    markdown_lines = [f"# {title_text}\n"]
                    markdown_lines.append(f"Source: {url}\n")
                    markdown_lines.append("---\n")

                    # Extract headers and paragraphs
                    for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol']):
                        if element.name.startswith('h'):
                            level = int(element.name[1])
                            markdown_lines.append(f"\n{'#' * level} {element.get_text().strip()}\n")
                        elif element.name == 'p':
                            text = element.get_text().strip()
                            if text:
                                markdown_lines.append(f"{text}\n")
                        elif element.name in ['ul', 'ol']:
                            for li in element.find_all('li'):
                                markdown_lines.append(f"- {li.get_text().strip()}\n")

                    return '\n'.join(markdown_lines)

        except Exception as e:
            print(f"Error extracting documentation: {e}")
            return None

    @classmethod
    async def _extract_kaggle_context(cls, url: str) -> Optional[str]:
        """
        Extract rich context from Kaggle dataset page.
        Captures dataset description, column info, tags, and metadata.
        """
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Extract dataset title
                    title = soup.find('h1')
                    title_text = title.get_text().strip() if title else "Kaggle Dataset"

                    markdown_lines = [f"# {title_text}\n"]
                    markdown_lines.append(f"**Source:** {url}\n")
                    markdown_lines.append("**Platform:** Kaggle\n")
                    markdown_lines.append("---\n")

                    # Extract description/about section
                    description_section = soup.find('div', {'class': lambda x: x and 'description' in x.lower()}) or \
                                        soup.find('div', {'data-testid': 'description'}) or \
                                        soup.find('section', {'class': lambda x: x and 'about' in x.lower()})

                    if description_section:
                        markdown_lines.append("\n## Description\n")
                        for p in description_section.find_all(['p', 'li']):
                            text = p.get_text().strip()
                            if text:
                                markdown_lines.append(f"{text}\n")

                    # Try to extract column/field information
                    # Kaggle often shows columns in a table or list
                    column_section = soup.find('div', {'class': lambda x: x and 'column' in x.lower()}) or \
                                   soup.find('table', {'class': lambda x: x and ('data' in x.lower() or 'column' in x.lower())})

                    if column_section:
                        markdown_lines.append("\n## Columns\n")

                        # Check for table format
                        rows = column_section.find_all('tr')
                        if rows:
                            for row in rows[:20]:  # Limit to first 20 columns
                                cells = row.find_all(['td', 'th'])
                                if cells:
                                    cell_text = ' | '.join(cell.get_text().strip() for cell in cells)
                                    markdown_lines.append(f"- {cell_text}\n")
                        else:
                            # Check for list format
                            for item in column_section.find_all('li')[:20]:
                                markdown_lines.append(f"- {item.get_text().strip()}\n")

                    # Extract tags/keywords
                    tags = soup.find_all('a', {'class': lambda x: x and 'tag' in x.lower()})
                    if tags:
                        markdown_lines.append("\n## Tags\n")
                        tag_texts = [tag.get_text().strip() for tag in tags[:10]]
                        markdown_lines.append(', '.join(tag_texts) + "\n")

                    # Extract any usage/license info
                    license_section = soup.find(text=lambda x: x and 'license' in x.lower() if x else False)
                    if license_section:
                        parent = license_section.find_parent()
                        if parent:
                            markdown_lines.append("\n## License\n")
                            markdown_lines.append(f"{parent.get_text().strip()}\n")

                    # Extract file information if available
                    file_section = soup.find('div', {'class': lambda x: x and 'file' in x.lower()})
                    if file_section:
                        markdown_lines.append("\n## Files\n")
                        for item in file_section.find_all(['li', 'div'])[:10]:
                            text = item.get_text().strip()
                            if text and len(text) < 200:
                                markdown_lines.append(f"- {text}\n")

                    # Get any remaining important paragraphs from body
                    main_content = soup.find('main') or soup.find('article') or soup.find('body')
                    if main_content:
                        markdown_lines.append("\n## Additional Information\n")
                        for p in main_content.find_all('p')[:10]:
                            text = p.get_text().strip()
                            if text and len(text) > 50 and len(text) < 1000:
                                # Avoid duplicates
                                if text not in '\n'.join(markdown_lines):
                                    markdown_lines.append(f"{text}\n\n")

                    return '\n'.join(markdown_lines)

        except Exception as e:
            print(f"Error extracting Kaggle context: {e}")
            return None
