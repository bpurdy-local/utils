import os
import tempfile
from pathlib import Path

import pytest

from utils.env import Env


@pytest.fixture(autouse=True)
def clean_env():
    original_env = dict(os.environ)
    yield
    os.environ.clear()
    os.environ.update(original_env)


class TestEnvGet:

    def test_get_existing_variable(self):
        os.environ["TEST_VAR"] = "test_value"
        assert Env.get("TEST_VAR") == "test_value"

    def test_get_nonexistent_returns_none(self):
        assert Env.get("NONEXISTENT") is None

    def test_get_with_default(self):
        assert Env.get("NONEXISTENT", default="default_value") == "default_value"

    def test_get_required_raises_when_missing(self):
        with pytest.raises(ValueError, match="required but not set"):
            Env.get("REQUIRED_VAR", required=True)

    def test_get_required_returns_value_when_present(self):
        os.environ["REQUIRED_VAR"] = "value"
        assert Env.get("REQUIRED_VAR", required=True) == "value"


class TestEnvGetInt:

    def test_get_int_valid(self):
        os.environ["INT_VAR"] = "42"
        assert Env.get_int("INT_VAR") == 42

    def test_get_int_negative(self):
        os.environ["INT_VAR"] = "-10"
        assert Env.get_int("INT_VAR") == -10

    def test_get_int_with_default(self):
        assert Env.get_int("NONEXISTENT", default=100) == 100

    def test_get_int_invalid_raises(self):
        os.environ["INT_VAR"] = "not_a_number"
        with pytest.raises(ValueError, match="not a valid integer"):
            Env.get_int("INT_VAR")

    def test_get_int_required(self):
        with pytest.raises(ValueError, match="required but not set"):
            Env.get_int("REQUIRED_INT", required=True)


class TestEnvGetFloat:

    def test_get_float_valid(self):
        os.environ["FLOAT_VAR"] = "3.14"
        assert Env.get_float("FLOAT_VAR") == 3.14

    def test_get_float_integer_string(self):
        os.environ["FLOAT_VAR"] = "42"
        assert Env.get_float("FLOAT_VAR") == 42.0

    def test_get_float_scientific_notation(self):
        os.environ["FLOAT_VAR"] = "1.5e-3"
        assert Env.get_float("FLOAT_VAR") == 0.0015

    def test_get_float_with_default(self):
        assert Env.get_float("NONEXISTENT", default=2.5) == 2.5

    def test_get_float_invalid_raises(self):
        os.environ["FLOAT_VAR"] = "not_a_float"
        with pytest.raises(ValueError, match="not a valid float"):
            Env.get_float("FLOAT_VAR")


class TestEnvGetBool:

    def test_get_bool_true_values(self):
        true_values = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON", "t", "T", "y", "Y"]
        for value in true_values:
            os.environ["BOOL_VAR"] = value
            assert Env.get_bool("BOOL_VAR") is True, f"Failed for value: {value}"

    def test_get_bool_false_values(self):
        false_values = ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF", "f", "F", "n", "N", ""]
        for value in false_values:
            os.environ["BOOL_VAR"] = value
            assert Env.get_bool("BOOL_VAR") is False, f"Failed for value: {value}"

    def test_get_bool_with_default(self):
        assert Env.get_bool("NONEXISTENT", default=True) is True
        assert Env.get_bool("NONEXISTENT", default=False) is False

    def test_get_bool_invalid_raises(self):
        os.environ["BOOL_VAR"] = "maybe"
        with pytest.raises(ValueError, match="not a valid boolean"):
            Env.get_bool("BOOL_VAR")


class TestEnvGetList:

    def test_get_list_comma_separated(self):
        os.environ["LIST_VAR"] = "a,b,c"
        assert Env.get_list("LIST_VAR") == ["a", "b", "c"]

    def test_get_list_with_spaces(self):
        os.environ["LIST_VAR"] = "a, b, c"
        assert Env.get_list("LIST_VAR") == ["a", "b", "c"]

    def test_get_list_custom_separator(self):
        os.environ["LIST_VAR"] = "a:b:c"
        assert Env.get_list("LIST_VAR", separator=":") == ["a", "b", "c"]

    def test_get_list_empty_string(self):
        os.environ["LIST_VAR"] = ""
        assert Env.get_list("LIST_VAR") == []

    def test_get_list_single_item(self):
        os.environ["LIST_VAR"] = "single"
        assert Env.get_list("LIST_VAR") == ["single"]

    def test_get_list_with_default(self):
        assert Env.get_list("NONEXISTENT", default=["x", "y"]) == ["x", "y"]

    def test_get_list_filters_empty_items(self):
        os.environ["LIST_VAR"] = "a,,b,,c"
        assert Env.get_list("LIST_VAR") == ["a", "b", "c"]


class TestEnvGetPath:

    def test_get_path_valid(self):
        os.environ["PATH_VAR"] = "/tmp/test"
        result = Env.get_path("PATH_VAR")
        assert isinstance(result, Path)
        assert str(result) == "/tmp/test"

    def test_get_path_with_default(self):
        result = Env.get_path("NONEXISTENT", default="/default/path")
        assert isinstance(result, Path)
        assert str(result) == "/default/path"

    def test_get_path_default_as_path(self):
        result = Env.get_path("NONEXISTENT", default=Path("/default"))
        assert isinstance(result, Path)
        assert str(result) == "/default"

    def test_get_path_nonexistent_no_default(self):
        assert Env.get_path("NONEXISTENT") is None


class TestEnvSetUnset:

    def test_set_variable(self):
        Env.set("NEW_VAR", "new_value")
        assert os.environ["NEW_VAR"] == "new_value"

    def test_unset_variable(self):
        os.environ["VAR_TO_REMOVE"] = "value"
        Env.unset("VAR_TO_REMOVE")
        assert "VAR_TO_REMOVE" not in os.environ

    def test_unset_nonexistent_variable(self):
        Env.unset("NONEXISTENT")


class TestEnvHas:

    def test_has_existing_variable(self):
        os.environ["EXISTING"] = "value"
        assert Env.has("EXISTING") is True

    def test_has_nonexistent_variable(self):
        assert Env.has("NONEXISTENT") is False


class TestEnvLoadDotenv:

    def test_load_dotenv_basic(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
            f.flush()

            try:
                loaded = Env.load_dotenv(path=f.name)
                assert loaded == {"KEY1": "value1", "KEY2": "value2"}
                assert os.environ["KEY1"] == "value1"
                assert os.environ["KEY2"] == "value2"
            finally:
                os.unlink(f.name)

    def test_load_dotenv_with_quotes(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write('QUOTED_DOUBLE="double quoted"\n')
            f.write("QUOTED_SINGLE='single quoted'\n")
            f.flush()

            try:
                Env.load_dotenv(path=f.name)
                assert os.environ["QUOTED_DOUBLE"] == "double quoted"
                assert os.environ["QUOTED_SINGLE"] == "single quoted"
            finally:
                os.unlink(f.name)

    def test_load_dotenv_with_comments(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("# This is a comment\n")
            f.write("KEY1=value1\n")
            f.write("# Another comment\n")
            f.write("KEY2=value2\n")
            f.flush()

            try:
                loaded = Env.load_dotenv(path=f.name)
                assert len(loaded) == 2
                assert "KEY1" in loaded
                assert "KEY2" in loaded
            finally:
                os.unlink(f.name)

    def test_load_dotenv_with_escape_sequences(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write('MULTI_LINE="line1\\nline2"\n')
            f.write('WITH_TAB="col1\\tcol2"\n')
            f.flush()

            try:
                Env.load_dotenv(path=f.name)
                assert os.environ["MULTI_LINE"] == "line1\nline2"
                assert os.environ["WITH_TAB"] == "col1\tcol2"
            finally:
                os.unlink(f.name)

    def test_load_dotenv_no_override(self):
        os.environ["EXISTING"] = "original"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("EXISTING=new_value\n")
            f.flush()

            try:
                Env.load_dotenv(path=f.name, override=False)
                assert os.environ["EXISTING"] == "original"
            finally:
                os.unlink(f.name)

    def test_load_dotenv_with_override(self):
        os.environ["EXISTING"] = "original"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("EXISTING=new_value\n")
            f.flush()

            try:
                Env.load_dotenv(path=f.name, override=True)
                assert os.environ["EXISTING"] == "new_value"
            finally:
                os.unlink(f.name)

    def test_load_dotenv_nonexistent_file(self):
        loaded = Env.load_dotenv(path="/nonexistent/.env")
        assert loaded == {}


class TestEnvToDict:

    def test_to_dict(self):
        os.environ["TEST1"] = "value1"
        os.environ["TEST2"] = "value2"

        env_dict = Env.to_dict()
        assert isinstance(env_dict, dict)
        assert "TEST1" in env_dict
        assert "TEST2" in env_dict


class TestEnvGetWithPrefix:

    def test_get_with_prefix(self):
        os.environ["APP_NAME"] = "myapp"
        os.environ["APP_VERSION"] = "1.0"
        os.environ["DB_HOST"] = "localhost"

        app_vars = Env.get_with_prefix("APP_")
        assert len(app_vars) == 2
        assert app_vars["APP_NAME"] == "myapp"
        assert app_vars["APP_VERSION"] == "1.0"
        assert "DB_HOST" not in app_vars


class TestEnvRequire:

    def test_require_all_present(self):
        os.environ["REQ1"] = "value1"
        os.environ["REQ2"] = "value2"

        Env.require("REQ1", "REQ2")

    def test_require_missing_raises(self):
        os.environ["REQ1"] = "value1"

        with pytest.raises(ValueError, match="Required environment variables are missing: REQ2"):
            Env.require("REQ1", "REQ2")

    def test_require_multiple_missing_raises(self):
        with pytest.raises(ValueError, match="REQ1"):
            Env.require("REQ1", "REQ2", "REQ3")
