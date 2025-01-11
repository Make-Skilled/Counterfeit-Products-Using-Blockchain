// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract userManagement {
  address admin;
  string adminUsername="admin";
  string adminPassword="admin123";

  struct User{
    address _userAddress; // Mandatory
    string _userName;
    string _userPassword;
    string _userRole; // Mandatory
    string _userEmail;
    bool _exist;
  }

  // mapping variables
  mapping(address=>User) users; // user wallet address is pointing a structure of user -> users[_users[0]]
  mapping(string=>User) usernames; // _usernames[username]
  address[] userAddresses; // user dynamic array of wallet addresses, _users[0], _users[1]
  

  // you can find out length of array (_users.length) -> Number of users registered
  // you can't find out the length of mapping variable (1) = array (1)

  constructor() {
    admin=msg.sender; // msg.sender is a global variable where it is holding the address of contract invoker
  }

  // ValidateAdmin will verify login details of admin passed by frontend
  function validateAdmin(string memory username,string memory password) public view returns(bool) {
    if(keccak256(bytes(username))==keccak256(bytes(adminUsername))){
      if(keccak256(bytes(password))==keccak256(bytes(adminPassword))){
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  }

  // It will create an account of user
  function userSignUp(address wallet,string memory username,string memory password,string memory role,string memory email) public {
    require(!users[wallet]._exist,"Already exist"); // require condition should be always false
    require(!usernames[username]._exist,"Already username taken"); 

    // Structure Member
    User memory new_user=User(wallet,username,password,role,email,true);
    users[wallet]=new_user;
    usernames[username]=new_user; // new_user is a structure of records
    userAddresses.push(wallet); // it will push wallet address
  }

  // It will return all the registered Users
  function viewAllUsers() public view returns(User[] memory){
    User[] memory _userArray = new User[] (userAddresses.length); // 100 chairs (empty)
    // empty structures create -> the length of userAddress (1)

    for (uint256 i = 0; i < userAddresses.length; i++) { // 0<1 // 100 students one-by-one seating
            _userArray[i] = users[userAddresses[i]]; // users[wallet]
    }

    return _userArray; 
  }

  // It will return only one record of user based on username
  function viewUserByUsername(string memory username) public view returns(User memory) {
    require(usernames[username]._exist,"No account with that username"); // true
    return usernames[username];
  }

  // It will return only one record of user based on wallet
  function viewUserByWallet(address wallet) public view returns(User memory) {
    require(users[wallet]._exist,"No account with that wallet");
    return users[wallet];
  }

  // It will validate the login details of user
  function userLogin(string memory username,string memory password) public view returns(bool){
    require(usernames[username]._exist,"No account with that username"); 

    if(keccak256(bytes(username))==keccak256(bytes(usernames[username]._userName))){
      if(keccak256(bytes(password))==keccak256(bytes(usernames[username]._userPassword))){
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  }

  // It has to return admin wallet address, admin username
  function viewAdmin() public view returns(address,string memory) {
    // Read Operation only
    return (admin,adminUsername);
  }
}