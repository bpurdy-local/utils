from utils.json_utils import JSON


class TestJSONPrettyMinify:
    def test_pretty_dict(self):
        data = {"a": 1, "b": 2}
        result = JSON.pretty(data)
        assert "\n" in result
        assert "  " in result  # Default indent=2

    def test_pretty_with_custom_indent(self):
        data = {"a": 1}
        result = JSON.pretty(data, indent=4)
        assert "    " in result  # 4 spaces

    def test_pretty_list(self):
        data = [1, 2, 3]
        result = JSON.pretty(data)
        assert "\n" in result

    def test_pretty_nested(self):
        data = {"a": {"b": {"c": 1}}}
        result = JSON.pretty(data)
        assert result.count("\n") >= 3

    def test_minify(self):
        json_str = '{"a": 1, "b": 2}'
        result = JSON.minify(json_str)
        assert result == '{"a":1,"b":2}'

    def test_minify_with_whitespace(self):
        json_str = """{
            "a": 1,
            "b": 2
        }"""
        result = JSON.minify(json_str)
        assert " " not in result
        assert "\n" not in result


class TestJSONFlatten:
    def test_flatten_simple(self):
        data = {"a": {"b": 1, "c": 2}}
        result = JSON.flatten(data)
        assert result == {"a.b": 1, "a.c": 2}

    def test_flatten_deeply_nested(self):
        data = {"x": {"y": {"z": 3}}}
        result = JSON.flatten(data)
        assert result == {"x.y.z": 3}

    def test_flatten_already_flat(self):
        data = {"a": 1, "b": 2}
        result = JSON.flatten(data)
        assert result == {"a": 1, "b": 2}

    def test_flatten_mixed_nesting(self):
        data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        result = JSON.flatten(data)
        assert result == {"a": 1, "b.c": 2, "b.d.e": 3}

    def test_flatten_custom_separator(self):
        data = {"a": {"b": 1}}
        result = JSON.flatten(data, separator="_")
        assert result == {"a_b": 1}

    def test_flatten_empty_dict(self):
        result = JSON.flatten({})
        assert result == {}

    def test_flatten_preserves_non_dict_values(self):
        data = {"a": {"b": [1, 2, 3]}}
        result = JSON.flatten(data)
        assert result == {"a.b": [1, 2, 3]}

    def test_flatten_with_empty_nested_dict(self):
        data = {"a": {"b": {}}}
        result = JSON.flatten(data)
        assert result == {"a.b": {}}


class TestJSONUnflatten:
    def test_unflatten_simple(self):
        data = {"a.b": 1, "a.c": 2}
        result = JSON.unflatten(data)
        assert result == {"a": {"b": 1, "c": 2}}

    def test_unflatten_deeply_nested(self):
        data = {"x.y.z": 3}
        result = JSON.unflatten(data)
        assert result == {"x": {"y": {"z": 3}}}

    def test_unflatten_already_flat(self):
        data = {"a": 1, "b": 2}
        result = JSON.unflatten(data)
        assert result == {"a": 1, "b": 2}

    def test_unflatten_custom_separator(self):
        data = {"a_b": 1}
        result = JSON.unflatten(data, separator="_")
        assert result == {"a": {"b": 1}}

    def test_unflatten_empty_dict(self):
        result = JSON.unflatten({})
        assert result == {}

    def test_flatten_unflatten_roundtrip(self):
        original = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}
        flattened = JSON.flatten(original)
        unflattened = JSON.unflatten(flattened)
        assert unflattened == original


class TestJSONParse:
    def test_parse_valid_json(self):
        result = JSON.parse('{"a": 1}')
        assert result == {"a": 1}

    def test_parse_invalid_json_returns_default(self):
        result = JSON.parse("invalid json", default={})
        assert result == {}

    def test_parse_invalid_json_returns_none(self):
        result = JSON.parse("invalid")
        assert result is None

    def test_parse_custom_default(self):
        result = JSON.parse("invalid", default=[])
        assert result == []

    def test_parse_list(self):
        result = JSON.parse("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_parse_null(self):
        result = JSON.parse("null")
        assert result is None

    def test_parse_number(self):
        result = JSON.parse("42")
        assert result == 42

    def test_parse_string(self):
        result = JSON.parse('"hello"')
        assert result == "hello"


class TestJSONValidateSchema:
    def test_validate_simple_schema(self):
        schema = {"name": str, "age": int}
        data = {"name": "John", "age": 30}
        assert JSON.validate_schema(data, schema) is True

    def test_validate_schema_type_mismatch(self):
        schema = {"name": str, "age": int}
        data = {"name": "John", "age": "30"}
        assert JSON.validate_schema(data, schema) is False

    def test_validate_schema_missing_field(self):
        schema = {"name": str, "age": int}
        data = {"name": "John"}
        assert JSON.validate_schema(data, schema) is False

    def test_validate_schema_nested(self):
        schema = {"user.name": str, "user.age": int}
        data = {"user": {"name": "John", "age": 30}}
        assert JSON.validate_schema(data, schema) is True

    def test_validate_schema_list_type(self):
        schema = {"items": list}
        data = {"items": [1, 2, 3]}
        assert JSON.validate_schema(data, schema) is True

    def test_validate_schema_dict_type(self):
        schema = {"config": dict}
        data = {"config": {"key": "value"}}
        assert JSON.validate_schema(data, schema) is True

    def test_validate_schema_bool_type(self):
        schema = {"active": bool}
        data = {"active": True}
        assert JSON.validate_schema(data, schema) is True

    def test_validate_schema_float_type(self):
        schema = {"price": float}
        data = {"price": 9.99}
        assert JSON.validate_schema(data, schema) is True


class TestJSONToFromString:
    def test_to_string(self):
        data = {"a": 1}
        result = JSON.to_string(data)
        assert result == '{"a": 1}'

    def test_to_string_pretty(self):
        data = {"a": 1}
        result = JSON.to_string(data, pretty=True)
        assert "\n" in result

    def test_to_string_custom_indent(self):
        data = {"a": 1}
        result = JSON.to_string(data, pretty=True, indent=4)
        assert "    " in result

    def test_from_string(self):
        json_str = '{"a": 1}'
        result = JSON.from_string(json_str)
        assert result == {"a": 1}

    def test_to_from_string_roundtrip(self):
        original = {"a": 1, "b": [2, 3], "c": {"d": 4}}
        json_str = JSON.to_string(original)
        result = JSON.from_string(json_str)
        assert result == original


class TestJSONIsValid:
    def test_is_valid_true(self):
        assert JSON.is_valid('{"a": 1}') is True

    def test_is_valid_false(self):
        assert JSON.is_valid("invalid") is False

    def test_is_valid_list(self):
        assert JSON.is_valid("[1, 2, 3]") is True

    def test_is_valid_string(self):
        assert JSON.is_valid('"hello"') is True

    def test_is_valid_number(self):
        assert JSON.is_valid("42") is True

    def test_is_valid_null(self):
        assert JSON.is_valid("null") is True

    def test_is_valid_malformed(self):
        assert JSON.is_valid('{"a": }') is False


class TestJSONEdgeCases:
    def test_empty_objects(self):
        data = {"empty_dict": {}, "empty_list": []}
        flattened = JSON.flatten(data)
        assert "empty_dict" in flattened
        assert "empty_list" in flattened

    def test_large_nested_structure(self):
        data = {"level1": {"level2": {"level3": {"level4": {"level5": "deep"}}}}}
        flattened = JSON.flatten(data)
        assert "level1.level2.level3.level4.level5" in flattened
        unflattened = JSON.unflatten(flattened)
        assert unflattened == data
