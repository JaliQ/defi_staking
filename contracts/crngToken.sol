//SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract CRNG is ERC20 {
    constructor() ERC20("Cringinium", "CRNG") {
        _mint(msg.sender, 1000000000000000000000000);
    }
}
