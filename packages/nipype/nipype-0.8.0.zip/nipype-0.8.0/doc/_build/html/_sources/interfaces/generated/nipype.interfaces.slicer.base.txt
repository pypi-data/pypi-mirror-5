.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.base
======================


.. _nipype.interfaces.slicer.base.SlicerCommandLine:


.. index:: SlicerCommandLine

SlicerCommandLine
-----------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/slicer/base.py#L3>`__

Wraps command **None**


Inputs::

        [Mandatory]
        terminal_output: ('stream' or 'allatonce' or 'file' or 'none')
                Control terminal output

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        None
