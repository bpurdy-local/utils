from utils import String


class TestStringTruncate:
    def test_truncate_basic(self):
        assert String.truncate("Hello, world!", length=10) == "Hello, ..."

    def test_truncate_exact_length(self):
        assert String.truncate("Hello", length=5) == "Hello"

    def test_truncate_shorter_than_length(self):
        assert String.truncate("Hi", length=10) == "Hi"

    def test_truncate_custom_suffix(self):
        assert String.truncate("Hello, world!", length=10, suffix="...") == "Hello, ..."
        assert String.truncate("Hello, world!", length=10, suffix="→") == "Hello, wo→"

    def test_truncate_empty_string(self):
        assert String.truncate("", length=10) == ""

    def test_truncate_words_basic(self):
        assert String.truncate_words("Hello world from Python", count=2) == "Hello world..."

    def test_truncate_words_exact_count(self):
        assert String.truncate_words("Hello world", count=2) == "Hello world"

    def test_truncate_words_more_words_than_count(self):
        assert String.truncate_words("Hello", count=5) == "Hello"

    def test_truncate_words_custom_suffix(self):
        assert String.truncate_words("Hello world from", count=2, suffix=" →") == "Hello world →"

    def test_truncate_words_empty_string(self):
        assert String.truncate_words("", count=5) == ""


class TestStringCaseConversions:
    def test_camel_case_basic(self):
        assert String.camel_case("hello world") == "helloWorld"
        assert String.camel_case("hello world python") == "helloWorldPython"

    def test_camel_case_single_word(self):
        assert String.camel_case("hello") == "hello"

    def test_camel_case_empty(self):
        assert String.camel_case("") == ""

    def test_snake_case_basic(self):
        assert String.snake_case("Hello World") == "hello_world"
        assert String.snake_case("HelloWorld") == "hello_world"

    def test_snake_case_with_numbers(self):
        assert String.snake_case("Hello World 123") == "hello_world_123"

    def test_snake_case_camel_case(self):
        assert String.snake_case("helloWorld") == "hello_world"
        assert String.snake_case("myVariableName") == "my_variable_name"

    def test_snake_case_pascal_case(self):
        assert String.snake_case("HelloWorld") == "hello_world"
        assert String.snake_case("MyClassName") == "my_class_name"

    def test_snake_case_consecutive_capitals(self):
        assert String.snake_case("HTTPServer") == "http_server"
        assert String.snake_case("XMLParser") == "xml_parser"
        assert String.snake_case("HTMLElement") == "html_element"
        assert String.snake_case("URLPath") == "url_path"

    def test_snake_case_kebab_case(self):
        assert String.snake_case("kebab-case-string") == "kebab_case_string"
        assert String.snake_case("my-variable-name") == "my_variable_name"

    def test_snake_case_mixed_delimiters(self):
        assert String.snake_case("hello-world from_Python") == "hello_world_from_python"
        assert String.snake_case("API-Key_Value") == "api_key_value"

    def test_snake_case_special_chars(self):
        assert String.snake_case("hello@world#test") == "hello_world_test"
        assert String.snake_case("user.name") == "user_name"

    def test_snake_case_already_snake_case(self):
        assert String.snake_case("already_snake_case") == "already_snake_case"
        assert String.snake_case("hello_world") == "hello_world"

    def test_snake_case_with_trailing_spaces(self):
        assert String.snake_case("  hello world  ") == "hello_world"

    def test_kebab_case_basic(self):
        assert String.kebab_case("Hello World") == "hello-world"

    def test_kebab_case_special_chars(self):
        assert String.kebab_case("Hello World!") == "hello-world"

    def test_title_case_basic(self):
        assert String.title_case("hello world") == "Hello World"

    def test_title_case_mixed(self):
        assert String.title_case("hELLo WoRLd") == "Hello World"

    def test_slug_basic(self):
        assert String.slug("Hello World!") == "hello-world"

    def test_slug_special_chars(self):
        assert String.slug("Hello@World#Python!") == "helloworldpython"

    def test_slug_multiple_spaces(self):
        assert String.slug("Hello    World") == "hello-world"


class TestStringManipulation:
    def test_reverse_basic(self):
        assert String.reverse("hello") == "olleh"

    def test_reverse_empty(self):
        assert String.reverse("") == ""

    def test_reverse_single_char(self):
        assert String.reverse("a") == "a"

    def test_remove_whitespace_basic(self):
        assert String.remove_whitespace("hello world") == "helloworld"

    def test_remove_whitespace_multiple_spaces(self):
        assert String.remove_whitespace("hello    world") == "helloworld"

    def test_remove_whitespace_tabs(self):
        assert String.remove_whitespace("hello\tworld") == "helloworld"

    def test_pad_left_basic(self):
        assert String.pad_left("hello", width=10) == "     hello"

    def test_pad_left_custom_char(self):
        assert String.pad_left("hello", width=10, fillchar="*") == "*****hello"

    def test_pad_left_already_longer(self):
        assert String.pad_left("hello world", width=5) == "hello world"

    def test_pad_right_basic(self):
        assert String.pad_right("hello", width=10) == "hello     "

    def test_pad_right_custom_char(self):
        assert String.pad_right("hello", width=10, fillchar="*") == "hello*****"

    def test_pad_center_basic(self):
        result = String.pad_center("hello", width=10)
        assert len(result) == 10
        assert result.strip() == "hello"

    def test_pad_center_custom_char(self):
        assert String.pad_center("hi", width=6, fillchar="*") == "**hi**"

    def test_remove_prefix_exists(self):
        assert String.remove_prefix("prefix_hello", prefix="prefix_") == "hello"

    def test_remove_prefix_not_exists(self):
        assert String.remove_prefix("hello", prefix="prefix_") == "hello"

    def test_remove_prefix_empty(self):
        assert String.remove_prefix("hello", prefix="") == "hello"

    def test_remove_suffix_exists(self):
        assert String.remove_suffix("hello_suffix", suffix="_suffix") == "hello"

    def test_remove_suffix_not_exists(self):
        assert String.remove_suffix("hello", suffix="_suffix") == "hello"

    def test_remove_suffix_empty(self):
        assert String.remove_suffix("hello", suffix="") == "hello"


class TestStringWrapping:
    def test_wrap_basic(self):
        result = String.wrap("This is a long line of text", width=10)
        assert isinstance(result, list)
        assert all(isinstance(line, str) for line in result)

    def test_wrap_short_text(self):
        result = String.wrap("Hi", width=10)
        assert len(result) == 1
        assert result[0] == "Hi"

    def test_wrap_empty(self):
        result = String.wrap("", width=10)
        assert result == []


class TestStringValidation:
    def test_is_email_valid(self):
        assert String.is_email("user@example.com") is True
        assert String.is_email("test.email+tag@example.co.uk") is True

    def test_is_email_invalid(self):
        assert String.is_email("invalid") is False
        assert String.is_email("user@") is False
        assert String.is_email("@example.com") is False
        assert String.is_email("user@example") is False

    def test_is_url_valid(self):
        assert String.is_url("https://example.com") is True
        assert String.is_url("http://example.com/path") is True

    def test_is_url_invalid(self):
        assert String.is_url("not-a-url") is False
        assert String.is_url("example.com") is False


class TestStringExtraction:
    def test_extract_emails_basic(self):
        emails = String.extract_emails("Contact info@example.com or support@test.com")
        assert len(emails) == 2
        assert all(isinstance(e, str) for e in emails)
        assert "info@example.com" in emails

    def test_extract_emails_none(self):
        emails = String.extract_emails("No emails here")
        assert emails == []

    def test_extract_urls_basic(self):
        urls = String.extract_urls("Visit https://example.com and http://test.com")
        assert len(urls) == 2
        assert all(isinstance(u, str) for u in urls)

    def test_extract_urls_none(self):
        urls = String.extract_urls("No URLs here")
        assert urls == []
