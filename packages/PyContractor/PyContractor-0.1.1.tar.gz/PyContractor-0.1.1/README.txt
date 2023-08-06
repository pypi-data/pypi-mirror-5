PyContractor
============

Introduction
------------

Design by contract is a methodology of software design. It prescribes
that software designers should define formal, precise and verifiable
interface specifications for software components, which extend the
ordinary definition of abstract data types with preconditions,
postconditions and invariants. These specifications are referred to as
"contracts", in accordance with a conceptual metaphor with the
conditions and obligations of business contracts.

Usage
-----

When using this library, just create a class and define the
preconditions, postconditions or invariants in the method, or in a
separate function.

For ex.

::

        from PyContractor import PyContractor

        def division(self, a, b):
            PyContractor.require(b != 0, "Divisor must be non-zero")

        division(2/0)

This tiny library just gives you a start to know this methodology and
it's mainly focused for educational purposes.
