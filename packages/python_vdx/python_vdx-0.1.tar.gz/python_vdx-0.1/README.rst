==================
PYTHON VDX PACKAGE
==================

1. Install
----------

::

    pip install python_vdx

2. Workspace creation
---------------------

::

    from vdx.diagramm import Diagramm
    from vdx.shapes import Point

    dia = Diagramm(top=Point(1, 11))


Note: Point (1, 11) is default point. It points to the upper left corner
of visio page. Also, you should remember that all objects craeted on the
diagramm placed in accordance with the point. So, Shape(startPoint=Point(2, 0))
will be places at Point(3, 11).   

3. Adding element on the diagramm
---------------------------------

::

    ...
    from vdx.shapes import EPCFunction  # EPCFunction is function object in ECP diagramm


    ## Add several "EPCFunction" objects with the same coordinates
    dia.append_shape(EPCFunction())
    dia.append_shape(EPCFunction())
    dia.append_shape(EPCFunction())
    dia.append_shape(EPCFunction())

4. Save the diagramm to a file.
-------------------------------

::

    ....

    dia.save('some_path_to_save.vdx')


Supported objects (at the moment only EPC objects are supported)
----------------------------------------------------------------

- Function (EPC)
- Event (EPC)
-  Organization Unit (EPC)
-  Information Material (EPC)
-  Main process (EPC)
-  Component (EPC)
-  Enterprise area (EPC)
-  Process group
-  XOR (EPC)
-  OR (EPC)
-  AND (EPC)
-  Dynamic connector (EPC)
