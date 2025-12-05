import base64
from typing import Tuple

class FileHandler:
    
    @staticmethod
    def encode_file_to_base64(file_path: str) -> str:
        """Encode a file to base64 string"""
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    
    @staticmethod
    def decode_base64_to_file(base64_string: str, output_path: str) -> None:
        """Decode base64 string and save to file"""
        file_data = base64.b64decode(base64_string)
        with open(output_path, 'wb') as file:
            file.write(file_data)
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Extract file extension from filename"""
        return filename.split('.')[-1] if '.' in filename else ''
    
    @staticmethod
    def validate_file_size(base64_string: str, max_size_mb: int = 10) -> Tuple[bool, str]:
        """Validate base64 encoded file size"""
        try:
            size_bytes = len(base64_string) * 3 / 4
            size_mb = size_bytes / (1024 * 1024)
            
            if size_mb > max_size_mb:
                return False, f"File size exceeds {max_size_mb}MB limit"
            return True, "Valid"
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
