import logging

import torch

from utils import get_operator_and_operands

unary_ops = {
    "sqrt": lambda x: x**0.5,
}

binary_ops = {
    "=": lambda x, y: (x - y) ** 2,
    ">=": lambda x, y: torch.relu(y - x),
    "+": lambda x, y: x + y,
    "/": lambda x, y: x / y,
    "*": lambda x, y: x * y,
}


def sexpr2loss(sexpr, variable_mgr):
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
        return float(float_value)
    elif isinstance(sexpr, str):  # the sexpr is an id
        return get_value(sexpr, variable_mgr)
    else:  # the sexpr is, well, a "normal" sexpr
        symbol = sexpr[0]
        if symbol in unary_ops:
            _operator, (_op,) = get_operator_and_operands(sexpr)
            logging.debug("op {} op1 {}".format(_operator, _op))
            _operator_func = unary_ops[_operator]
            return _operator_func(sexpr2loss(_op, variable_mgr))
        if symbol in binary_ops:
            _operator, (_op1, _op2) = get_operator_and_operands(sexpr)
            logging.debug("op {} op1 {} op2 {}".format(_operator, _op1, _op2))
            _operator_func = binary_ops[_operator]
            return _operator_func(
                sexpr2loss(_op1, variable_mgr),
                sexpr2loss(_op2, variable_mgr),
            )
        logging.error("operator {}, not supported".format(symbol))
        assert 0  # should not reach here. Need to check if the specified operator is supported
    return


class Optim_solver:
    def __init__(self, builder):
        variables, constraints_sexpr = builder.variables, builder.constraints

        # the variable manager controls the parameters and its values.
        length = len(variables)
        self.pytorch_variables = torch.rand((length,), requires_grad=True)
        id2idx = {v.id: idx for idx, v in enumerate(variables)}
        self.variable_mgr = {
            v.id: self.pytorch_variables[id2idx[v.id]] for v in variables
        }
        # store the constraint expression as it is, will be used to construct it.
        # while in the soft loss approach we construct a computation graph, here
        # we simply construct a constraint-graph, a AND node along with a set of
        # clauses (constraints)
        self.constraints_sexpr = constraints_sexpr

    def solve(self):
        optimizer = torch.optim.SGD([self.pytorch_variables], lr=0.01, momentum=0.9)

        # iterative optimization.
        for i in range(100):
            optimizer.zero_grad()
            losses = [sexpr2loss(c, self.variable_mgr) for c in self.constraints_sexpr]
            # based on the value of parameters from the variable manager
            # construct all the losses (convert the constraint into soft loss)
            losses = torch.hstack(losses).sum()
            losses.backward()
            optimizer.step()

        result = {}
        for v_id in self.variable_mgr:
            var = self.variable_mgr[v_id]
            realized_value = var
            result[v_id] = realized_value
            assert realized_value is not None
            logging.info(
                "variable {} under id {} should be {} ".format(
                    var, v_id, float(realized_value)
                )
            )

        return result
