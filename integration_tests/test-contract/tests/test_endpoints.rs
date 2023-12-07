multiversx_sc::imports!();
multiversx_sc::derive_imports!();

pub mod world_state;

use multiversx_sc_scenario::{
    api::StaticApi,
    scenario_model::{ScCallStep, TxExpect},
};
use test_contract::{
    DayOfWeek, EnumWithEverything, ProxyTrait as _, HEX_ADDRESS, TOKEN_IDENTIFIER,
    TOKEN_IDENTIFIER_2,
};
use world_state::*;

#[test]
fn test_endpoint_1() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_1())
            .expect(TxExpect::ok()),
    );
}

#[test]
fn test_endpoint_2() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_2(
                4u8,
                75u16,
                874566u32,
                8984584484u64,
                1848usize,
            ))
            .expect(TxExpect::ok()),
    );

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_2(
                4u8,
                76u16,
                874566u32,
                8984584484u64,
                1848usize,
            ))
            .expect(TxExpect::user_error("str:b failed")),
    );
}

#[test]
fn test_endpoint_3() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_3(
                -4i8,
                -75i16,
                -874566i32,
                8984584484i64,
                -1848isize,
            ))
            .expect(TxExpect::ok()),
    );

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_3(
                -4i8,
                -75i16,
                -874568i32,
                8984584484i64,
                -1848isize,
            ))
            .expect(TxExpect::user_error("str:c failed")),
    );
}

#[test]
fn test_endpoint_4() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_4(
                TokenIdentifier::from(TOKEN_IDENTIFIER),
                ManagedAddress::from(HEX_ADDRESS),
            ))
            .expect(TxExpect::ok()),
    );

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_4(
                TokenIdentifier::from(TOKEN_IDENTIFIER_2),
                ManagedAddress::from(HEX_ADDRESS),
            ))
            .expect(TxExpect::user_error("str:a failed")),
    );
}

#[test]
fn test_endpoint_5() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_5(
                Some(TokenIdentifier::from(TOKEN_IDENTIFIER)),
                OptionalValue::<u64>::None,
            ))
            .expect(TxExpect::ok()),
    );

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_5(
                Some(TokenIdentifier::from(TOKEN_IDENTIFIER)),
                OptionalValue::<u64>::Some(78u64),
            ))
            .expect(TxExpect::user_error("str:b failed")),
    );
}

#[test]
fn test_endpoint_6() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    let mut b = MultiValueEncoded::<StaticApi, u32>::new();
    b.push(1u32);
    b.push(2u32);
    b.push(3u32);
    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_6(7846u32, b.clone()))
            .expect(TxExpect::ok()),
    );

    b.push(4u32);
    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_6(7846u32, b))
            .expect(TxExpect::user_error("str:b failed")),
    );
}

#[test]
fn test_endpoint_7() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_7(
                DayOfWeek::Monday,
                DayOfWeek::Sunday,
                EnumWithEverything::Default,
                EnumWithEverything::Today(DayOfWeek::Tuesday),
                EnumWithEverything::Write(ManagedVec::from(Vec::from([1u8, 2u8, 4u8, 8u8])), 14u16),
                EnumWithEverything::Struct {
                    int: 8u16,
                    seq: ManagedVec::from(Vec::from([9u8, 45u8])),
                    another_byte: 0u8,
                    uint_32: 789484u32,
                    uint_64: 485u64,
                },
            ))
            .expect(TxExpect::ok()),
    );

    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_7(
                DayOfWeek::Monday,
                DayOfWeek::Sunday,
                EnumWithEverything::Default,
                EnumWithEverything::Today(DayOfWeek::Tuesday),
                EnumWithEverything::Write(ManagedVec::from(Vec::from([1u8, 2u8, 4u8, 8u8])), 14u16),
                EnumWithEverything::Struct {
                    int: 8u16,
                    seq: ManagedVec::from(Vec::from([9u8, 45u8])),
                    another_byte: 5u8,
                    uint_32: 789484u32,
                    uint_64: 485u64,
                },
            ))
            .expect(TxExpect::user_error("str:f failed")),
    );
}

#[test]
fn test_endpoint_8() {
    let mut world_state = WorldState::new();
    world_state.deploy_all();

    let mut b = MultiValueEncoded::<StaticApi, EsdtTokenPayment<StaticApi>>::new();
    b.push(EsdtTokenPayment::new(
        TokenIdentifier::from(TOKEN_IDENTIFIER),
        0,
        BigUint::from(89784651u64),
    ));
    b.push(EsdtTokenPayment::new(
        TokenIdentifier::from(TOKEN_IDENTIFIER_2),
        0,
        BigUint::from(184791484u64),
    ));
    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_8(b))
            .expect(TxExpect::ok()),
    );

    let mut b_bis = MultiValueEncoded::<StaticApi, EsdtTokenPayment<StaticApi>>::new();
    b_bis.push(EsdtTokenPayment::new(
        TokenIdentifier::from(TOKEN_IDENTIFIER),
        0,
        BigUint::from(89784651u64),
    ));
    b_bis.push(EsdtTokenPayment::new(
        TokenIdentifier::from(TOKEN_IDENTIFIER_2),
        0,
        BigUint::from(18478484u64),
    ));
    world_state.world.sc_call(
        ScCallStep::new()
            .from(USER_ADDRESS_EXPR)
            .call(world_state.test_contract.endpoint_8(b_bis))
            .expect(TxExpect::user_error("str:Wrong second payment")),
    );
}
