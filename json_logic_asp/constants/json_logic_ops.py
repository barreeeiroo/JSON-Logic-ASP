from enum import Enum


class JsonLogicOps(str, Enum):
    DATA_VAR = "var"
    DATA_MISSING = "missing"
    DATA_MISSING_SOME = "missing_some"

    LOGIC_IF = "if"
    LOGIC_EQ = "=="
    LOGIC_STRICT_EQ = "==="
    LOGIC_NOT_EQ = "!="
    LOGIC_STRICT_NOT_EQ = "!=="
    BOOLEAN_NOT = "!"
    BOOLEAN_NOT_NOT = "!!"
    BOOLEAN_AND = "and"
    BOOLEAN_OR = "or"

    NUMERIC_GT = ">"
    NUMERIC_GTE = ">="
    NUMERIC_LT = "<"
    NUMERIC_LTE = "<="
    NUMERIC_MAX = "max"
    NUMERIC_MIN = "min"
    NUMERIC_SUM = "+"
    NUMERIC_MINUS = "-"
    NUMERIC_MULTIPLY = "*"
    NUMERIC_DIVIDE = "/"
    NUMERIC_MODULUS = "%"

    ARRAY_MAP = "map"
    ARRAY_REDUCE = "reduce"
    ARRAY_filter = "filter"
    ARRAY_ALL = "all"
    ARRAY_NONE = "none"
    ARRAY_SOME = "some"
    ARRAY_MERGE = "merge"
    ARRAY_IN = "in"

    # STRING_IN = "in"
    STRING_CAT = "cat"
    STRING_SUBSTR = "substr"

    MISC_LOG = "log"
