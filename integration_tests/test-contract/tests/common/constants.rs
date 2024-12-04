use multiversx_sc::hex_literal::hex;
use multiversx_sc_scenario::imports::*;

// users
pub const USER_ADDRESS: TestAddress = TestAddress::new("user");
pub const OWNER_ADDRESS: TestAddress = TestAddress::new("owner");

// contracts addresses
pub const TEST_CONTRACT_ADDRESS: TestSCAddress = TestSCAddress::new("test-contract");

// contracts codes
pub const TEST_CONTRACT_CODE_PATH: MxscPath = MxscPath::new("output/test-contract.mxsc.json");

// parameters
pub const TOKEN_IDENTIFIER: &[u8] = b"WEGLD-abcdef";
pub const TOKEN_IDENTIFIER_2: &[u8] = b"MEX-abcdef";
pub const HEX_ADDRESS: [u8; 32] =
    hex!("000000000000000005004d4e468a6785c67dcf63611a05266562ba913638aa59");
// erd1qqqqqqqqqqqqqpgqf48ydzn8shr8mnmrvydq2fn9v2afzd3c4fvsk4wglm
