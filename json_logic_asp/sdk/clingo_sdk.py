from typing import List, Tuple, Dict

from clingo import Control


def run_clingo(absolute_file_path: str) -> Tuple[str, List[str], Dict]:
    rules: List[str] = []

    prg = Control(['--stats'])
    prg.load(absolute_file_path)
    prg.ground([("base", [])])

    with prg.solve(yield_=True) as hdl:
        for model in hdl:
            for symbol in model.symbols(terms=True, shown=True):
                if symbol.name != "rule" and len(symbol.arguments) != 1:
                    continue
                rules.append(symbol.arguments[0].name)
            hdl.cancel()
        status = str(hdl.get())

    return status, rules, prg.statistics
