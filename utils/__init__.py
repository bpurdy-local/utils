"""Utility library with type wrappers and common functions."""

from utils.collections import Collection
from utils.common import (
    chunk,
    debounce,
    flatten,
    group_by,
    retry,
    slugify,
    throttle,
)
from utils.datetime import Datetime
from utils.decorators import Decorators
from utils.dict import Dict
from utils.encoding import (
    base64_decode,
    base64_encode,
    defang,
    fang,
    html_decode,
    html_encode,
    url_decode,
    url_encode,
)
from utils.file_io import FileIO
from utils.integer import Integer
from utils.iterable import Iterable
from utils.misc import (
    bytes_to_human,
    clamp,
    generate_id,
    hash_string,
    memoize,
    once,
    percentage,
)
from utils.path import Path
from utils.random_utils import Random
from utils.regex import Regex
from utils.string import String
from utils.validation import (
    is_credit_card,
    is_email,
    is_empty,
    is_hex_color,
    is_integer,
    is_ipv4,
    is_numeric,
    is_phone,
    is_url,
    is_uuid,
)
from utils.validator import Validator

deep_get = Dict.deep_get
deep_set = Dict.deep_set
first = Collection.first
last = Collection.last
omit = Collection.omit
partition = Collection.partition
pick = Collection.pick
pluck = Collection.pluck
unique = Collection.unique
zip_dict = Collection.zip_dict

__all__ = [
    # Wrapper Classes
    "String",
    "Integer",
    "Iterable",
    "Datetime",
    "Dict",
    "Path",
    "Regex",
    "Random",
    "FileIO",
    "Decorators",
    "Validator",
    "Collection",
    # Common
    "chunk",
    "debounce",
    "flatten",
    "group_by",
    "retry",
    "slugify",
    "throttle",
    # Collections
    "deep_get",
    "deep_set",
    "first",
    "last",
    "omit",
    "partition",
    "pick",
    "pluck",
    "unique",
    "zip_dict",
    # Misc
    "bytes_to_human",
    "clamp",
    "generate_id",
    "hash_string",
    "memoize",
    "once",
    "percentage",
    # Encoding/Decoding
    "base64_encode",
    "base64_decode",
    "url_encode",
    "url_decode",
    "html_encode",
    "html_decode",
    "fang",
    "defang",
    # Validation
    "is_credit_card",
    "is_email",
    "is_empty",
    "is_hex_color",
    "is_integer",
    "is_ipv4",
    "is_numeric",
    "is_phone",
    "is_uuid",
    "is_url",
]
