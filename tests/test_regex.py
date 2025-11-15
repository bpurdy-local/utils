from utils import Regex


class TestRegexMatch:
    def test_match_basic(self):
        match = Regex.match(r"\d+", "123abc")
        assert match is not None
        assert match.group() == "123"

    def test_match_no_match(self):
        match = Regex.match(r"\d+", "abc")
        assert match is None


class TestRegexSearch:
    def test_search_basic(self):
        match = Regex.search(r"\d+", "abc123def")
        assert match is not None
        assert match.group() == "123"


class TestRegexFindall:
    def test_findall_basic(self):
        result = Regex.findall(r"\d+", "abc123def456")
        assert result == ["123", "456"]


class TestRegexSub:
    def test_sub_basic(self):
        result = Regex.sub(r"\d+", "X", "abc123def456")
        assert result == "abcXdefX"


class TestRegexSplit:
    def test_split_basic(self):
        result = Regex.split(r"\s+", "hello   world")
        assert result == ["hello", "world"]


class TestRegexGroups:
    def test_groups(self):
        match = Regex.match(r"(\d+)-(\d+)", "123-456")
        groups = Regex.groups(match)
        assert groups == ("123", "456")

    def test_groupdict(self):
        match = Regex.match(r"(?P<year>\d+)-(?P<month>\d+)", "2024-01")
        groupdict = Regex.groupdict(match)
        assert groupdict == {"year": "2024", "month": "01"}


class TestRegexIsValid:
    def test_is_valid_true(self):
        assert Regex.is_valid(r"^\d+$", "123") is True

    def test_is_valid_false(self):
        assert Regex.is_valid(r"^\d+$", "abc") is False
