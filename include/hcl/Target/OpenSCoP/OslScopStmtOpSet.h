/*
 * Copyright HeteroCL authors. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 * Modification: Polymer
 * https://github.com/kumasento/polymer
 */

//===- OslScopStmtOpSet.h ---------------------------------------*- C++ -*-===//
//
// This file declares the class OslScopStmtOpSet.
//
//===----------------------------------------------------------------------===//
#ifndef HCL_SUPPORT_OSLSCOPSTMTOPSET_H
#define HCL_SUPPORT_OSLSCOPSTMTOPSET_H

#include "llvm/ADT/SetVector.h"

using namespace llvm;

namespace mlir {
class Operation;
struct LogicalResult;
class FlatAffineValueConstraints;
} // namespace mlir

namespace mlir {
namespace hcl {

/// This class contains a set of operations that will correspond to a single
/// OpenScop statement body. The underlying data structure is SetVector.
class OslScopStmtOpSet {
public:
  using Set = llvm::SetVector<mlir::Operation *>;
  using iterator = Set::iterator;
  using reverse_iterator = Set::reverse_iterator;

  OslScopStmtOpSet() {}

  /// The core store op. There should be only one of it.
  mlir::Operation *getStoreOp() { return storeOp; }

  /// Insert.
  void insert(mlir::Operation *op);

  /// Count.
  unsigned count(mlir::Operation *op) { return opSet.count(op); };

  /// Size.
  unsigned size() { return opSet.size(); }

  /// Iterators.
  iterator begin() { return opSet.begin(); }
  iterator end() { return opSet.end(); }
  reverse_iterator rbegin() { return opSet.rbegin(); }
  reverse_iterator rend() { return opSet.rend(); }

  mlir::Operation *get(unsigned i) { return opSet[i]; }

  /// The domain of a stmtOpSet is the union of all load/store operations in
  /// that set. We calculate such a union by concatenating the constraints of
  /// domain defined by FlatAffineValueConstraints.
  /// TODO: improve the interface.
  mlir::LogicalResult getDomain(mlir::FlatAffineValueConstraints &domain);
  mlir::LogicalResult
  getDomain(mlir::FlatAffineValueConstraints &domain,
            SmallVectorImpl<mlir::Operation *> &enclosingOps);

  /// Get the enclosing operations for the opSet.
  mlir::LogicalResult
  getEnclosingOps(SmallVectorImpl<mlir::Operation *> &enclosingOps);

private:
  Set opSet;

  mlir::Operation *storeOp = nullptr;
};

} // namespace hcl
} // namespece mlir

#endif
