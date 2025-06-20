import ast
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Final, Type

from scripts_engine.types import ModeLiteral


class ScriptsSettings:
    # Режим исполнения скрипта.
    MODE: Final[ModeLiteral] = "exec"
    # Зарезервированное имя переменной для организации обратной связи с кодом скрипта.
    RESULT_VARNAME: Final[str] = "result"
    # Заглушка имени файла исполняемого скрипта.
    FILENAME_PLACEHOLDER: Final[str] = "<wf-scripts_engine>"
    # Разрешённые абстрактные узлы AST скрипта.
    ALLOWED_AST_NODES: Final[set[Type[ast.AST]]] = {
        # Корневой узел.
        ast.Module,
        # Выражения.
        ast.Expression,
        ast.Expr,
        # Базовая нода для бинарных операций.
        ast.BinOp,
        # Базовая нода для унарных операций.
        ast.UnaryOp,
        # Для получения доступа к памяти по именам (переменных) `x`, `y`, `z`.
        ast.Name,
        # Загрузка и сохранение в память.
        ast.Store,
        # Загрузка сохранённого из памяти.
        ast.Load,
        # Вызов callable-объектов (функций и методов).
        ast.Call,
        # Доступ к атрибутам объектов.
        ast.Attribute,
        # Ключевое слово `pass`.
        ast.Pass,
        # Присваивание значений: `=`.
        ast.Assign,
        # Аннотированное присваивание: `+=`, `-=`, `*=`, ...
        ast.AugAssign,
        # Узлы in-place констант: `4`, `"123"`, `3.14`.
        ast.Constant,
        # Логические (булевы) операции.
        ast.Compare,
        ast.BoolOp,
        ast.And,  # `and`
        ast.Or,  # `or`
        ast.If,  # `if`
        ast.IfExp,  # тернарный оператор с `if`
        ast.Not,  # `not`
        ast.Gt,  # `>`
        ast.GtE,  # `>=`
        ast.Lt,  # `<`
        ast.LtE,  # `<=`
        ast.Eq,  # `==`
        ast.NotEq,  # `!=`
        ast.Is,  # `is`
        ast.IsNot,  # `is not`
        ast.In,  # `in`
        ast.NotIn,  # `not in`
        # Циклы.
        ast.For,  # `for`
        ast.While,  # `while`
        # Математические операторы и операции.
        ast.Add,  # `+`
        ast.Sub,  # `-`
        ast.Mult,  # `*`
        ast.Div,  # `/`
        ast.FloorDiv,  # `//`
        ast.Mod,  # `%`
        ast.Pow,  # `**`
        # Cтроковые узлы.
        ast.JoinedStr,
        ast.FormattedValue,
        # Составные типы.
        ast.List,
        ast.Tuple,
        ast.Set,
        ast.Dict,
    }
    # Разрешённые глобальные имена.
    ALLOWED_GLOBALS: Final[dict[str, Any]] = {
        # Переопределяем `__builtins__` для безопасности.
        "__builtins__": {},  # не удалять!
        # Поддерживаемые singleton-значения.
        "True": True,
        "False": False,
        "None": None,
        # Поддерживаемые типы и приведение типов.
        "type": type,
        "bool": bool,
        "int": int,
        "float": float,
        "Decimal": Decimal,
        "str": str,
        "list": list,
        "tuple": tuple,
        "set": set,
        "dict": dict,
        "date": date,
        "datetime": datetime,
        # Другие полезные build-ins.
        "abs": abs,
        "all": all,
        "any": any,
        "len": len,
        "max": max,
        "min": min,
        "round": round,
        "sorted": sorted,
        "sum": sum,
        "range": range,
        "zip": zip,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "exit": exit,
    }


settings = ScriptsSettings()
