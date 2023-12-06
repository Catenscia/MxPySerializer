#![no_std]

use multiversx_sc::hex_literal::hex;

multiversx_sc::imports!();
multiversx_sc::derive_imports!();

pub const TOKEN_IDENTIFIER: &[u8] = b"WEGLD-abcdef";
pub const TOKEN_IDENTIFIER_2: &[u8] = b"MEX-abcdef";
pub const HEX_ADDRESS: [u8; 32] =
    hex!("000000000000000005004d4e468a6785c67dcf63611a05266562ba913638aa59");
/// erd1qqqqqqqqqqqqqpgqf48ydzn8shr8mnmrvydq2fn9v2afzd3c4fvsk4wglm

#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, TypeAbi, PartialEq, Eq)]
pub struct MyStruct<M: ManagedTypeApi> {
    pub int: u16,
    pub seq: ManagedVec<M, u8>,
    pub another_byte: u8,
    pub uint_32: u32,
    pub uint_64: u64,
}

#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, TypeAbi, PartialEq, Eq)]
pub struct Struct<M: ManagedTypeApi> {
    pub int: u16,
    pub seq: ManagedVec<M, u8>,
    pub another_byte: u8,
    pub uint_32: u32,
    pub uint_64: u64,
}

#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, TypeAbi, PartialEq, Eq)]
pub enum DayOfWeek {
    Monday,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday,
    Sunday,
}

#[derive(TopEncode, TopDecode, NestedEncode, NestedDecode, TypeAbi, PartialEq, Eq)]
pub enum EnumWithEverything<M: ManagedTypeApi> {
    Default,
    Today(DayOfWeek),
    Write(ManagedVec<M, u8>, u16),
    Struct {
        int: u16,
        seq: ManagedVec<M, u8>,
        another_byte: u8,
        uint_32: u32,
        uint_64: u64,
    },
}

/// This contract has only view endpoint that all expects very specific inputs.
/// This is used to check that the data send to the contract is interpreted as wanted
#[multiversx_sc::contract]
pub trait TestContract {
    #[init]
    fn init(&self) {}

    #[view]
    fn endpoint_0(&self, a: Struct<Self::Api>) {
        let _ = a.uint_32.clone();
    }

    #[view]
    fn endpoint_1(&self) {}

    #[view]
    fn endpoint_2(
        &self,
        a: u8,
        b: u16,
        c: u32,
        d: u64,
        e: usize,
    ) -> MultiValue5<u8, u16, u32, u64, usize> {
        require!(a == 4u8, "a failed");
        require!(b == 75u16, "b failed");
        require!(c == 874566u32, "c failed");
        require!(d == 8984584484u64, "d failed");
        require!(e == 1848usize, "e failed");
        (a, b, c, d, e).into()
    }

    #[view]
    fn endpoint_3(
        &self,
        a: i8,
        b: i16,
        c: i32,
        d: i64,
        e: isize,
    ) -> MultiValue5<i8, i16, i32, i64, isize> {
        require!(a == -4i8, "a failed");
        require!(b == -75i16, "b failed");
        require!(c == -874566i32, "c failed");
        require!(d == 8984584484i64, "d failed");
        require!(e == -1848isize, "e failed");
        (a, b, c, d, e).into()
    }

    #[view]
    fn endpoint_4(
        &self,
        a: TokenIdentifier,
        b: ManagedAddress,
    ) -> MultiValue2<TokenIdentifier, ManagedAddress> {
        require!(a == TokenIdentifier::from(TOKEN_IDENTIFIER), "a failed");
        require!(b == ManagedAddress::from(HEX_ADDRESS), "b failed");
        (a, b).into()
    }

    #[view]
    fn endpoint_5(
        &self,
        a: Option<TokenIdentifier>,
        b: OptionalValue<u64>,
    ) -> MultiValue2<Option<TokenIdentifier>, OptionalValue<u64>> {
        require!(
            a == Some(TokenIdentifier::from(TOKEN_IDENTIFIER)),
            "a failed"
        );
        require!(b.is_none(), "b failed");
        (a, b).into()
    }

    #[view]
    fn endpoint_5_bis(
        &self,
        a: Option<TokenIdentifier>,
        b: OptionalValue<u64>,
    ) -> MultiValue2<Option<TokenIdentifier>, OptionalValue<u64>> {
        require!(
            a == Some(TokenIdentifier::from(TOKEN_IDENTIFIER)),
            "a failed"
        );
        require!(b.clone().into_option() == Some(789u64), "b failed");
        (a, b).into()
    }

    #[view]
    fn endpoint_6(
        &self,
        a: u32,
        b: MultiValueEncoded<u32>,
    ) -> MultiValue2<u32, MultiValueEncoded<u32>> {
        let mut expected_b: MultiValueEncoded<u32> = MultiValueEncoded::new();
        expected_b.push(1u32);
        expected_b.push(2u32);
        expected_b.push(3u32);
        require!(a == 7846u32, "a failed");
        require!(b == expected_b, "b failed");
        (a, b).into()
    }

    #[view]
    fn endpoint_7(
        &self,
        a: DayOfWeek,
        b: DayOfWeek,
        c: EnumWithEverything<Self::Api>,
        d: EnumWithEverything<Self::Api>,
        e: EnumWithEverything<Self::Api>,
        f: EnumWithEverything<Self::Api>,
    ) -> MultiValue6<
        DayOfWeek,
        DayOfWeek,
        EnumWithEverything<Self::Api>,
        EnumWithEverything<Self::Api>,
        EnumWithEverything<Self::Api>,
        EnumWithEverything<Self::Api>,
    > {
        require!(a == DayOfWeek::Monday, "a failed");
        require!(b == DayOfWeek::Sunday, "b failed");
        require!(c == EnumWithEverything::Default, "c failed");
        require!(
            d == EnumWithEverything::Today(DayOfWeek::Tuesday),
            "d failed"
        );
        let mut expected_e_seq = ManagedVec::new();
        expected_e_seq.push(1u8);
        expected_e_seq.push(2u8);
        expected_e_seq.push(4u8);
        expected_e_seq.push(8u8);
        require!(
            e == EnumWithEverything::Write(expected_e_seq, 14u16),
            "e failed"
        );
        let mut expected_f_seq = ManagedVec::new();
        expected_f_seq.push(9u8);
        expected_f_seq.push(45u8);
        require!(
            f == EnumWithEverything::Struct {
                int: 8u16,
                seq: expected_f_seq,
                another_byte: 0u8,
                uint_32: 789484u32,
                uint_64: 485u64
            },
            "f failed"
        );
        (a, b, c, d, e, f).into()
    }

    #[view]
    fn endpoint_8(
        &self,
        payments: MultiValueEncoded<EsdtTokenPayment>,
    ) -> MultiValueEncoded<EsdtTokenPayment> {
        let payment_vec = payments.to_vec();
        require!(payments.len() == 2, "Wrong payments number");
        require!(
            payment_vec.get(0)
                == EsdtTokenPayment::new(
                    TokenIdentifier::from(TOKEN_IDENTIFIER),
                    0,
                    BigUint::from(89784651u64)
                ),
            "Wrong first payment"
        );
        require!(
            payment_vec.get(1)
                == EsdtTokenPayment::new(
                    TokenIdentifier::from(TOKEN_IDENTIFIER_2),
                    0,
                    BigUint::from(184791484u64)
                ),
            "Wrong second payment"
        );
        payments
    }
}
