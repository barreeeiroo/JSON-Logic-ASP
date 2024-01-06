from enum import Enum


class PredicateNames(str, Enum):
    ARRAY_MERGE = "merge"
    ARRAY_IN = "in"
    BOOLEAN_AND = "and"
    BOOLEAN_OR = "or"
    BOOLEAN_NOT = "neg"
    DATA_VAR = "var"
    DATA_MISSING = "missing"
    LOGIC_IF = "if"
    LOGIC_IF_ELIF = "elif"
    LOGIC_IF_ELSE = "else"
    LOGIC_EQUALS = "eq"
    LOGIC_NOTEQUALS = "neq"
    LOGIC_STRICTEQUALS = "seq"
    LOGIC_STRICTNOTEQUALS = "sneq"
    LOGIC_LOWER = "lt"
    LOGIC_LOWEREQUAL = "lte"
    LOGIC_GREATER = "gt"
    LOGIC_GREATEREQUAL = "gte"

    RULE = "rule"

    BOOL = "bool"


class VariableNames(str, Enum):
    ANY = "_"
    VAR = "V"
    MERGE = "M"
    IN = "I"
