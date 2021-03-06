"""Well-formedness tests for Cozy expressions."""

import itertools

from cozy.common import typechecked, OrderedSet
from cozy.typecheck import is_collection, is_scalar
from cozy.target_syntax import *
from cozy.syntax_tools import pprint, free_vars
from cozy.solver import ModelCachingSolver
from cozy.pools import RUNTIME_POOL, STATE_POOL
from cozy.opts import Option
from cozy.structures import extension_handler
from cozy.contexts import Context, RootCtx, shred

class ExpIsNotWf(Exception):
    def __init__(self, e, offending_subexpression, reason):
        super().__init__(reason)
        self.e = e
        self.offending_subexpression = offending_subexpression
        self.reason = reason

def exp_wf_nonrecursive(solver, e : Exp, context : Context, pool = RUNTIME_POOL, assumptions : Exp = T):
    state_vars = OrderedSet(v for v, p in context.vars() if p == STATE_POOL)
    args       = OrderedSet(v for v, p in context.vars() if p == RUNTIME_POOL)
    assumptions = EAll([assumptions, context.path_condition()])

    h = extension_handler(type(e))
    if h is not None:
        msg = h.check_wf(e, state_vars=state_vars, args=args, pool=pool, assumptions=assumptions, is_valid=solver.valid)
        if msg is not None:
            raise ExpIsNotWf(e, e, msg)
        return
    at_runtime = pool == RUNTIME_POOL
    if isinstance(e, EStateVar) and not at_runtime:
        raise ExpIsNotWf(e, e, "EStateVar in state pool position")
    if isinstance(e, EVar):
        if at_runtime and e in state_vars:
            raise ExpIsNotWf(e, e, "state var at runtime")
        elif not at_runtime and e in args:
            raise ExpIsNotWf(e, e, "arg in state exp")

@typechecked
def exp_wf(e : Exp, context : Context, pool = RUNTIME_POOL, assumptions : Exp = T, solver = None):
    """
    Returns True or throws exception indicating why `e` is not well-formed.
    """
    if solver is None:
        solver = ModelCachingSolver(vars=[], funcs={})
    for x, ctx, p in shred(e, context, pool):
        try:
            exp_wf_nonrecursive(solver, x, ctx, p, assumptions=ctx.adapt(assumptions, context))
        except ExpIsNotWf as exc:
            raise ExpIsNotWf(e, x, exc.reason)
    return True
