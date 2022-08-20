from brownie import Box, BoxV2, ProxyAdmin, TransparentUpgradeableProxy, Contract
from scripts.helpers import get_account, network, encode_function_data, upgrade


def main():
    """
    This proxy implementation is centralized because the proxy deployer address is the only one that controls the proxy contract.
    This risk might be mitigated by using a multisig wallet to deploy the proxy.
    """
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy({"from": account}, publish_source=True)
    print(box.retrieve())
    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=True)
    # initializer = box.store, 1
    # box_encoded_initializer_function = encode_function_data(initializer)
    # empty initializer:
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
        publish_source=True,
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    # Assigning proxy the abi os the Box contract.
    # This works only because the proxy contract delegates all of its calls to the Box contract
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())
    # upgrade:
    box_v2 = BoxV2.deploy({"from": account}, publish_source=True)
    upgrade_transaction = upgrade(account, proxy, box_v2.address, proxy_admin_contract=proxy_admin)
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded. Now it points to BoxV2 contract!!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box_increment_tx = proxy_box.increment({"from": account})
    proxy_box_increment_tx.wait(1)
    # 1 -> 2 - Storage remains because it was kept in the proxy contract
    print(proxy_box.retrieve())
