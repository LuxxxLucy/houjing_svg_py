# Define a set of prior knowledge about the geometrical shapes
# Each shape starts with a unique identifier ("Circle", "Rect", etc)
# then comes the fields (attributes of this shape)
# as well as the constraints and the inherit relation.
#
# For example, Canvas is a special Rect, so it inherits from Rect,
# and so has the same attribues as Rect ("width", etc).
# More than that, we know by prior knowledge that the x and y-
# coordinates of the Canvas must be zero. So the Canvas natually
# comes with these two constraints, without the need for human to
# provide additionally

# Note:
# 1. field name should start with a lowercase letter.

_arithmetic_knowledge = {
    "Float": {},
    "NonnegativeFloat": {
        "inherit": ["Float"],
        "constraints": [
            """
            (>= . 0)
            """,
        ],
    },
}
_geometry_knowledge = {
    "Circle": {
        "fields": {"x": "Float", "y": "Float", "radius": "NonnegativeFloat"},
        "properties": {
            "center_x": """
                        (get . x)
                        """,
            "center_y": """
                        (get . y)
                        """,
        },
        "constraints": [],
    },
    "Rect": {
        "fields": {
            "x": "Float",
            "y": "Float",
            "width": "NonnegativeFloat",
            "height": "NonnegativeFloat",
        },
        "properties": {
            "center_x": """
                        (+ (/ width 2) x)
                        """,
            "center_y": """
                        (+ (/ height 2) y)
                        """,
        },
        "constraints": [],
    },
    "Canvas": {
        "inherit": ["Rect"],
        "fields": {},
        "constraints": [
            "(= x 0)", 
            "(= y 0)", 
        ]
    },
}

_knowledge = {}
_knowledge.update(_arithmetic_knowledge)
_knowledge.update(_geometry_knowledge)

_supported_geometry_objects = list(_geometry_knowledge.keys())