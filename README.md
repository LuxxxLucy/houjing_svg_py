# Houjing

declarative figure making with simple geometric primitives


Given a spec
```
txt_spec = """
    (define root
        (Canvas 
            (= width 256) 
            (= height 256)
            (define a Circle)
            (define b Rect)
            (= (get a center_x) (get b center_x))
            (= (get a center_y) (get b center_y))
            (= (get a center_x) (get . center_x))
            (= (get a center_y) (get . center_y))
            (= (get a radius) (/ (get . width) 4))
            (= (get b width) (get b height))
            (= (get b width) (*  (get a radius) (sqrt 2))))
    )
    """
```

the program will construct a graph of related variables and solve it by a SMT solver backend. The result can be exported to SVG.

![](./test.svg)
