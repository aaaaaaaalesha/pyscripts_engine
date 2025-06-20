import logging
from dataclasses import dataclass
from datetime import date, datetime

from scripts_engine.exceptions import ScriptCompileException, ScriptRuntimeException
from scripts_engine.engine import PyScriptsEngine

# Пример.
if __name__ == "__main__":
    @dataclass
    class User:
        first_name = "Aleksey"
        last_name = "Aleksandrov"
        birthday = date(2001, 5, 21)
        deleted_at = None
        updated_at = datetime.now()


    @dataclass
    class Document:
        deleted_at = None
        updated_at = datetime.now()
        creator = User()
        version = 1

        def save(self):
            self.version += 1


    wf_executor = PyScriptsEngine(Document(), type_object=3)

    # Пример скрипта
    script = """
# Объявление локальных переменных.
a = 1  
a *= 1  
print(f"{a=}")

b = []
b.append(a)

c = {a: b}
print(c)

if type_object == 1:
    result = False
elif type_object == 3:
    if object.deleted_at is None and object.updated_at < datetime.now():
        result = True
else:
    a /= 3

print(f"{a=}")  

for i in range(10):
    print(i, Decimal("3.14") + i ** Decimal(0.01))
"""
    try:
        wf_executor.compile(script)
    except ScriptCompileException as exc:
        logging.exception(exc)
        exit(1)

    result = None
    try:
        result = wf_executor.run()
    except ScriptRuntimeException as exc:
        logging.error(exc)

    print(f"{result=}")
