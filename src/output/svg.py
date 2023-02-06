"""
In SVG knowledge, each obj type has a list "attributes" which contains key-value pairs as (attribute_name : default_value)
as well as a str_rep for its SVG string
"""

import svgwrite
from svgwrite.shapes import *


def save_svg(builder, ret, path="test.svg"):
    """
    explicit params
        obj: a json-like dictionary
        path

    implicit params:
        knowledge about how to translate the object into SVG
    """

    import knowledge

    print("Supported geometry types are", knowledge._supported_geometry_objects)
    objs = []
    for v in builder.variables:
        if v.type in knowledge._supported_geometry_objects:
            print(v.type, v.id)
            objs.append(v)

    def get_value(dic, _id, _field):
        x = "/".join([_id, _field])
        x = float(dic[x])
        return x

    for obj in objs:
        if obj.type == "Canvas":
            w = get_value(ret, obj.id, "width")
            h = get_value(ret, obj.id, "height")
            dwg = svgwrite.Drawing("test.svg", profile="tiny", height=h, width=w)
            break

    for obj in objs:
        if obj.type == "Circle":
            x = get_value(ret, obj.id, "x")
            y = get_value(ret, obj.id, "y")
            r = get_value(ret, obj.id, "radius")
            dwg.add(
                Circle(
                    center=(x, y),
                    r=r,
                    stroke=svgwrite.rgb(10, 10, 16, "%"),
                    fill="none",
                )
            )
            continue
        elif obj.type == "Rect":
            x = get_value(ret, obj.id, "x")
            y = get_value(ret, obj.id, "y")
            w = get_value(ret, obj.id, "width")
            h = get_value(ret, obj.id, "height")
            dwg.add(
                Rect(
                    insert=(x, y),
                    size=(w, h),
                    stroke=svgwrite.rgb(10, 10, 16, "%"),
                    fill="none",
                )
            )

    dwg.save()
    return
