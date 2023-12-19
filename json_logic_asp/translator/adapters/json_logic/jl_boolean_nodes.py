from typing import Dict, List

from json_logic_asp.translator.adapters.asp.asp_nodes import PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.translator.models.jl_base import JsonLogicDefinitionNode, JsonLogicRuleNode
from json_logic_asp.utils.id_management import generate_unique_id, generate_constant_string
from json_logic_asp.translator.adapters.json_logic.jl_data_nodes import DataVarNode


class BooleanAndNode(JsonLogicRuleNode):
    def __init__(self, child_nodes: List[JsonLogicDefinitionNode]):
        # Remove duplicates
        self.child_nodes: List[JsonLogicDefinitionNode] = list(set(child_nodes))

        node_id = generate_unique_id()

        # For each child node, get the atom and use it as literal
        child_statements: Dict[str, PredicateAtom] = {}
        for child_node in self.child_nodes:
            for asp_statement in child_node.asp_statements:
                child_statements[child_node.id] = asp_statement.atom

        self.statement = RuleStatement(
            atom=PredicateAtom(predicate_name="and", terms=[node_id]),
            literals=list(child_statements.values()),
        )

        super().__init__(node_id=node_id, asp_statements=[self.statement])

    def to_asp(self, with_comment: bool = False):
        stmts = []
        for child_node in self.child_nodes:
            stmts.extend(child_node.to_asp(with_comment=with_comment))

        if with_comment and self.statement.comment_to_asp():
            stmts.append(self.statement.comment_to_asp())
        stmts.append(self.statement.to_asp())
        return stmts

    def __str__(self):
        return f"AND({self.id})"

    def __hash__(self):
        return hash(("and", *sorted(hash(child) for child in self.child_nodes)))


class BooleanOrNode(JsonLogicRuleNode):
    def __init__(self, child_nodes: List[JsonLogicDefinitionNode]):
        # Remove duplicates
        self.child_nodes: List[JsonLogicDefinitionNode] = list(set(child_nodes))

        node_id = generate_unique_id()

        self.statements: List[RuleStatement] = []

        for child_node in self.child_nodes:
            # For each child node, get the atom and use it as literal
            child_statements: Dict[str, PredicateAtom] = {}
            for asp_statement in child_node.asp_statements:
                child_statements[child_node.id] = asp_statement.atom

            self.statements.append(
                RuleStatement(
                    atom=PredicateAtom(predicate_name="or", terms=[node_id]),
                    literals=list(child_statements.values()),
                )
            )

        super().__init__(node_id=node_id, asp_statements=self.statements)

    def to_asp(self, with_comment: bool = False):
        stmts = []
        for child_node in self.child_nodes:
            stmts.extend(child_node.to_asp(with_comment=with_comment))

        for statement in self.statements:
            if with_comment and statement.comment_to_asp():
                stmts.append(statement.comment_to_asp())
            stmts.append(statement.to_asp())

        return stmts

    def __str__(self):
        return f"OR({self.id})"

    def __hash__(self):
        return hash(("or", *sorted(hash(child) for child in self.child_nodes)))


class BooleanNotNode(JsonLogicRuleNode):
    def __init__(self, child_nodes: List[JsonLogicDefinitionNode]):
        # Remove duplicates
        self.child_nodes: List[JsonLogicDefinitionNode] = list(set(child_nodes))

        node_id = generate_unique_id()

        # For each child node, get the atom and use it as literal
        child_statements: Dict[str, PredicateAtom] = {}
        for child_node in self.child_nodes:
            if isinstance(child_node, DataVarNode):
                child_statements[child_node.id] = PredicateAtom(
                    predicate_name="var",
                    terms=[generate_constant_string(child_node.var_name), "_"],
                    negated=True,
                )
            else:
                for asp_statement in child_node.asp_statements:
                    child_statements[child_node.id] = PredicateAtom(
                        predicate_name=asp_statement.atom.predicate_name,
                        terms=asp_statement.atom.terms,
                        negated=True,
                    )

        self.statement = RuleStatement(
            atom=PredicateAtom(predicate_name="neg", terms=[node_id]),
            literals=list(child_statements.values()),
        )

        super().__init__(node_id=node_id, asp_statements=[self.statement])

    def to_asp(self, with_comment: bool = False):
        stmts = []
        for child_node in self.child_nodes:
            stmts.extend(child_node.to_asp(with_comment=with_comment))

        if with_comment and self.statement.comment_to_asp():
            stmts.append(self.statement.comment_to_asp())
        stmts.append(self.statement.to_asp())
        return stmts

    def __str__(self):
        return f"NOT({self.id})"

    def __hash__(self):
        return hash(("not", *sorted(hash(child) for child in self.child_nodes)))
