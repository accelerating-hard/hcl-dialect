# Copyright HeteroCL authors. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#  Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
#  See https://llvm.org/LICENSE.txt for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

try:
  from ..ir import *
except ImportError as e:
  raise RuntimeError("Error loading imports from extension module") from e

from typing import Any, Optional, Sequence, Union
from ._ods_common import get_op_result_or_value as _get_op_result_or_value, get_op_results_or_values as _get_op_results_or_values

class ForOp:
  """Specialization for the SCF for op class."""

  def __init__(self,
               lower_bound,
               upper_bound,
               step,
               iter_args: Optional[Union[Operation, OpView,
                                         Sequence[Value]]] = None,
               
               *,
               reduction=None,
               name="",
               stage="",
               loc=None,
               ip=None):
    """Creates an SCF `for` operation.

    - `lower_bound` is the value to use as lower bound of the loop.
    - `upper_bound` is the value to use as upper bound of the loop.
    - `step` is the value to use as loop step.
    - `iter_args` is a list of additional loop-carried arguments or an operation
      producing them as results.
    """
    if iter_args is None:
      iter_args = []
    iter_args = _get_op_results_or_values(iter_args)

    attributes = {}
    if name != "":
      attributes["loop_name"] = name
    if stage != "":
      attributes["op_name"] = stage
    if reduction:
      attributes["reduction"] = reduction

    results = [arg.type for arg in iter_args]
    super().__init__(
        self.build_generic(
            regions=1,
            results=results,
            operands=[
                _get_op_result_or_value(o)
                for o in [lower_bound, upper_bound, step]
            ] + list(iter_args),
            attributes=attributes,
            loc=loc,
            ip=ip))
    self.regions[0].blocks.append(IndexType.get(), *results)

  @property
  def body(self):
    """Returns the body (block) of the loop."""
    return self.regions[0].blocks[0]

  @property
  def induction_variable(self):
    """Returns the induction variable of the loop."""
    return self.body.arguments[0]

  @property
  def inner_iter_args(self):
    """Returns the loop-carried arguments usable within the loop.

    To obtain the loop-carried operands, use `iter_args`.
    """
    return self.body.arguments[1:]


class IfOp:
  """Specialization for the SCF if op class."""

  def __init__(self,
               cond,
               results_=[],
               *,
               hasElse=False,
               loc=None,
               ip=None):
    """Creates an SCF `if` operation.

    - `cond` is a MLIR value of 'i1' type to determine which regions of code will be executed.
    - `hasElse` determines whether the if operation has the else branch.
    """
    operands = []
    operands.append(cond)
    results = []
    results.extend(results_)
    super().__init__(
        self.build_generic(
            regions=2,
            results=results,
            operands=operands,
            loc=loc,
            ip=ip))
    self.regions[0].blocks.append(*[])
    if hasElse:
        self.regions[1].blocks.append(*[])

  @property
  def then_block(self):
    """Returns the then block of the if operation."""
    return self.regions[0].blocks[0]

  @property
  def else_block(self):
    """Returns the else block of the if operation."""
    return self.regions[1].blocks[0]
