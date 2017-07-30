from cozy.target_syntax import *
from cozy.syntax_tools import BottomUpRewriter, cse
from cozy.evaluation import construct_value

class _V(BottomUpRewriter):
    def visit_EBinOp(self, e):
        if e.op == BOp.In:
            if isinstance(e.e2, EBinOp) and e.e2.op == "+":
                return self.visit(EAny([EIn(e.e1, e.e2.e1), EIn(e.e1, e.e2.e2)]))
            elif isinstance(e.e2, EUnaryOp) and e.e2.op == UOp.Distinct:
                return self.visit(EIn(e.e1, e.e2.e))
            elif isinstance(e.e2, EFilter):
                return self.visit(EAll([EIn(e.e1, e.e2.e), e.e2.p.apply_to(e.e1)]))
        return EBinOp(self.visit(e.e1), e.op, self.visit(e.e2)).with_type(e.type)
    def visit_EMapGet(self, e):
        if isinstance(e.map, EMakeMap2):
            return self.visit(ECond(EIn(e.key, e.map.e),
                e.map.value.apply_to(e.key),
                construct_value(e.type)).with_type(e.type))
        return EMapGet(self.visit(e.map), self.visit(e.key)).with_type(e.type)

simplify = _V().visit
