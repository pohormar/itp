import re

def parse_tags(text: str, tag_name: str) -> list[str]:
    """Finds all occurrences of a given tag and returns their content."""
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    return re.findall(pattern, text, re.DOTALL)

def remove_tags(text: str) -> str:
    """Removes all XML-like tags from the text."""
    return re.sub(r'<.*?>', '', text) 