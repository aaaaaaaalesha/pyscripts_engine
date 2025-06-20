class BaseScriptException(Exception):
    pass


class ScriptCompileException(BaseScriptException):
    pass


class ScriptRuntimeException(BaseScriptException):
    pass
