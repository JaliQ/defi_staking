from brownie import network, exceptions
from brownie.network import account
from scripts.helpful_scripts import (
    DECIMALS,
    INITIAL_PRICE_FEED_VALUE,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)
import pytest
from scripts.deploy import KEPT_BAL, deploy_token_farm


def test_set_price_feed():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("You aren't in local environment!")
    account = get_account()
    non_owner_account = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm()
    price_feed_address = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract(
        dapp_token.address, get_contract("eth_usd_price_feed"), {"from": account}
    )
    assert token_farm.priceFeedMapping(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm, dapp_token = deploy_token_farm()
        price_feed_address = get_contract("eth_usd_price_feed")
        token_farm.setPriceFeedContract(
            dapp_token.address,
            get_contract("eth_usd_price_feed"),
            {"from": non_owner_account},
        )


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    # Act
    tx = token_farm.issueTokens({"from": account})
    tx.wait(1)
    # Arrange
    # we are staking 1 dapp_token == in price to 1 ETH
    # soo... we should get 2,000 dapp tokens in reward
    # since the price of eth is $2,000
    assert (
        dapp_token.balanceOf(account.address)
        == starting_balance + INITIAL_PRICE_FEED_VALUE
    )


def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("You aren't in local environment!")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    assert token_farm.stakeBalance(dapp_token.address, account.address) == amount_staked
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.Stakers(0) == account.address
    return token_farm, dapp_token


def test_can_unstake(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    tx = token_farm.unstakeTokens(dapp_token.address, {"from": account})
    tx.wait(1)
    assert token_farm.uniqueTokensStaked(account.address) == 0
    assert dapp_token.balanceOf(account.address) == KEPT_BAL
    assert token_farm.stakeBalance(dapp_token.address, account.address) == 0


def test_get_user_total_value_with_different_tokens(amount_staked, random_erc20):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    # Act
    token_farm.addAllowedTokens(random_erc20.address, {"from": account})
    token_farm.setPriceFeedContract(
        random_erc20.address, get_contract("eth_usd_price_feed"), {"from": account}
    )
    random_erc20_stake_amount = amount_staked * 2
    random_erc20.approve(
        token_farm.address, random_erc20_stake_amount, {"from": account}
    )
    token_farm.stakeTokens(
        random_erc20_stake_amount, random_erc20.address, {"from": account}
    )
    # Assert
    total_value = token_farm.getUserTotalValue(account.address)
    assert total_value == INITIAL_PRICE_FEED_VALUE * 3


def test_get_token_value():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    token_farm, dapp_token = deploy_token_farm()
    # Act / Assert
    assert token_farm.getTokenValue(dapp_token.address) == (
        INITIAL_PRICE_FEED_VALUE,
        DECIMALS,
    )


def test_add_allowed_tokens():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner_account = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm()
    # Act
    token_farm.addAllowed(dapp_token.address, {"from": account})
    # Assert
    assert token_farm.allowedTokens(0) == dapp_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.addAllowed(dapp_token.address, {"from": non_owner_account})
