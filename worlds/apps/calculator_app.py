"""Calculator application — MCP server for safe mathematical expression evaluation."""

from __future__ import annotations

import ast
import math
import statistics

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Safe expression evaluator
# ---------------------------------------------------------------------------

_SAFE_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.FloorDiv,
    ast.USub,
    ast.UAdd,
    # Also allow function calls to whitelisted names
    ast.Call,
    ast.Name,
    ast.Load,
}

_SAFE_NAMES = {
    # Math constants
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,
    # Math functions
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "cbrt": math.cbrt,
    "exp": math.exp,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
    "gcd": math.gcd,
    "lcm": math.lcm,
    "degrees": math.degrees,
    "radians": math.radians,
    "hypot": math.hypot,
    "pow": pow,
    "min": min,
    "max": max,
    "sum": sum,
}


def _check_safe(node: ast.AST) -> None:
    if type(node) not in _SAFE_NODES:
        raise ValueError(f"Unsafe operation: {type(node).__name__}")
    for child in ast.iter_child_nodes(node):
        _check_safe(child)


def _eval_expr(expr: str) -> float:
    expr = expr.strip()
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Syntax error: {exc}") from exc
    _check_safe(tree.body)

    # Extra check: only allow safe Name references
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id not in _SAFE_NAMES:
            raise ValueError(f"Unknown name: '{node.id}'")

    result = eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, _SAFE_NAMES)  # noqa: S307
    return float(result)


class CalculatorApp:
    """Safe mathematical calculator supporting arithmetic, algebra, and common math functions."""

    def __init__(self) -> None:
        self.name = "calculator"

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def calculate(self, expression: str) -> dict:
        """Evaluate a mathematical expression and return the result.

        Supports: +, -, *, /, ** (power), % (modulo), // (floor division),
        and functions: sqrt, log, log2, log10, sin, cos, tan, asin, acos,
        atan, atan2, sinh, cosh, tanh, ceil, floor, factorial, gcd, lcm,
        degrees, radians, hypot, abs, round, pow, min, max.
        Constants: pi, e, tau, inf.

        Args:
            expression: Mathematical expression to evaluate (e.g. '2 + 2', 'sqrt(144)',
                        'sin(pi/2)', 'log(100, 10)', '2**10 + factorial(5)').

        Returns:
            dict: Contains 'expression', 'result' (float), and 'result_int' (if result
                  is a whole number). Returns error dict on invalid expression.

        Tags:
            calculator, math, expression, evaluate, compute
        """
        try:
            result = _eval_expr(expression)
        except (ValueError, ZeroDivisionError, OverflowError) as exc:
            return {"error": str(exc), "expression": expression}

        out: dict = {"expression": expression, "result": result}
        if result == int(result) and abs(result) < 1e15:
            out["result_int"] = int(result)
        return out

    def statistics(self, numbers: list[float], include_all: bool = False) -> dict:
        """Compute descriptive statistics for a list of numbers.

        Args:
            numbers: List of numeric values.
            include_all: When True, also computes mode, variance, and stdev.
                         Default False (returns count, sum, mean, min, max, median).

        Returns:
            dict: Statistical summary of the input list, or error dict if list is empty.

        Tags:
            calculator, statistics, mean, median, stdev, math
        """
        if not numbers:
            return {"error": "Cannot compute statistics on an empty list."}
        result: dict = {
            "count": len(numbers),
            "sum": sum(numbers),
            "mean": statistics.mean(numbers),
            "median": statistics.median(numbers),
            "min": min(numbers),
            "max": max(numbers),
        }
        if include_all:
            try:
                result["mode"] = statistics.mode(numbers)
            except statistics.StatisticsError:
                result["mode"] = None  # no unique mode
            if len(numbers) > 1:
                result["variance"] = statistics.variance(numbers)
                result["stdev"] = statistics.stdev(numbers)
        return result

    def convert_units(self, value: float, from_unit: str, to_unit: str) -> dict:
        """Convert a value between common units of measurement.

        Supported unit groups:
        - Length: m, km, cm, mm, mile, ft, inch, yard
        - Weight: kg, g, lb, oz, ton
        - Temperature: celsius, fahrenheit, kelvin
        - Area: m2, km2, cm2, ft2, acre, hectare
        - Volume: liter, ml, gallon, quart, pint, cup, fl_oz
        - Speed: m_s, km_h, mph, knot
        - Time: second, minute, hour, day, week

        Args:
            value: Numeric value to convert.
            from_unit: Source unit (case-insensitive).
            to_unit: Target unit (case-insensitive).

        Returns:
            dict: Contains 'value', 'from_unit', 'to_unit', 'result'.
                  Returns error dict for unsupported or mismatched units.

        Tags:
            calculator, convert, units, measurement, transform
        """
        # Conversion factors to SI base unit
        _TO_BASE: dict[str, tuple[str, float, float]] = {
            # length → meters
            "m": ("length", 1.0, 0),
            "km": ("length", 1000.0, 0),
            "cm": ("length", 0.01, 0),
            "mm": ("length", 0.001, 0),
            "mile": ("length", 1609.344, 0),
            "ft": ("length", 0.3048, 0),
            "inch": ("length", 0.0254, 0),
            "yard": ("length", 0.9144, 0),
            # weight → kg
            "kg": ("weight", 1.0, 0),
            "g": ("weight", 0.001, 0),
            "lb": ("weight", 0.453592, 0),
            "oz": ("weight", 0.0283495, 0),
            "ton": ("weight", 907.185, 0),
            # temperature (special handling)
            "celsius": ("temperature", 1.0, 0),
            "fahrenheit": ("temperature", 1.0, 0),
            "kelvin": ("temperature", 1.0, 0),
            # area → m²
            "m2": ("area", 1.0, 0),
            "km2": ("area", 1e6, 0),
            "cm2": ("area", 1e-4, 0),
            "ft2": ("area", 0.092903, 0),
            "acre": ("area", 4046.86, 0),
            "hectare": ("area", 10000.0, 0),
            # volume → liters
            "liter": ("volume", 1.0, 0),
            "ml": ("volume", 0.001, 0),
            "gallon": ("volume", 3.78541, 0),
            "quart": ("volume", 0.946353, 0),
            "pint": ("volume", 0.473176, 0),
            "cup": ("volume", 0.236588, 0),
            "fl_oz": ("volume", 0.0295735, 0),
            # speed → m/s
            "m_s": ("speed", 1.0, 0),
            "km_h": ("speed", 1 / 3.6, 0),
            "mph": ("speed", 0.44704, 0),
            "knot": ("speed", 0.514444, 0),
            # time → seconds
            "second": ("time", 1.0, 0),
            "minute": ("time", 60.0, 0),
            "hour": ("time", 3600.0, 0),
            "day": ("time", 86400.0, 0),
            "week": ("time", 604800.0, 0),
        }

        fu = from_unit.lower()
        tu = to_unit.lower()

        if fu not in _TO_BASE:
            return {"error": f"Unknown unit: '{from_unit}'"}
        if tu not in _TO_BASE:
            return {"error": f"Unknown unit: '{to_unit}'"}

        from_group = _TO_BASE[fu][0]
        to_group = _TO_BASE[tu][0]

        if from_group != to_group:
            return {"error": f"Cannot convert between '{from_unit}' ({from_group}) and '{to_unit}' ({to_group})"}

        # Temperature is a special case (offset conversions)
        if from_group == "temperature":
            if fu == "celsius" and tu == "fahrenheit":
                result = value * 9 / 5 + 32
            elif fu == "fahrenheit" and tu == "celsius":
                result = (value - 32) * 5 / 9
            elif fu == "celsius" and tu == "kelvin":
                result = value + 273.15
            elif fu == "kelvin" and tu == "celsius":
                result = value - 273.15
            elif fu == "fahrenheit" and tu == "kelvin":
                result = (value - 32) * 5 / 9 + 273.15
            elif fu == "kelvin" and tu == "fahrenheit":
                result = (value - 273.15) * 9 / 5 + 32
            else:
                result = value  # same unit
        else:
            base = value * _TO_BASE[fu][1]
            result = base / _TO_BASE[tu][1]

        return {"value": value, "from_unit": from_unit, "to_unit": to_unit, "result": round(result, 10)}

    def percent(self, operation: str, a: float, b: float) -> dict:
        """Perform percentage-related calculations.

        Args:
            operation: One of:
                - 'of': What is A% of B? (e.g. 15% of 200 = 30)
                - 'change': Percentage change from A to B
                - 'is_what_pct': A is what percent of B?
                - 'add': Add A% to B (e.g. B + A% of B)
                - 'subtract': Subtract A% from B
            a: First number (the percentage in 'of', 'add', 'subtract'; the start value in 'change').
            b: Second number (the base value or end value depending on operation).

        Returns:
            dict: Contains 'operation', 'a', 'b', 'result', and a human-readable 'description'.

        Tags:
            calculator, percent, percentage, math, compute
        """
        op = operation.lower()
        if op == "of":
            result = (a / 100) * b
            desc = f"{a}% of {b} = {result}"
        elif op == "change":
            if a == 0:
                return {"error": "Cannot compute percentage change from 0"}
            result = ((b - a) / abs(a)) * 100
            desc = f"Change from {a} to {b} = {result:+.4f}%"
        elif op == "is_what_pct":
            if b == 0:
                return {"error": "Cannot compute percentage: divisor is 0"}
            result = (a / b) * 100
            desc = f"{a} is {result:.4f}% of {b}"
        elif op == "add":
            result = b + (a / 100) * b
            desc = f"{b} + {a}% = {result}"
        elif op == "subtract":
            result = b - (a / 100) * b
            desc = f"{b} - {a}% = {result}"
        else:
            return {"error": f"Unknown operation '{operation}'. Use: of, change, is_what_pct, add, subtract"}
        return {"operation": op, "a": a, "b": b, "result": result, "description": desc}

    # ------------------------------------------------------------------

    def list_tools(self) -> list:
        return [self.calculate, self.statistics, self.convert_units, self.percent]

    def create_mcp_server(self) -> FastMCP:
        mcp = FastMCP(self.name)
        for tool_fn in self.list_tools():
            mcp.tool()(tool_fn)
        return mcp


if __name__ == "__main__":
    app = CalculatorApp()
    server = app.create_mcp_server()
    server.run()
