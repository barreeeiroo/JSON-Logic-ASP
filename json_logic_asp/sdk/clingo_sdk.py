from typing import Dict, List, Tuple

from clingo import Control


def run_clingo(absolute_file_path: str) -> Tuple[str, List[str], Dict]:
    rules: List[str] = []

    prg = Control(["--stats"])
    try:
        prg.load(absolute_file_path)
    except (RuntimeError, MemoryError):
        return "ERROR", [], {}

    prg.ground([("base", [])])

    with prg.solve(yield_=True) as hdl:  # type: ignore
        for model in hdl:
            for symbol in model.symbols(terms=True, shown=True):
                if symbol.name != "rule" or len(symbol.arguments) != 1:
                    continue
                rules.append(symbol.arguments[0].name)
            hdl.cancel()
        status = str(hdl.get())

    return status, rules, prg.statistics
