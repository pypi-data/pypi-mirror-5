.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.dynamic_slicer
=========================


.. _nipype.interfaces.dynamic_slicer.SlicerCommandLine:


.. index:: SlicerCommandLine

SlicerCommandLine
-----------------

`Link to code <http://github.com/nipy/nipype/tree/9595f272aa4086ea28f7534a8bd05690f60bf6b8/nipype/interfaces/dynamic_slicer.py#L14>`__

Wraps command **Slicer3**

Experimental Slicer wrapper. Work in progress.

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
        module: (a string)
                name of the Slicer command line module you want to use

Outputs::

        None
