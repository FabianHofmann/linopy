#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 13:33:55 2022.

@author: fabian
"""

from functools import cached_property

import numpy as np
import pandas as pd

from linopy import expressions


def create_vector(indices, values, fill_value=np.nan, shape=None):
    """Create a vector of a size equal to the maximum index plus one."""
    if shape is None:
        shape = max(indices) + 1
    vector = np.full(shape, fill_value)
    vector[indices] = values
    return vector


class MatrixAccessor:
    """
    Helper class to quickly access model related vectors and matrices.
    """

    def __init__(self, model):
        self._parent = model

    def clean_cached_properties(self):
        "Clear the cache for all cached properties of an object"

        for cached_prop in ["flat_vars", "flat_cons", "sol", "dual"]:
            # check existence of cached_prop without creating it
            if cached_prop in self.__dict__:
                delattr(self, cached_prop)

    @cached_property
    def flat_vars(self):
        m = self._parent
        return m.variables.flat

    @cached_property
    def flat_cons(self):
        m = self._parent
        return m.constraints.flat

    @property
    def vlabels(self):
        "Vector of labels of all non-missing variables."
        df = self.flat_vars
        return create_vector(df.key, df.labels, -1)

    @property
    def vtypes(self):
        "Vector of types of all non-missing variables."
        m = self._parent
        df = self.flat_vars
        specs = []
        for name in m.variables:
            if name in m.binaries:
                val = "B"
            elif name in m.integers:
                val = "I"
            else:
                val = "C"
            specs.append(pd.Series(val, index=m.variables[name].flat.labels))

        ds = pd.concat(specs)
        ds = df.set_index("key").labels.map(ds)
        return create_vector(ds.index, ds.values, fill_value="")

    @property
    def lb(self):
        "Vector of lower bounds of all non-missing variables."
        df = self.flat_vars
        return create_vector(df.key, df.lower)

    @cached_property
    def sol(self):
        "Vector of solution values of all non-missing variables."
        if not self._parent.status == "ok":
            raise ValueError("Model is not optimized.")
        if "solution" not in self.flat_vars:
            del self.flat_vars  # clear cache
        df = self.flat_vars
        return create_vector(df.key, df.solution, fill_value=np.nan)

    @cached_property
    def dual(self):
        "Vector of dual values of all non-missing constraints."
        if not self._parent.status == "ok":
            raise ValueError("Model is not optimized.")
        if "dual" not in self.flat_cons:
            del self.flat_cons  # clear cache
        df = self.flat_cons
        if "dual" not in df:
            raise AttributeError(
                "Underlying is optimized but does not have dual values stored."
            )
        return create_vector(df.key, df.dual, fill_value=np.nan)

    @property
    def ub(self):
        "Vector of upper bounds of all non-missing variables."
        df = self.flat_vars
        return create_vector(df.key, df.upper)

    @property
    def clabels(self):
        "Vector of labels of all non-missing constraints."
        df = self.flat_cons
        if df.empty:
            return np.array([], dtype=int)
        return create_vector(df.key, df.labels, fill_value=-1)

    @property
    def A(self):
        "Constraint matrix of all non-missing constraints and variables."
        m = self._parent
        A = m.constraints.to_matrix(filter_missings=False)
        return A[self.clabels][:, self.vlabels] if A is not None else None

    @property
    def sense(self):
        "Vector of senses of all non-missing constraints."
        df = self.flat_cons
        return create_vector(df.key, df.sign.astype(np.dtype("<U1")), fill_value="")

    @property
    def b(self):
        "Vector of right-hand-sides of all non-missing constraints."
        df = self.flat_cons
        return create_vector(df.key, df.rhs)

    @property
    def c(self):
        "Vector of objective coefficients of all non-missing variables."
        m = self._parent
        ds = m.objective.flat
        if isinstance(m.objective.expression, expressions.QuadraticExpression):
            ds = ds[(ds.vars1 == -1) | (ds.vars2 == -1)]
            ds["vars"] = ds.vars1.where(ds.vars1 != -1, ds.vars2)

        vars = ds.vars.map(self.flat_vars.set_index("labels").key)
        shape = self.flat_vars.key.max() + 1
        return create_vector(vars, ds.coeffs, fill_value=0.0, shape=shape)

    @property
    def Q(self):
        "Matrix objective coefficients of quadratic terms of all non-missing variables."
        m = self._parent
        if m.is_linear:
            return None

        return m.objective.expression.to_matrix()[self.vlabels][:, self.vlabels]
