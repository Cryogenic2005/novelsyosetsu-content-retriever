import csv
import os
import requests
from enum import Enum

class NovelStorageError(Exception):
    """Base exception class for novel storage errors."""
    pass
class NovelNotFoundError(NovelStorageError):
    """Exception raised when a novel is not found in the catalog."""
    pass
class NovelExistsError(NovelStorageError): 
    """Exception raised when trying to add a novel that already exists in the catalog."""
    pass
class NovelLinkError(NovelStorageError):
    """Exception raised when the provided novel link is invalid or inaccessible."""
    pass
class NovelNoContentError(NovelStorageError):
    """Exception raised when a requested novel content is not found."""
    pass
class NovelContentRetrievalError(NovelStorageError):
    """Exception raised when there is an error retrieving novel content."""
    pass

class NovelContentType(Enum):
    """Enum for different types of novel content."""
    RAW_HTML = 'raw_html'
    RAW_CONTENT = 'raw_content'
    TRANSLATION = 'translation'
    
    def __str__(self):
        return self.value.replace('_', ' ').title()

class NovelStorageHandler:
    """Handles storage operations for novel translations."""
    
    CATALOG_FILENAME = 'novels.csv'

    def __init__(self, storage_path: str):
        self._storage_path = storage_path
        self._catalog_path = self.get_catalog_path()
        self._catalog = self._retrieve_novel_catalog_data()
        
    def get_catalog_path(self) -> str:
        """Get the path to the novel catalog file."""
        
        return os.path.join(self._storage_path, self.CATALOG_FILENAME)
        
    def get_novel_contents_dir(self,
                               novel_name: str,
                               content_type: NovelContentType = None) -> str:
        """Get directory path for a given novel name and content type.
        
        Args:
            novel_name (str): The name of the novel to retrieve the path for.
            content_type (NovelContentType, optional): The type of content to retrieve the path for.
                If None, returns the base directory for the novel.
                
        Raises:
            NovelNotFoundError: If the novel is not found in the catalog.
            
        Returns:
            str: The path to the novel's storage directory or specific content type directory.
        """
        
        if novel_name not in self._catalog:
            raise NovelNotFoundError(f"Novel '{novel_name}' not found in the catalog.")
        
        novel_dir = os.path.join(self._storage_path, novel_name)
        novel_dir = os.path.abspath(novel_dir)
        
        return novel_dir \
            if content_type is None \
            else os.path.join(novel_dir, content_type.value)
                
    def get_all_novel_names(self) -> list[str]:
        """Get all novel names from the catalog.
        
        Returns:
            list[str]: A list of all novel names.
        """
        return list(self._catalog.keys())

    def get_novel_link(self, novel_name: str) -> str:
        """Get the link for a given novel name.

        Args:
            novel_name (str): The name of the novel to retrieve the link for.

        Raises:
            NovelNotFoundError: If the novel is not found in the catalog.

        Returns:
            str: The link to the novel.
        """

        if novel_name not in self._catalog:
            raise NovelNotFoundError(f"Novel '{novel_name}' not found in the catalog.")
        
        return self._catalog[novel_name]

    def get_novel_content(self,
                          novel_name: str,
                          filename: str,
                          content_type: NovelContentType) -> str:
        """Get the content of a specific file for a given novel and content type.
        
        Args:
            novel_name (str): The name of the novel.
            filename (str): The name of the file to retrieve.
            content_type (NovelContentType): The type of content to retrieve.
        Raises:
            NovelNotFoundError: If the novel is not found in the catalog.
            NovelNoContentError: If the requested content file does not exist.
            NovelContentRetrievalError: If there is an error reading the content file.
        Returns:
            str: The content of the file.
        """
        
        save_dir = self.get_novel_contents_dir(novel_name, content_type)
        filepath = os.path.join(save_dir, filename)
        
        if not os.path.exists(filepath):
            raise NovelNoContentError(f"Content file '{filename}' for novel '{novel_name}' not found in {content_type}.")
        
        try:
            with open(filepath, mode='r', encoding='utf-8') as file:
                return file.read()
        except IOError as e:
            raise NovelContentRetrievalError(f"Error reading content file '{filepath}': {e}")

    def add_novel(self, novel_name: str, novel_link: str) -> None:
        """Add a new novel to novels.csv."""
        
        # Check if the novel already exists in the catalog
        if novel_name in self._catalog:
            raise NovelExistsError(f"Novel '{novel_name}' already exists in the catalog.")
        
        # Validate the novel link points to a valid URL
        try:
            response = requests.get(novel_link)
            if response.status_code != 200:
                raise ValueError(f"Invalid URL: {novel_link}. Status code: {response.status_code}")
        except requests.RequestException as e:
            raise NovelLinkError(f"Error accessing novel link: {e}")
        
        # Add the new novel to the catalog
        self._catalog[novel_name] = novel_link
        
        # Ensure the storage directories for the novel exists
        novel_dir = os.path.join(self._storage_path, novel_name)
        os.makedirs(novel_dir, exist_ok=True)
        for content_type in NovelContentType:
            os.makedirs(os.path.join(novel_dir, content_type.value), exist_ok=True)
        
        # Write the updated catalog back to novels.csv
        with open(self._catalog_path, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for name, link in self._catalog.items():
                writer.writerow([name, link])
                
    def save_contents(self,
                      novel_name: str,
                      content_type: NovelContentType,
                      content_filename: str,
                      content: str) -> bool:
        """Save content to the specified novel's storage directory.
        
        Args:
            novel_name (str): The name of the novel.
            content_type (NovelContentType): The type of content to save.
            content_filename (str): The filename to save the content as.
            content (str): The content to save.
        
        Returns:
            bool: True if the content was saved successfully, False otherwise.
            
        Raises:
            NovelNotFoundError: If the novel is not found in the catalog.    
        """
        
        save_dir = self.get_novel_contents_dir(novel_name, content_type)
        
        if not os.path.exists(save_dir):
            raise Exception(f"Novel directory '{save_dir}' does not exist.")
        
        file_path = os.path.join(save_dir, content_filename)
        
        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                file.write(content)
            return True
        except IOError as e:
            print(f"Error saving content to {file_path}: {e}")
            return False
        
    def _retrieve_novel_catalog_data(self) -> dict[str, str]:
        catalog = {}
        
        try:
            with open(self._catalog_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    if len(row) < 2:
                        continue
                    
                    name = row[0].strip().strip('"')
                    link = row[1].strip().strip('"')
                    
                    if name and link:
                        catalog[name] = link
        except FileNotFoundError:
            print(f"Catalog file {self._catalog_path} not found. Starting with an empty catalog.")
            
            with open(self._catalog_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Link', 'Bookmark'])  # Write header row
        except Exception as e:
            raise NovelStorageError(f"Error reading catalog file {self._catalog_path}: {e}")
        
        return catalog