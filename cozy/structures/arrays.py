from cozy.common import declare_case
from cozy.syntax import Type, Exp, Stm

TArray = declare_case(Type, "TArray", ["t"])
EArrayCapacity = declare_case(Exp, "EArrayCapacity", ["e"])
EArrayGet = declare_case(Exp, "EArrayGet", ["a", "i"])
SArrayAlloc = declare_case(Stm, "SArrayAlloc", ["a", "capacity"])
SArrayReAlloc = declare_case(Stm, "SArrayReAlloc", ["a", "new_capacity"])
SEnsureCapacity = declare_case(Stm, "SEnsureCapacity", ["a", "capacity"])
