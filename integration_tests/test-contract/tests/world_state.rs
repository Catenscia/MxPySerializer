use multiversx_sc::types::Address;
use multiversx_sc_scenario::{
    api::StaticApi,
    scenario_model::{Account, AddressValue, ScDeployStep, SetStateStep},
    *,
};
use test_contract::ProxyTrait as _;

pub const USER_ADDRESS_EXPR: &str = "address:user";
pub const OWNER_ADDRESS_EXPR: &str = "address:owner";
pub const TEST_CONTRACT_ADDRESS_EXPR: &str = "sc:test-contract";
pub const TEST_CONTRACT_PATH_EXPR: &str = "file:output/test-contract.wasm";

type TestContract = ContractInfo<test_contract::Proxy<StaticApi>>;

fn create_world() -> ScenarioWorld {
    let mut world = ScenarioWorld::new();
    world.set_state_step(
        SetStateStep::new()
            .put_account(OWNER_ADDRESS_EXPR, Account::new().nonce(1))
            .put_account(USER_ADDRESS_EXPR, Account::new().nonce(1))
            .new_address(OWNER_ADDRESS_EXPR, 1, TEST_CONTRACT_ADDRESS_EXPR),
    );

    world.register_contract(TEST_CONTRACT_PATH_EXPR, test_contract::ContractBuilder);

    world
}

pub struct WorldState {
    pub world: ScenarioWorld,
    pub owner_address: Address,
    pub user_address: Address,
    pub test_contract: TestContract,
}

impl WorldState {
    pub fn new() -> Self {
        WorldState {
            world: create_world(),
            owner_address: AddressValue::from(OWNER_ADDRESS_EXPR).to_address(),
            user_address: AddressValue::from(USER_ADDRESS_EXPR).to_address(),
            test_contract: TestContract::new(TEST_CONTRACT_ADDRESS_EXPR),
        }
    }

    pub fn deploy_all(&mut self) -> &mut Self {
        let test_contract_code = self.world.code_expression(TEST_CONTRACT_PATH_EXPR);
        self.world.sc_deploy(
            ScDeployStep::new()
                .from(OWNER_ADDRESS_EXPR)
                .code(test_contract_code)
                .call(self.test_contract.init()),
        );
        self
    }
}
