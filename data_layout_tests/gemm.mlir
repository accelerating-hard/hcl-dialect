// Copyright HeteroCL authors. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

// RUN: hcl-opt -opt %s | FileCheck %s
module {
    // define a customization template
    hcl.customization @gemm_opt(
        %AA: memref<?x?x!hcl.Type>,
        %BB: memref<?x?x!hcl.Type>,
        %CC: memref<?x?x!hcl.Type>,
        %i: !hcl.LoopHandle,
        %j: !hcl.LoopHandle,
        %k: !hcl.LoopHandle
    ) {
        hcl.pipeline(%j, 1)
        hcl.data_layout(%AA: memref<?x?x!hcl.Type>, "CompletePartition", 2)
        hcl.data_layout(%BB: memref<?x?x!hcl.Type>, "CompletePartition", 2)
        hcl.data_layout(%CC: memref<?x?x!hcl.Type>, "CompletePartition", 2)
        hcl.end
    }

    func.func @top(%A: memref<64x64xi32>, %B: memref<64x64xi32>) -> memref<64x64xi32>
    {   
        %s1 = hcl.create_op_handle "s1"
        %i1 = hcl.create_loop_handle %s1, "i1"
        %j1 = hcl.create_loop_handle %s1, "j1"
        %k1 = hcl.create_loop_handle %s1,  "k1"
        // C = A * B
        %C = memref.alloc() : memref<64x64xi32>
        affine.for %i = 0 to 64 {
            affine.for %j = 0 to 64 {
                affine.for %k = 0 to 64 {
                    %a = affine.load %A[%i, %k] : memref<64x64xi32>
                    %b = affine.load %B[%k, %j] : memref<64x64xi32>
                    %c = affine.load %C[%i, %j] : memref<64x64xi32>
                    %prod = arith.muli %a, %b : i32
                    %sum = arith.addi %prod, %c: i32
                    affine.store %sum, %C[%i, %j] : memref<64x64xi32>
                } { loop_name = "k1" }
            // CHECK: pipeline_ii = 1 : i32
            } { loop_name = "j1" }
        } { loop_name = "i1", op_name = "s1" }

        // apply the customization template
        hcl.apply @gemm_opt(%A, %B, %C, %i1, %j1, %k1) : (memref<64x64xi32>, memref<64x64xi32>, memref<64x64xi32>, !hcl.LoopHandle, !hcl.LoopHandle, !hcl.LoopHandle) -> ()
        return %C : memref<64x64xi32>
    }
}
