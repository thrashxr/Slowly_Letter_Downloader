import re
import unicodedata
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a string to be safe for filenames across different operating systems.
    - Removes illegal characters ( < > : " / \ | ? * )
    - Normalizes unicode
    - Strips leading/trailing whitespace
    - Limits length
    """
    filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
    
    filename = filename.strip().strip('.')
    
    if len(filename) > 100:
        filename = filename[:100]
    if len(filename) > 100:
        filename = filename[:100]
        
    if not filename:
        filename = "untitled"
        
    return filename

def ensure_unique_path(path: Path) -> Path:
    """
    If path exists, appends (1), (2), etc. to the filename to make it unique.
    """
    if not path.exists():
        return path
        
    parent = path.parent
    stem = path.stem
    suffix = path.suffix
    
    counter = 1
    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
