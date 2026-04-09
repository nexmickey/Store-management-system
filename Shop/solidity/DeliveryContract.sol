// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract DeliveryContract {
    address payable owner_adr;
    address payable courier_adr;
    address payable customer_adr;

    uint256 total_price;
    uint256 owner_amount;
    uint256 courier_amount;

    enum StageEnum {
        INIT,
        PAY_DELIVERY,
        COURIER_PICK_UP,
        DONE,
        ERROR
    }
    struct StageOfDelivery {
        StageEnum stage;
        string stage_name;
        address payable allowed_user_adr;
    }

    StageOfDelivery[] stages;
    uint256 curr_stage_index;

    modifier check_user_allowed() { 
        require(stages[curr_stage_index].allowed_user_adr == msg.sender, 
            "You are not allowed to perform this transaction"); 
        _;
    }
    modifier check_member() { 
        require(msg.sender == customer_adr || msg.sender == courier_adr || msg.sender == owner_adr, 
            "Only customer, courier, or owner can do this action"); 
        _; 
    }
    modifier check_stage(StageEnum _stage) { 
        require(stages[curr_stage_index].stage == _stage, 
            string.concat("Action not allowed because current stage is:", stages[curr_stage_index].stage_name)); 
        _; 
    }

    function _move_to_next_stage() internal {
        require(curr_stage_index < stages.length - 1, "Already at the last stage");
        curr_stage_index++;
    }

    function pay_user(address payable _user, uint256 _amount) internal {
        (bool sent, ) = _user.call{value: _amount}("");
        require(sent, "Failed payment to user");
    }

    // zero stage
    constructor (address payable _customer, uint256 _price) {
        owner_adr    = payable(msg.sender);
        courier_adr  = payable(address(0));
        customer_adr = _customer;
        curr_stage_index = 0;

        total_price = _price;
        owner_amount = (80 * _price) / 100;
        courier_amount = (20 * _price) / 100;

        stages.push(StageOfDelivery(StageEnum.INIT, "CREATED", customer_adr));
        stages.push(StageOfDelivery(StageEnum.PAY_DELIVERY, "PAID", payable(address(0))));
        stages.push(StageOfDelivery(StageEnum.COURIER_PICK_UP, "PICKUP", owner_adr));
        stages.push(StageOfDelivery(StageEnum.DONE, "COMPLETE", payable(address(0))));
        stages.push(StageOfDelivery(StageEnum.ERROR, "ERROR", payable(address(0))));
    }

    // first stage (customer pays for delivery)
    function invoice() external payable check_stage(StageEnum.INIT) check_user_allowed {
        require(msg.value == total_price, "Insufficient funds!");
        _move_to_next_stage();
    }

    // second stage (courier picks up order)
    function pick_up_order(address payable _new_courier) external check_stage(StageEnum.PAY_DELIVERY) {
        courier_adr = _new_courier;
        _move_to_next_stage();
    }

    // last stage (customer confirms delivery)
    function delivered() external check_stage(StageEnum.COURIER_PICK_UP) check_user_allowed {
        _move_to_next_stage();

        pay_user(owner_adr, owner_amount);
        pay_user(courier_adr, courier_amount);
    }

    // getters
    function get_stage() external view returns (string memory) {
        return stages[curr_stage_index].stage_name;
    }
    function get_total_price() external view check_member returns (uint256, uint256, uint256){
        return (total_price, owner_amount, courier_amount);
    }
    function get_contract_info() external view check_member returns (address, address, address, uint256, uint256, uint256){
        return (owner_adr, customer_adr, courier_adr, total_price, owner_amount, courier_amount);
    }
}