import os
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger


def create_file(file_path: str, content: str) -> Dict[str, Any]:
    """Create a new file or overwrite existing file with given content."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info(f"Successfully created file: {path.resolve()}")
        return {"status": "success", "file_path": str(path.resolve()), "bytes": len(content)}
    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return {"status": "error", "error": str(e)}


def read_file_content(file_path: str) -> Dict[str, Any]:
    """Read and return content of a text file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {"status": "error", "error": f"File does not exist: {file_path}"}
        content = path.read_text(encoding="utf-8")
        return {"status": "success", "file_path": str(path.resolve()), "content": content}
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return {"status": "error", "error": str(e)}


def list_directory(dir_path: str = ".") -> Dict[str, Any]:
    """List all files and folders in a target directory."""
    try:
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            return {"status": "error", "error": f"Directory does not exist: {dir_path}"}
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size_bytes": item.stat().st_size if item.is_file() else None
            })
        return {"status": "success", "directory": str(path.resolve()), "items": items}
    except Exception as e:
        logger.error(f"Error listing directory {dir_path}: {e}")
        return {"status": "error", "error": str(e)}
