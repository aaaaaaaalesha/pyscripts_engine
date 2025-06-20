import ast
import traceback
from types import CodeType
from typing import Any, Final

from scripts_engine.exceptions import ScriptCompileException, ScriptRuntimeException
from .conf import settings
from .types import Object


class PyScriptsEngine:
    """Пользовательский движок для исполнения скриптов на основе Python-подобного AST."""

    class ReadOnlyObjectWrapper:
        """Позволяет только получать read-only доступ к атрибутам объекта."""
        # Атрибуты, доступ к которым ограничен.
        RESTRICTED_ATTRS: Final[set[str]] = {
            "create",
            "save",
            "update",
            "delete",
        }

        def __init__(self, obj: Object):
            self.__object = obj

        def __getattr__(self, attr: str) -> Any:
            if attr in self.RESTRICTED_ATTRS:
                raise AttributeError(f"Недопустимый атрибут `{attr}`")
            return getattr(self.__object, attr)

    def __init__(self, obj: Object, type_object: int):
        """
        :param obj: Объект (нечто, поддерживающие протокол `__getattr__`).
        :param type_object: Тип объекта - численный экземпляр перечисления.
        """
        self.type_object = type_object
        self.object = self.ReadOnlyObjectWrapper(obj)
        # Исходный код скрипта построчно (нужно для указания места ошибок).
        self.__source_code: list[str] | None = None
        # Скомпилированный код, полученный в методе `compile`.
        self.__compiled_code: CodeType | None = None
        # Локальная область видимости скрипта.
        self.__locals = {
            "object": self.object,
            "type_object": self.type_object,
        }
        # Глобальная область видимости.
        self.__globals = {
            **settings.ALLOWED_GLOBALS,
            # Организуем канал обратной связи через зарезервированную переменную.
            settings.RESULT_VARNAME: None,
        }

    def compile(self, source_code: str) -> CodeType:
        """
        Компилирует переданный исходный Python-подобный код с пользовательскими
        ограничениями используемых синтаксических единиц AST.
        :param source_code: Строка с Python-подобным исходным кодом.
        :return: Compiled `CodeType` object for execution.
        """
        if not all((source_code, isinstance(source_code, str))):
            raise ScriptCompileException("Значение входного параметра для компиляции должно быть непустой строкой")

        try:
            ast_tree: ast.Module = ast.parse(source_code)
            self.__ast_checkup_traversal(ast_tree)
            compiled_code: CodeType = compile(ast_tree, mode=settings.MODE, filename=settings.FILENAME_PLACEHOLDER)
        except Exception as exc:
            raise ScriptCompileException(f"Ошибка компиляции скрипта: {exc}")

        self.__compiled_code = compiled_code
        self.__source_code = source_code.splitlines()
        return compiled_code

    def run(self) -> Any:
        """
        Отправляет скомпилированный ранее код (методом `compile`) на исполнение.
        :raise ScriptCompileException: Если код не был предварительно скомпилирован в `.compile(code)`.
        :raise ScriptRuntimeException: Если во время исполнения кода скрипта возникла ошибка.
        :return: Результат выполнения скрипта, складированный в зарезервированную переменную (имя в `RESULT_VARNAME`).
                 По умолчанию возвращает `None`.
        """
        if self.__compiled_code is None:
            raise ScriptCompileException("Код должен быть скомпилирован перед исполнением. "
                                         "Для начала выполните метод `.compile(code)`.")
        try:
            exec(self.__compiled_code, self.__locals, self.__globals)
        except Exception as exc:
            err_msg = self.__collect_script_error_location(exc)
            raise ScriptRuntimeException(err_msg)

        return self.__globals.get(settings.RESULT_VARNAME)

    def __ast_checkup_traversal(self, node: ast.AST) -> None:
        """
        Рекурсивный обход AST-дерева и проверка допустимости используемых синтаксических единиц.
        Возбуждает исключение `CompileException` в случае наличия недопустимых синтаксических единиц.
        :param node: Узел дерева AST.
        :raise CompileException: Если `node` (или один из её потомков) является недопустимой синтаксической единицей.
        """
        # Проверка допустимости синтаксических единиц.
        if type(node) not in settings.ALLOWED_AST_NODES:
            node_name: str = type(node).__name__
            raise ScriptCompileException(f"недопустимая синтаксическая единица: `{node_name}`")

        for node in ast.iter_child_nodes(node):
            self.__ast_checkup_traversal(node)

    def __collect_script_error_location(self, occurred_exc: Exception) -> str:
        """
        Собирает информацию о месте возникновения ошибки в скрипте.
        :param occurred_exc: Возникшее исключение.
        :return: Строка с информацией о месте возникновения ошибки в скрипте.
        """
        err_msg = f"Ошибка выполнения скрипта: {occurred_exc}"
        for filename, line, _, _ in traceback.extract_tb(occurred_exc.__traceback__):
            if filename == settings.FILENAME_PLACEHOLDER:
                err_location: str = "\n".join(
                    line
                    for line in (
                        f"  File '{filename}', line {line}",
                        # Предшествующая строка (если есть).
                        f"       {line - 1}. {self.__source_code[line - 2]}" if line > 1 else "",
                        # Строчка, где произошла ошибка.
                        f">>>    {line}. {self.__source_code[line - 1]}",
                        # Следующая строка (если есть).
                        f"       {line + 1}. {self.__source_code[line]}" if line < len(self.__source_code) else "",
                    )
                    if line
                )
                return "\n".join((err_msg, "Контекст:", err_location))

        return err_msg
