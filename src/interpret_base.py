import logging
import string

from utils import get_operator_and_operands
from parse import parse_sexpr

from knowledge import _knowledge


class Variable:
    # _const = False # true if does not need to be infer this variable
    # _need_infer = False
    # _realized = False # set to true after the inference is done
    def __init__(self, ID_list, type):
        # ID is a list of identifiers. such as ["root", "a", "width"]
        # the joined str uniquely determines a variable ID, in this case "root/a/width"
        self._id_list = ID_list
        self._type = type

    def __str__(self):
        return "ID: {} Type:{}".format(self.id, self._type)

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        # return self._id_list
        return "/".join(self._id_list)


class Builder:
    def __init__(self):
        self.variables = []
        self.intermediate_variables = []
        self.constraints = []

    def id2type(self, id):
        # return the type of the object specified by the ID
        for v in self.variables:
            if v.id == id:
                return v.type

    def display(self):
        logging.info("Builder display start")
        for v in self.variables:
            logging.info("variable: {}".format(v))
        for c in self.constraints:
            logging.info("constraints: {}".format(c))
        logging.info("Builder display end")


class Context:
    _scope = [""]
    _builder = None  # Link to the global builder

    def __init__(self, builder):
        self._builder = builder
        return

    @property
    def current_scope(self):
        return [s for s in self._scope if s != "."]
        # return self._scope

    @property
    def current_scope_as_str(self):
        return "/".join(self.current_scope)

    def push_scope(self, name):
        self._scope.append(name)
        logging.debug("scope push, current is {}".format(self.current_scope))

    def pop_scope(self):
        self._scope.pop()
        logging.debug("scope pop, current is {}".format(self.current_scope))

    def get_unique_id(self, id):
        if id[0] == "/":
            # already unique ID (absolute path-like)
            return id
        elif id == ".":
            return self.current_scope_as_str
        elif id[0] == ".":
            # todo: need to handle relative path
            return
        else:
            print(self.current_scope, id)
            return "/".join(self.current_scope + [id])


def register_variable(ctx, _id, _type):
    v = Variable(ctx.current_scope + [_id], _type)
    logging.debug('register variable: "{}"'.format(v))
    ctx._builder.variables.append(v)


def register_constraint(ctx, c):
    logging.debug('register constraint: "{}"'.format(c))
    ctx._builder.constraints.append(c)


def get_all_fields(knowledge, type):
    # find all fields that needs to be registered
    all_fields = {}
    if "inherit" in knowledge[type]:
        for inherited_parent in knowledge[type]["inherit"]:
            inherited_parent_fields = get_all_fields(knowledge, inherited_parent)
            all_fields.update(inherited_parent_fields)
    if "fields" in knowledge[type]:
        all_fields.update(knowledge[type]["fields"])
    return all_fields


def get_all_properties(knowledge, type):
    # find all fields that needs to be registered
    all_properties = {}
    if "inherit" in knowledge[type]:
        for inherited_parent in knowledge[type]["inherit"]:
            inherited_parent_properties = get_all_properties(
                knowledge, inherited_parent
            )
            all_properties.update(inherited_parent_properties)
    if "properties" in knowledge[type]:
        all_properties.update(knowledge[type]["properties"])
    return all_properties


def get_all_prior_constraints(knowledge, type):
    print("getting all cons for ", type)
    # find all constraints that needs to be registered
    all_constraints = []
    if "inherit" in knowledge[type]:
        for inherited_parent in knowledge[type]["inherit"]:
            inherited_parent_constraints = get_all_prior_constraints(
                knowledge, inherited_parent
            )
            all_constraints += inherited_parent_constraints
    if "constraints" in knowledge[type]:
        all_constraints += knowledge[type]["constraints"]
    print("they are", all_constraints)
    return [parse_sexpr(c) for c in all_constraints]


def _handle_get(ctx, sexpr):
    _operator, (_id, _field) = get_operator_and_operands(sexpr)
    assert _operator == "get"
    _uid = ctx.get_unique_id(_id)
    obj_type = ctx._builder.id2type(_uid)  # the type of the object with the id

    all_fields = get_all_fields(_knowledge, obj_type)
    if _field in all_fields:
        result = "{}/{}".format(_uid, _field)
        return result

    properties = get_all_properties(_knowledge, obj_type)
    if _field in properties:
        expr = parse_sexpr(properties[_field])
        ctx.push_scope(_id)
        ret = expand_sexpr(ctx, expr)
        ctx.pop_scope()
        return ret

    logging.error("error!!!")
    return "Error"


def _handle_define(ctx, sexpr):
    _operator, (_id, _obj) = get_operator_and_operands(sexpr)
    assert _operator == "define"
    if isinstance(_obj, str):
        _type, _statements = _obj, []
    else:
        _type, _statements = get_operator_and_operands(_obj)
    register_variable(ctx, _id, _type)
    if _type in _knowledge:
        ctx.push_scope(_id)

        all_constraints = get_all_prior_constraints(_knowledge, _type)
        for constraint in all_constraints:
            interpret_sexpr(ctx, constraint)

        all_fields = get_all_fields(_knowledge, _type)
        for field in all_fields:
            field_type = all_fields[field]
            register_variable(ctx, field, field_type)
            all_constraints = get_all_prior_constraints(_knowledge, field_type)
            for constraint in all_constraints:
                ctx.push_scope(field)
                interpret_sexpr(ctx, constraint)
                ctx.pop_scope()

        for statement in _statements:
            interpret_sexpr(ctx, statement)

        ctx.pop_scope()
    else:
        logging.info('{}: unsupported (in statement "{}")'.format(_type, sexpr))
        quit()


_language_keyword_handle_routines = {
    "define": _handle_define,
    "get": _handle_get,
}


def is_str_symbol_id(s):
    if s == ".":
        return True  # refer to itself in the current scope
    if s[0] in string.ascii_lowercase:
        return True  # is an ID if starts with lowercase letter
    return False


def expand_sexpr(ctx, sexpr):
    logging.debug("sexpr is {}".format(sexpr))
    # expand the IDs in the sexpr to unique ID
    # assume all operator takes two input argument (binary)
    if isinstance(sexpr, str):
        if is_str_symbol_id(sexpr):
            return ctx.get_unique_id(sexpr)
        else:
            return float(sexpr)
    _operator, _ops = get_operator_and_operands(sexpr)
    if _operator == "get":
        result = _handle_get(ctx, sexpr)
    else:
        result = [_operator] + [expand_sexpr(ctx, op) for op in _ops]
    return result


def _handle_constraint(ctx, sexpr):
    c = expand_sexpr(ctx, sexpr)
    register_constraint(ctx, c)


# _constraint_handle_routines = {"=": _handle_constraint, ">=": _handle_constraint}

_handle_routines = {}
_handle_routines.update(_language_keyword_handle_routines)
# _handle_routines.update(_constraint_handle_routines)


def interpret_sexpr(ctx: Context, sexpr):
    symbol = sexpr[0]
    if symbol in _handle_routines:
        ret = _handle_routines[symbol](ctx, sexpr)
    else:
        ret = _handle_constraint(ctx, sexpr)

    return ret


def interpret(sexpr):
    builder = Builder()
    building_ctx = Context(builder)
    interpret_sexpr(building_ctx, sexpr)

    builder.display()

    # forward reparameterize, eliminate some trival constraints
    # builder.reparameterize()
    return builder
