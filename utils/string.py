import hashlib
import re
import textwrap


class String:
    @staticmethod
    def truncate(text: str, *, length: int, suffix: str = "...") -> str:
        if length < 0:
            raise ValueError("length must be >= 0")
        if len(text) <= length:
            return text
        if length == 0:
            return ""
        if len(suffix) >= length:
            return suffix[:length]
        head = length - len(suffix)
        return text[:head] + suffix

    @staticmethod
    def truncate_words(text: str, *, count: int, suffix: str = "...") -> str:
        words = text.split()
        if len(words) <= count:
            return text
        truncated = " ".join(words[:count])
        return truncated + suffix

    @staticmethod
    def slug(text: str) -> str:
        result = text.lower()
        result = re.sub(r"[^\w\s-]", "", result)
        result = re.sub(r"[-\s]+", "-", result)
        return result.strip("-")

    @staticmethod
    def camel_case(text: str) -> str:
        words = text.split()
        if not words:
            return ""
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])

    @staticmethod
    def snake_case(text: str) -> str:
        s = text.strip()
        s = re.sub(r"[^\w]+", "_", s)
        s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", s)
        s = s.lower()
        s = re.sub(r"_+", "_", s).strip("_")
        return s

    @staticmethod
    def kebab_case(text: str) -> str:
        return String.slug(text)

    @staticmethod
    def title_case(text: str) -> str:
        return text.title()

    @staticmethod
    def reverse(text: str) -> str:
        return text[::-1]

    @staticmethod
    def remove_whitespace(text: str) -> str:
        return "".join(text.split())

    @staticmethod
    def pad_left(text: str, *, width: int, fillchar: str = " ") -> str:
        return text.rjust(width, fillchar)

    @staticmethod
    def pad_right(text: str, *, width: int, fillchar: str = " ") -> str:
        return text.ljust(width, fillchar)

    @staticmethod
    def pad_center(text: str, *, width: int, fillchar: str = " ") -> str:
        return text.center(width, fillchar)

    @staticmethod
    def remove_prefix(text: str, *, prefix: str) -> str:
        if text.startswith(prefix):
            return text[len(prefix) :]
        return text

    @staticmethod
    def remove_suffix(text: str, *, suffix: str) -> str:
        if not suffix or not text.endswith(suffix):
            return text
        return text[: -len(suffix)]

    @staticmethod
    def wrap(text: str, *, width: int) -> list[str]:
        return textwrap.wrap(text, width)

    @staticmethod
    def is_email(text: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, text))

    @staticmethod
    def is_url(text: str) -> bool:
        pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return bool(re.match(pattern, text))

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        return re.findall(pattern, text)

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        pattern = r"https?://[^\s/$.?#].[^\s]*"
        return re.findall(pattern, text)

    @staticmethod
    def hash(text: str, *, algorithm: str = "sha256") -> str:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode("utf-8"))
        return hash_obj.hexdigest()
