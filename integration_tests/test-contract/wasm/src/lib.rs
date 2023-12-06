// Code generated by the multiversx-sc multi-contract system. DO NOT EDIT.

////////////////////////////////////////////////////
////////////////// AUTO-GENERATED //////////////////
////////////////////////////////////////////////////

// Init:                                 1
// Endpoints:                           10
// Async Callback (empty):               1
// Total number of exported functions:  12

#![no_std]

// Configuration that works with rustc < 1.73.0.
// TODO: Recommended rustc version: 1.73.0 or newer.
#![feature(lang_items)]

multiversx_sc_wasm_adapter::allocator!();
multiversx_sc_wasm_adapter::panic_handler!();

multiversx_sc_wasm_adapter::endpoints! {
    test_contract
    (
        init => init
        endpoint_0 => endpoint_0
        endpoint_1 => endpoint_1
        endpoint_2 => endpoint_2
        endpoint_3 => endpoint_3
        endpoint_4 => endpoint_4
        endpoint_5 => endpoint_5
        endpoint_5_bis => endpoint_5_bis
        endpoint_6 => endpoint_6
        endpoint_7 => endpoint_7
        endpoint_8 => endpoint_8
    )
}

multiversx_sc_wasm_adapter::async_callback_empty! {}
