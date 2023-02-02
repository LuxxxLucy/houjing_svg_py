
def save_svg(obj, path=None):
    """
    explicit params
        obj: a json-like dictionary
        path
    
    implicit params:
        knowledge about how to translate the object into SVG
    """

    svg_str = obj2svg(obj)
    # save svg_str into a local file.
    pass

