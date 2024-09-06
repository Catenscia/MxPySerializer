mxpy --verbose contract deploy \
                --bytecode="output/test-contract.wasm" \
                --pem="wallets/test_owner.pem" \
                --gas-limit=150000000 \
                --proxy="https://devnet-gateway.multiversx.com" \
                --outfile="deploy.json" \
                --recall-nonce \
                --send