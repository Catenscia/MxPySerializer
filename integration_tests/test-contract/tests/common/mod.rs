use multiversx_sc_scenario::imports::*;
use test_contract::proxy::TestContractProxy;

pub mod constants;
use constants::*;

pub fn setup_users(world: &mut ScenarioWorld) {
    world.account(USER_ADDRESS).nonce(1);
    world.account(OWNER_ADDRESS).nonce(1);
}

pub fn setup_contract(world: &mut ScenarioWorld) {
    // deploy
    world.register_contract(TEST_CONTRACT_CODE_PATH, test_contract::ContractBuilder);
    world
        .tx()
        .from(OWNER_ADDRESS)
        .typed(TestContractProxy)
        .init()
        .code(TEST_CONTRACT_CODE_PATH)
        .new_address(TEST_CONTRACT_ADDRESS)
        .run();
}

pub fn setup_world(world: &mut ScenarioWorld) {
    setup_users(world);
    setup_contract(world);
}
