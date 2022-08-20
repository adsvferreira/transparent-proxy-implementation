import eth_utils
from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-forked"]


def get_account(index: int = None, id: str = None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)  # Ex: af_test_account
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS + FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def encode_function_data(initializer=None, *args):
    """Encodes the function call so we can work with an initializer.

    Args:
        initializer ([brownie.network.contract.ContractTx], optional):
        The initializer function we want to call. Ex: 'box.store'.
        Default is None.

        args(Any, optional):
        Arguments to pass to the initializer function.

    Returns:
        [bytes]: Return the encoded bytes.
    """
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(account, proxy, new_implementation_address, proxy_admin_contract=None, initializer=None, *args):
    """Returns upgrade tx receipt"""
    if proxy_admin_contract:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            return proxy_admin_contract.upgradeAndCall(
                proxy.address, new_implementation_address, encode_function_call, {"from": account}
            )
        return proxy_admin_contract.upgrade(proxy.address, new_implementation_address, {"from": account})
    if initializer:  # if not proxy_admin_contract, proxy admin will be the deployer address
        encode_function_call = encode_function_data(initializer, *args)
        return proxy.upgradeAndCall(proxy.address, new_implementation_address, encode_function_call, {"from": account})
    return proxy.upgradeTo(proxy.address, new_implementation_address, {"from": account})
