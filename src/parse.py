def parse_sexpr(spec):
    """parse string specification into a s-expression"""

    def parse_sexpr_(tokens):
        "a simple push/pop routine to parse into s-expression"
        if len(tokens) == 0:
            return
        token = tokens.pop(0)
        if "(" == token:
            L = []
            while tokens[0] != ")":
                L.append(parse_sexpr_(tokens))
            tokens.pop(0)  # pop off ')'
            return tuple(L)
        elif ")" == token:
            raise SyntaxError("unexpected )")
        else:
            return token

    try:
        result = list()
        s = spec.strip().replace("(", " ( ").replace(")", " ) ").split()
        sexpr = parse_sexpr_(s)
        if sexpr:
            result.append(sexpr)
        # return result
        return sexpr
    except:
        raise RuntimeError("Could not parse s-expressions")
