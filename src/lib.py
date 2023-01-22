import logging
import pprint
from pprint import pprint as pr

from parse import parse_sexpr


def set_env():
    level = getattr(logging, "INFO", None)
    if not isinstance(level, int):
        raise ValueError("level {} not supported".format(args.verbose))
    handler1 = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(levelname)s - %(filename)s - %(asctime)s - %(message)s"
    )
    handler1.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler1)
    logger.setLevel(level)


if __name__ == "__main__":
    set_env()

    txt_spec = """
    (define root
        (Canvas 
            (= width 256) 
            (= height 256)
            (define a Circle)
            (define b Rect)
            (= (get a center_x) (get b center_x))
            (= (get a center_y) (get b center_y))
            (= (get a radius) (/ (get . width) 4))
            (= (get b width) (get b height))
            (= (get b width) (*  (get a radius) (sqrt 2))))
    )
    """

    def build(spec):
        sexpr = parse_sexpr(spec)
        indented_sexpr = pprint.pformat(sexpr, indent=2)
        logging.info("the entire spec is:\n{}".format(indented_sexpr))

        from interpret_base import interpret

        builder = interpret(sexpr)
        return builder

    builder = build(txt_spec)

    from backend import smt
    smt_solver = smt.SMT_solver(builder)
    result = smt_solver.solve()

    # todo: add the routine to expor the result and render into SVG
    # save_svg(result) # parse and render as save as svg
    # save_png(result) # parse and render as save as png
