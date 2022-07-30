//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract tokenFarm is Ownable {
    address[] public allowedTokens;
    mapping(address => mapping(address => uint256)) public stakeBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    address[] public Stakers;
    IERC20 public dappToken;
    mapping(address => address) public priceFeedMapping;

    constructor(address _dappTokenAddress) public {
        dappToken = IERC20(_dappTokenAddress);
    }

    function setPriceFeedContract(address _token, address _priceFeed)
        public
        onlyOwner
    {
        priceFeedMapping[_token] = _priceFeed;
    }

    function issueTokens() public onlyOwner {
        for (
            uint256 StakersIndex = 0;
            StakersIndex < Stakers.length;
            StakersIndex++
        ) {
            address recepient = Stakers[StakersIndex];
            uint256 userTotalValue = getUserTotalValue(recepient);
            dappToken.transfer(recepient, userTotalValue);
        }
    }

    function unstakeTokens(address _token) public {
        uint256 balance = stakeBalance[_token][msg.sender];
        require(balance > 0, "Balance can't be 0!");
        IERC20(_token).transfer(msg.sender, balance);
        stakeBalance[_token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    function getUserTotalValue(address _user) public view returns (uint256) {
        uint256 totalValue = 0;
        require(
            uniqueTokensStaked[_user] > 0,
            "You don't havae stacked tokens!"
        );
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            totalValue =
                totalValue +
                getUserSingleTokenValue(
                    _user,
                    allowedTokens[allowedTokensIndex]
                );
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token)
        public
        view
        returns (uint256)
    {
        if (uniqueTokensStaked[_user] <= 0) {
            return 0;
        }
        (uint256 price, uint256 decimals) = getTokenValue(_token);
        return ((stakeBalance[_token][_user] * price) / 10**decimals);
    }

    function getTokenValue(address _token)
        public
        view
        returns (uint256, uint256)
    {
        address priceFeedAdress = priceFeedMapping[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAdress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals);
    }

    function stakeTokens(uint256 _amount, address _Token) public {
        require(_amount > 0, "Ammount should be more than 0!");
        require(IsAllowed(_Token), "Token isn'y allowed!");
        updateUniqueTokensStaked(msg.sender, _Token);
        IERC20(_Token).transferFrom(msg.sender, address(this), _amount);
        stakeBalance[_Token][msg.sender] =
            stakeBalance[_Token][msg.sender] +
            _amount;
        if (uniqueTokensStaked[msg.sender] == 1) {
            Stakers.push(msg.sender);
        }
    }

    function updateUniqueTokensStaked(address _address, address _token)
        internal
    {
        if (stakeBalance[_token][_address] <= 0) {
            uniqueTokensStaked[_address] = uniqueTokensStaked[_address] + 1;
        }
    }

    function addAllowed(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    function IsAllowed(address _token) public returns (bool) {
        for (
            uint256 allowedTokensIndex = 0;
            allowedTokensIndex < allowedTokens.length;
            allowedTokensIndex++
        ) {
            if (allowedTokens[allowedTokensIndex] == _token) {
                return true;
            }
        }
        return false;
    }
}
