use multiversx_sc_scenario::imports::*;

mod common;
use common::constants::*;
use common::setup_world;

use test_contract::proxy::{DayOfWeek, EnumWithEverything, TestContractProxy};

#[test]
fn test_endpoint_1() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_1()
        .run();
}

#[test]
fn test_endpoint_2() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_2(4u8, 75u16, 874566u32, 8984584484u64, 1848usize)
        .run();

    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_2(4u8, 76u16, 874566u32, 8984584484u64, 1848usize)
        .with_result(ExpectError(4, "b failed"))
        .run();
}

#[test]
fn test_endpoint_3() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_3(-4i8, -75i16, -874566i32, 8984584484i64, -1848isize)
        .run();

    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_3(-4i8, -75i16, -874568i32, 8984584484i64, -1848isize)
        .with_result(ExpectError(4, "c failed"))
        .run();
}

#[test]
fn test_endpoint_4() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_4(
            TokenIdentifier::from(TOKEN_IDENTIFIER),
            ManagedAddress::from(HEX_ADDRESS),
        )
        .run();

    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_4(
            TokenIdentifier::from(TOKEN_IDENTIFIER_2),
            ManagedAddress::from(HEX_ADDRESS),
        )
        .with_result(ExpectError(4, "a failed"))
        .run();
}

#[test]
fn test_endpoint_5() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_5(
            Some(TokenIdentifier::from(TOKEN_IDENTIFIER)),
            OptionalValue::<u64>::None,
        )
        .run();

    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_5(
            Some(TokenIdentifier::from(TOKEN_IDENTIFIER)),
            OptionalValue::<u64>::Some(78u64),
        )
        .with_result(ExpectError(4, "b failed"))
        .run();
}

#[test]
fn test_endpoint_6() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    let mut b = MultiValueVec::from(vec![1u32, 2u32, 3u32]);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_6(7846u32, b.clone())
        .run();

    b.push(4u32);
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_6(7846u32, b)
        .with_result(ExpectError(4, "b failed"))
        .run();
}

#[test]
fn test_endpoint_7() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    let mut b = MultiValueVec::from(vec![1u32, 2u32, 3u32]);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_7(
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
        )
        .run();

    b.push(4u32);
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_7(
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
        )
        .with_result(ExpectError(4, "f failed"))
        .run();
}

#[test]
fn test_endpoint_8() {
    // Given
    let mut world = ScenarioWorld::new();
    setup_world(&mut world);

    let payments = MultiValueVec::from(vec![
        EsdtTokenPayment::new(
            TokenIdentifier::from(TOKEN_IDENTIFIER),
            0,
            BigUint::from(89784651u64),
        ),
        EsdtTokenPayment::new(
            TokenIdentifier::from(TOKEN_IDENTIFIER_2),
            0,
            BigUint::from(184791484u64),
        ),
    ]);

    let payments_2 = MultiValueVec::from(vec![
        EsdtTokenPayment::new(
            TokenIdentifier::from(TOKEN_IDENTIFIER),
            0,
            BigUint::from(89784651u64),
        ),
        EsdtTokenPayment::new(
            TokenIdentifier::from(TOKEN_IDENTIFIER_2),
            0,
            BigUint::from(18478484u64),
        ),
    ]);

    // When
    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_8(payments)
        .run();

    world
        .tx()
        .from(USER_ADDRESS)
        .to(TEST_CONTRACT_ADDRESS)
        .typed(TestContractProxy)
        .endpoint_8(payments_2)
        .with_result(ExpectError(4, "Wrong second payment"))
        .run();
}
