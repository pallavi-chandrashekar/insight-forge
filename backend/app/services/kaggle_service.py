"""
Kaggle Service - Download datasets directly from Kaggle using their API
"""

import os
import re
import zipfile
import tempfile
import shutil
from typing import Optional, Tuple
import pandas as pd


class KaggleService:
    """Service to interact with Kaggle API for downloading datasets"""

    @staticmethod
    def extract_dataset_slug(url: str) -> Optional[str]:
        """
        Extract dataset slug (owner/dataset-name) from Kaggle URL.

        Examples:
            https://www.kaggle.com/datasets/USERNAME/DATASET-NAME -> USERNAME/DATASET-NAME
            https://kaggle.com/datasets/user/my-dataset -> user/my-dataset
        """
        # Pattern to match Kaggle dataset URLs
        patterns = [
            r'kaggle\.com/datasets/([^/]+/[^/\?]+)',
            r'kaggle\.com/([^/]+/[^/\?]+)/data',
        ]

        for pattern in patterns:
            match = re.search(pattern, url.lower())
            if match:
                slug = match.group(1)
                # Clean up any trailing slashes or query params
                slug = slug.split('?')[0].rstrip('/')
                return slug

        return None

    @staticmethod
    async def download_dataset(
        url: str,
        kaggle_username: str,
        kaggle_key: str
    ) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str]]:
        """
        Download a dataset from Kaggle and return as DataFrame.

        Args:
            url: Kaggle dataset URL
            kaggle_username: Kaggle username
            kaggle_key: Kaggle API key

        Returns:
            Tuple of (DataFrame, filename, error_message)
        """
        # Extract dataset slug from URL
        slug = KaggleService.extract_dataset_slug(url)
        if not slug:
            return None, None, "Could not extract dataset identifier from URL"

        # Set Kaggle credentials as environment variables
        os.environ['KAGGLE_USERNAME'] = kaggle_username
        os.environ['KAGGLE_KEY'] = kaggle_key

        try:
            # Import kaggle after setting credentials
            from kaggle.api.kaggle_api_extended import KaggleApi

            api = KaggleApi()
            api.authenticate()

            # Create temp directory for download
            temp_dir = tempfile.mkdtemp()

            try:
                # Download the dataset
                owner, dataset_name = slug.split('/')
                api.dataset_download_files(slug, path=temp_dir, unzip=True)

                # Find CSV/data files in the downloaded content
                data_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith(('.csv', '.json', '.xlsx', '.xls', '.parquet')):
                            data_files.append(os.path.join(root, file))

                if not data_files:
                    return None, None, "No data files found in the downloaded dataset"

                # Use the largest file (usually the main dataset)
                main_file = max(data_files, key=os.path.getsize)
                filename = os.path.basename(main_file)

                # Read into DataFrame
                if main_file.endswith('.csv'):
                    df = pd.read_csv(main_file)
                elif main_file.endswith('.json'):
                    df = pd.read_json(main_file)
                elif main_file.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(main_file)
                elif main_file.endswith('.parquet'):
                    df = pd.read_parquet(main_file)
                else:
                    return None, None, f"Unsupported file type: {filename}"

                return df, filename, None

            finally:
                # Cleanup temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError:
            return None, None, "Kaggle package not installed. Run: pip install kaggle"
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Could not authenticate" in error_msg:
                return None, None, "Invalid Kaggle credentials. Please check your username and API key."
            elif "403" in error_msg:
                return None, None, "Access denied. You may need to accept the dataset's terms on Kaggle first."
            elif "404" in error_msg:
                return None, None, "Dataset not found. Please check the URL."
            else:
                return None, None, f"Failed to download from Kaggle: {error_msg}"

    @staticmethod
    async def get_dataset_metadata(
        url: str,
        kaggle_username: str,
        kaggle_key: str
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Get dataset metadata by extracting JSON-LD structured data from Kaggle page.
        Kaggle embeds schema.org Dataset metadata in a script tag.

        Args:
            url: Kaggle dataset URL
            kaggle_username: Kaggle username
            kaggle_key: Kaggle API key

        Returns:
            Tuple of (metadata_dict, error_message)
        """
        slug = KaggleService.extract_dataset_slug(url)
        if not slug:
            return None, "Could not extract dataset identifier from URL"

        owner, dataset_name = slug.split('/')

        try:
            import aiohttp
            from bs4 import BeautifulSoup
            import json

            # Fetch the Kaggle page
            kaggle_url = f"https://www.kaggle.com/datasets/{slug}"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(kaggle_url) as response:
                    if response.status != 200:
                        return None, f"Failed to fetch Kaggle page: {response.status}"

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Look for JSON-LD structured data (schema.org format)
                    # Kaggle embeds dataset info in: <script type="application/ld+json">
                    json_ld_script = soup.find('script', type='application/ld+json')

                    description = None
                    title = dataset_name.replace('-', ' ').title()
                    tags = []
                    license_name = None

                    if json_ld_script and json_ld_script.string:
                        try:
                            schema_data = json.loads(json_ld_script.string)

                            # Extract from schema.org Dataset format
                            title = schema_data.get('name', title)
                            description = schema_data.get('description', '')

                            # Clean up HTML entities in description
                            if description:
                                description = description.replace('&amp;', '&')
                                description = description.replace('&lt;', '<')
                                description = description.replace('&gt;', '>')
                                description = description.replace('&quot;', '"')

                            # Extract keywords/tags
                            keywords = schema_data.get('keywords', [])
                            if keywords:
                                for kw in keywords:
                                    # Keywords are like "subject, science and technology, internet"
                                    # Extract the last part which is the actual tag
                                    parts = kw.split(',')
                                    tag = parts[-1].strip() if parts else kw
                                    if tag and tag not in tags:
                                        tags.append(tag)

                            # Extract license
                            license_info = schema_data.get('license', {})
                            if isinstance(license_info, dict):
                                license_name = license_info.get('name')
                            elif isinstance(license_info, str):
                                license_name = license_info

                        except json.JSONDecodeError:
                            pass

                    # Fallback: try meta description if no JSON-LD
                    if not description:
                        meta_desc = soup.find('meta', {'name': 'description'})
                        if meta_desc:
                            description = meta_desc.get('content', '')

                    metadata = {
                        'title': title,
                        'description': description,
                        'creator': owner,
                        'url': kaggle_url,
                        'license': license_name,
                        'tags': tags,
                    }

                    return metadata, None

        except Exception as e:
            return None, f"Failed to get metadata: {str(e)}"

    @staticmethod
    def format_metadata_as_context(metadata: dict, column_info: list = None) -> str:
        """
        Format Kaggle metadata as a markdown context document.

        Args:
            metadata: Dataset metadata from Kaggle API/scraping
            column_info: Optional list of column information from the DataFrame

        Returns:
            Markdown formatted context string
        """
        lines = []

        # Title
        title = metadata.get('title', 'Kaggle Dataset')
        lines.append(f"# {title}\n")

        # Source info
        lines.append(f"**Source:** {metadata.get('url', 'Kaggle')}")
        lines.append("**Platform:** Kaggle")
        if metadata.get('creator'):
            lines.append(f"**Creator:** {metadata['creator']}")
        if metadata.get('license'):
            lines.append(f"**License:** {metadata['license']}")
        if metadata.get('usability'):
            lines.append(f"**Usability Score:** {metadata['usability']}/10")
        lines.append("")
        lines.append("---\n")

        # About Dataset / Description (the key content from Kaggle page)
        description = metadata.get('description')
        if description:
            # Remove Disclaimer section if present
            import re
            # Remove everything after "**Disclaimer**" or "Disclaimer:"
            description = re.split(r'\*\*Disclaimer\*\*|Disclaimer:', description, flags=re.IGNORECASE)[0]
            # Clean up any trailing markdown formatting
            description = description.strip()
            description = re.sub(r'\*+\s*$', '', description).strip()

            if description:
                lines.append("## About Dataset\n")
                lines.append(description)
                lines.append("")

        # Tags/Keywords
        tags = metadata.get('tags', [])
        if tags:
            lines.append("## Tags\n")
            lines.append(', '.join(str(t) for t in tags))
            lines.append("")

        # Column information from DataFrame (as supplementary info)
        if column_info:
            lines.append("## Column Schema\n")
            lines.append("| Column | Type | Sample Values |")
            lines.append("|--------|------|---------------|")
            for col in column_info:
                name = col.get('name', '')
                dtype = col.get('dtype', '')
                samples = col.get('sample_values', [])[:3]
                sample_str = ', '.join(str(s)[:30] for s in samples)
                lines.append(f"| {name} | {dtype} | {sample_str} |")
            lines.append("")

        return '\n'.join(lines)

    @staticmethod
    def validate_credentials(username: str, key: str) -> Tuple[bool, str]:
        """
        Validate Kaggle credentials by attempting to authenticate.

        Returns:
            Tuple of (is_valid, message)
        """
        if not username or not key:
            return False, "Username and API key are required"

        os.environ['KAGGLE_USERNAME'] = username
        os.environ['KAGGLE_KEY'] = key

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            api = KaggleApi()
            api.authenticate()
            # Try a simple API call to verify
            api.competitions_list(page=1, page_size=1)
            return True, "Credentials valid"
        except ImportError:
            return False, "Kaggle package not installed"
        except Exception as e:
            return False, f"Invalid credentials: {str(e)}"
