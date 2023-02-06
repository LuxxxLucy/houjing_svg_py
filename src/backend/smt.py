import logging

from pysmt.shortcuts import Symbol
from pysmt.shortcuts import Equals, And, Min, Max, get_model
from pysmt.shortcuts import Plus, Pow
from pysmt.shortcuts import GT, LT

from pysmt.shortcuts import Real, Int
from pysmt.shortcuts import REAL, INT

from utils import get_operator_and_operands


unary_ops = {
    # "sqrt": lambda x : x**0.5,
    "sqrt": lambda x: Pow(x, Real(0.5)),
}

binary_ops = {
    "=": lambda x, y: Equals(x, y),
    "==": Equals,
    ">=": lambda x, y: GT(x, y),
    "+": lambda x, y: x + y,
    "/": lambda x, y: x / y,
    "*": lambda x, y: x * y,
}


def sexpr2smt_formula(sexpr, variable_mgr):
    def get_value(sexpr, variable_mgr):
        _id = sexpr
        if _id in variable_mgr:
            return variable_mgr[_id]
        logging.info(
            "getting variable error. Variable of id {} is not defined.".format(_id)
        )
        assert 0  # should not reach here. Need to check if the specified operator is supported

    if isinstance(sexpr, float):  # the sexpr is just a float value
        float_value = sexpr
        return Real(float_value)
    elif isinstance(sexpr, str):  # the sexpr is an id
        return get_value(sexpr, variable_mgr)
    else:  # the sexpr is, well, a "normal" sexpr
        symbol = sexpr[0]
        if symbol in unary_ops:
            _operator, (_op,) = get_operator_and_operands(sexpr)
            logging.debug("op {} op1 {}".format(_operator, _op))
            _operator_func = unary_ops[_operator]
            return _operator_func(sexpr2smt_formula(_op, variable_mgr))
        if symbol in binary_ops:
            _operator, (_op1, _op2) = get_operator_and_operands(sexpr)
            logging.debug("op {} op1 {} op2 {}".format(_operator, _op1, _op2))
            _operator_func = binary_ops[_operator]
            return _operator_func(
                sexpr2smt_formula(_op1, variable_mgr),
                sexpr2smt_formula(_op2, variable_mgr),
            )
        logging.error("operator {}, not supported".format(symbol))
        assert 0  # should not reach here. Need to check if the specified operator is supported
    return


class SMT_solver:
    def __init__(self, builder):
        variables, constraints_sexpr = builder.variables, builder.constraints

        # the variable manager controls the parameters and its values.
        self.variable_mgr = {v.id: Symbol(v.id, REAL) for v in variables}
        # store the constraint expression as it is, will be used to construct it.
        # while in the soft loss approach we construct a computation graph, here
        # we simply construct a constraint-graph, a AND node along with a set of
        # clauses (constraints)
        self.constraints_sexpr = constraints_sexpr

    def solve(self):
        # based on the value of parameters from the variable manager
        # construct all constraints.
        constraints = [
            sexpr2smt_formula(c, self.variable_mgr) for c in self.constraints_sexpr
        ]
        model = get_model(And(constraints))

        assert model is not None
        result = {}
        for v_id in self.variable_mgr:
            var = self.variable_mgr[v_id]
            realized_value = model.get_py_value(var)
            result[v_id] = realized_value
            assert realized_value is not None
            logging.info(
                "variable {} under id {} should be {} ".format(
                    var, v_id, float(realized_value)
                )
            )

        return result
