"""
Rich Text Formatter for CLI Output
Converts markdown-style formatting to ANSI-colored terminal output
"""
import re
from typing import List, Tuple


class TextFormatter:
    """
    Formats text with markdown-style syntax for beautiful CLI output
    Supports:
    - **bold** or __bold__
    - *italic* or _italic_
    - `code`
    - # Headers
    - Lists (-, *, +)
    - Code blocks (```)
    - Links [text](url)
    """
    
    # ANSI Color Codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background Colors
    BG_BLACK = '\033[40m'
    BG_CYAN = '\033[46m'
    BG_BLUE = '\033[44m'
    
    def __init__(self):
        self.in_code_block = False
        self.code_block_lang = ""
    
    def format(self, text: str) -> str:
        """
        Main formatting function - converts markdown to formatted CLI output
        """
        if not text:
            return text
        
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            formatted_line = self._format_line(line)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    def _format_line(self, line: str) -> str:
        """Format a single line with all markdown elements"""
        
        # Handle code blocks
        if line.strip().startswith('```'):
            self.in_code_block = not self.in_code_block
            if self.in_code_block:
                self.code_block_lang = line.strip()[3:].strip()
                return f"{self.BRIGHT_BLACK}{'─' * 60}{self.RESET}"
            else:
                self.code_block_lang = ""
                return f"{self.BRIGHT_BLACK}{'─' * 60}{self.RESET}"
        
        if self.in_code_block:
            return self._format_code_line(line)
        
        # Handle headers
        if line.strip().startswith('#'):
            return self._format_header(line)
        
        # Handle lists
        if re.match(r'^\s*[\-\*\+]\s', line):
            return self._format_list_item(line)
        
        # Handle numbered lists
        if re.match(r'^\s*\d+\.\s', line):
            return self._format_numbered_list(line)
        
        # Handle horizontal rules
        if re.match(r'^\s*[\-\*_]{3,}\s*$', line):
            return f"{self.BRIGHT_BLACK}{'─' * 60}{self.RESET}"
        
        # Apply inline formatting
        line = self._format_inline(line)
        
        return line
    
    def _format_header(self, line: str) -> str:
        """Format markdown headers"""
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2)
            
            if level == 1:
                # H1: Bold, bright cyan, with underline
                formatted_text = self._format_inline(text)
                return f"\n{self.BOLD}{self.BRIGHT_CYAN}{formatted_text}{self.RESET}\n{self.BRIGHT_CYAN}{'═' * 60}{self.RESET}"
            elif level == 2:
                # H2: Bold, cyan
                formatted_text = self._format_inline(text)
                return f"\n{self.BOLD}{self.CYAN}{formatted_text}{self.RESET}\n{self.CYAN}{'─' * 40}{self.RESET}"
            elif level == 3:
                # H3: Bold, blue
                formatted_text = self._format_inline(text)
                return f"\n{self.BOLD}{self.BLUE}{formatted_text}{self.RESET}"
            else:
                # H4+: Bold only
                formatted_text = self._format_inline(text)
                return f"{self.BOLD}{formatted_text}{self.RESET}"
        
        return line
    
    def _format_list_item(self, line: str) -> str:
        """Format unordered list items"""
        match = re.match(r'^(\s*)([\-\*\+])\s+(.+)$', line)
        if match:
            indent = match.group(1)
            text = match.group(3)
            formatted_text = self._format_inline(text)
            return f"{indent}{self.BRIGHT_YELLOW}•{self.RESET} {formatted_text}"
        return line
    
    def _format_numbered_list(self, line: str) -> str:
        """Format ordered list items"""
        match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
        if match:
            indent = match.group(1)
            number = match.group(2)
            text = match.group(3)
            formatted_text = self._format_inline(text)
            return f"{indent}{self.BRIGHT_CYAN}{number}.{self.RESET} {formatted_text}"
        return line
    
    def _format_code_line(self, line: str) -> str:
        """Format lines inside code blocks"""
        return f"{self.BG_BLACK}{self.BRIGHT_GREEN}{line}{self.RESET}"
    
    def _format_inline(self, text: str) -> str:
        """Apply inline formatting (bold, italic, code, links)"""
        
        # Escape already formatted text temporarily
        # This prevents double-formatting
        
        # Code blocks first (highest priority)
        text = re.sub(
            r'`([^`]+)`',
            lambda m: f"{self.BG_CYAN}{self.BLACK}{m.group(1)}{self.RESET}",
            text
        )
        
        # Bold (**text** or __text__)
        text = re.sub(
            r'\*\*(.+?)\*\*',
            lambda m: f"{self.BOLD}{self.BRIGHT_WHITE}{m.group(1)}{self.RESET}",
            text
        )
        text = re.sub(
            r'__(.+?)__',
            lambda m: f"{self.BOLD}{self.BRIGHT_WHITE}{m.group(1)}{self.RESET}",
            text
        )
        
        # Italic (*text* or _text_) - be careful not to match already processed bold
        text = re.sub(
            r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)',
            lambda m: f"{self.ITALIC}{self.YELLOW}{m.group(1)}{self.RESET}",
            text
        )
        text = re.sub(
            r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)',
            lambda m: f"{self.ITALIC}{self.YELLOW}{m.group(1)}{self.RESET}",
            text
        )
        
        # Links [text](url)
        text = re.sub(
            r'\[([^\]]+)\]\(([^\)]+)\)',
            lambda m: f"{self.UNDERLINE}{self.BRIGHT_BLUE}{m.group(1)}{self.RESET} {self.DIM}({m.group(2)}){self.RESET}",
            text
        )
        
        # Strikethrough ~~text~~
        text = re.sub(
            r'~~(.+?)~~',
            lambda m: f"{self.DIM}{m.group(1)}{self.RESET}",
            text
        )
        
        return text
    
    def format_json_response(self, response: str) -> str:
        """
        Special formatting for JSON/structured responses from API
        Highlights important information
        """
        return self.format(response)
    
    def format_error(self, error_text: str) -> str:
        """Format error messages with red color"""
        return f"{self.BOLD}{self.RED}❌ Error: {error_text}{self.RESET}"
    
    def format_success(self, success_text: str) -> str:
        """Format success messages with green color"""
        return f"{self.BOLD}{self.GREEN}✅ {success_text}{self.RESET}"
    
    def format_info(self, info_text: str) -> str:
        """Format info messages with blue color"""
        return f"{self.BRIGHT_BLUE}ℹ️  {info_text}{self.RESET}"
    
    def format_warning(self, warning_text: str) -> str:
        """Format warning messages with yellow color"""
        return f"{self.BOLD}{self.YELLOW}⚠️  {warning_text}{self.RESET}"


# Global formatter instance
_formatter = None

def get_formatter() -> TextFormatter:
    """Get or create the global formatter instance"""
    global _formatter
    if _formatter is None:
        _formatter = TextFormatter()
    return _formatter


def format_text(text: str) -> str:
    """Convenience function to format text"""
    return get_formatter().format(text)


def format_error(text: str) -> str:
    """Convenience function to format errors"""
    return get_formatter().format_error(text)


def format_success(text: str) -> str:
    """Convenience function to format success messages"""
    return get_formatter().format_success(text)


def format_info(text: str) -> str:
    """Convenience function to format info messages"""
    return get_formatter().format_info(text)


def format_warning(text: str) -> str:
    """Convenience function to format warnings"""
    return get_formatter().format_warning(text)


# Demo function
if __name__ == "__main__":
    formatter = TextFormatter()
    
    demo_text = """
# Main Header

This is a paragraph with **bold text**, *italic text*, and `inline code`.

## Subheader

Here's a list:
- First item with **bold**
- Second item with *italic*
- Third item with `code`

### Smaller header

1. Numbered item one
2. Numbered item two
3. Numbered item three

Here's a link: [Google](https://google.com)

```python
def example():
    print("This is code")
```

**Important**: This is very important!

---

End of demo.
"""
    
    print(formatter.format(demo_text))
