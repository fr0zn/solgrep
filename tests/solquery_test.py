from solquery import *
import pytest
import json

testdata = [
    (
'''
pragma solidity 0.7.0;
''',
'''
id: solidity-test
message: >
  This is the message for testing
risk: 1
impact: 1
patterns:
  - pattern: pragma solidity 0.7.0
''',
        # Report
        {'id': 'solidity-test', 'message': 'This is the message for testing', 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {}, 'bytesrange': [(0, 22)], 'linesrange': [((0, 0), (0, 22))]}
    ),
    (
'''
pragma solidity >0.7.0 <=0.8.0;
''',
'''
id: solidity-test
message: >
  This is the message for testing {{VERSION}}
risk: 1
impact: 1
patterns:
  - pattern: pragma solidity $VERSION;
metavars-regex:
  $VERSION: .*(=|>|<|^).*
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message for testing ['>0.7.0 <=0.8.0']", 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'VERSION': ['>0.7.0 <=0.8.0']}, 'bytesrange': [(0, 31)], 'linesrange': [((0, 0), (0, 31))]}

    ),
    (
'''
function NAME(){
    string memory a = "asdf"
    /* comment */
    "more";
}
''',
'''
id: solidity-test
message: |
  This is the message for testing {{STRING5}}
risk: 1
impact: 1
patterns:
  - pattern: string memory $A = '$STRING5';
metavars-regex:
  $STRING5: a.*
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message for testing ['asdfmore']", 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'A': ['a'], 'STRING5': ['asdfmore']}, 'bytesrange': [(21, 75)], 'linesrange': [((1, 4), (3, 11))]}

    ),
    (
'''
function setVars(address _contract, uint256 num) public payable {
}
''',
'''
id: solidity-test
message: |
  This is the message for testing {{NAME}} {{C}}, {{NUM}}
risk: 1
impact: 1
patterns:
  - pattern: |
      function $NAME(..., address $C, ..., uint256 $NUM, ...) ... {
      ...
      }
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message for testing ['setVars'] ['_contract'], ['num']", 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'NAME': ['setVars'], 'C': ['_contract'], 'NUM': ['num']}, 'bytesrange': [(0, 67)], 'linesrange': [((0, 0), (1, 1))]}

    ),
    (
'''
contract Test {

    uint public y;

    function one() public view returns(uint[]) {
        uint[10] a = new uint[](10);

        // More nodes

        return a;
    }

}
''',
'''
id: solidity-test
message: |
  This is the message for testing {{NAME}} {{FNC}} {{TYPE}} {{NUM}}
risk: 1
impact: 1
patterns:
  - pattern: |
      contract $NAME {
      ...
      $TYPE $VISIBILITY $Y;
      ...
      function $FNC() $VISIBILITY $STATE returns($TYPE[]) {
          ...
          $TYPE[$NUM] $VAR = new $TYPE[]($NUM);
          ...
          return $VAR;
          }
          ...
      }
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message for testing ['Test'] ['one'] ['uint'] ['10']", 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'NAME': ['Test'], 'TYPE': ['uint'], 'VISIBILITY': ['public'], 'Y': ['y'], 'FNC': ['one'], 'STATE': ['view'], 'NUM': ['10'], 'VAR': ['a']}, 'bytesrange': [(0, 173)], 'linesrange': [((0, 0), (12, 1))]}

    ),
    (
'''
contract Test {
    function name() {

    }

    function name() public {

    }

    function name() external {

    }

}
''',
'''
id: solidity-test
message: |
  This is the message for testing{{ NAME | pluralize}}: {{ NAME | join(', ')}}
  List:
  {{ NAME | format_list('- {}')}}
risk: 1
impact: 1
patterns:
  - pattern: |
      function $NAME(...) ... {
        ...
      }
  - not: |
      function $NAME(...) $VISIBILITY {
        ...
      }
metavars-regex:
  $VISIBILITY: .*
''',
        # Report
        {'id': 'solidity-test', 'message': 'This is the message for testing: name\nList:\n- name', 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'NAME': ['name']}, 'bytesrange': [(20, 44)], 'linesrange': [((1, 4), (3, 5))]}

    ),
    (
'''
/*
 * @source: https://capturetheether.com/challenges/math/token-sale/
 * @author: Steve Marx
 */

pragma solidity ^0.4.21;

contract TokenSaleChallenge {
    mapping(address => uint256) public balanceOf;
    uint256 constant PRICE_PER_TOKEN = 1 ether;

    function TokenSaleChallenge(address _player) public payable {
        require(msg.value == 1 ether);
    }

    function isComplete() public view returns (bool) {
        return address(this).balance < 1 ether;
    }

    function buy(uint256 numTokens) public payable {
        require(msg.value == numTokens * PRICE_PER_TOKEN);

        balanceOf[msg.sender] += numTokens;
    }

    function sell(uint256 numTokens) public {
        require(balanceOf[msg.sender] >= numTokens);

        balanceOf[msg.sender] -= numTokens;
        msg.sender.transfer(numTokens * PRICE_PER_TOKEN);
    }
}

contract IntegerOverflowMappingSym1 {
    mapping(uint256 => uint256) map;

    function init(uint256 k, uint256 v) public {
        map[k] -= v;
    }
}

contract IntegerOverflowMinimal {
    uint public count = 1;

    function run(uint256 input) public {
        count -= input;
    }
}


contract IntegerOverflowMul {
    uint public count = 2;

    function run(uint256 input) public {
        count *= input;
    }
}
''',
'''
id: solidity-test 
message: |
  This is the message
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...} 
  - and: 
      - pattern: function $FUN(...)  ... {...}
        and:
          - pattern: $VAR[msg.sender] += ...
# This will match all solidity  version, including <0.8.0
metavars-regex:
  $FUN: buy 
''',
        # Report
        {'id': 'solidity-test', 'message': 'This is the message', 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'CONTRACT': ['TokenSaleChallenge']}, 'bytesrange': [(125, 849)], 'linesrange': [((7, 0), (31, 1))]} 

    ),
    (
'''
/*
 * @source: https://capturetheether.com/challenges/math/token-sale/
 * @author: Steve Marx
 */

pragma solidity ^0.4.21;

contract TokenSaleChallenge {
    mapping(address => uint256) public balanceOf;
    uint256 constant PRICE_PER_TOKEN = 1 ether;

    function TokenSaleChallenge(address _player) public payable {
        require(msg.value == 1 ether);
    }

    function isComplete() public view returns (bool) {
        return address(this).balance < 1 ether;
    }

    function buy(uint256 numTokens) public payable {
        require(msg.value == numTokens * PRICE_PER_TOKEN);

        balanceOf[msg.sender] += numTokens;
    }

    function sell(uint256 numTokens) public {
        require(balanceOf[msg.sender] >= numTokens);

        balanceOf[msg.sender] -= numTokens;
        msg.sender.transfer(numTokens * PRICE_PER_TOKEN);
    }
}

contract IntegerOverflowMappingSym1 {
    mapping(uint256 => uint256) map;

    function init(uint256 k, uint256 v) public {
        map[k] -= v;
    }
}

contract IntegerOverflowMinimal {
    uint public count = 1;

    function run(uint256 input) public {
        count -= input;
    }
}


contract IntegerOverflowMul {
    uint public count = 2;

    function run(uint256 input) public {
        count *= input;
    }
}
''',
'''
id: solidity-test 
message: |
  This is the message
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...} 
  - and: 
      - pattern: function init(...)  ... {...}
        and: ... -= ... 
      - pattern: function run(...)  ... {...}
        not: ... -= ... 
# This will match all solidity  version, including <0.8.0
metavars-regex:
  $CONTRACT: .* 
''',
        # Report
        {'id': 'solidity-test', 'message': 'This is the message', 'risk': 1, 'impact': 1, 'results': 2, 'metavars': {'CONTRACT': ['IntegerOverflowMappingSym1', 'IntegerOverflowMul']}, 'bytesrange': [(851, 1004), (1143, 1273)], 'linesrange': [((33, 0), (39, 1)), ((50, 0), (56, 1))]} 

    ),
    (
'''
pragma solidity >0.8.0;


contract IntegerOverflowMinimal {
    uint public count = 1;

    function run(uint256 input) public {
        count -= input;
    }
}


contract IntegerOverflowMul {
    uint public count = 2;

    function run(uint256 input) public {
        count *= input;
    }
}
''',
'''
id: solidity-test 
message: |
  This is the message
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...} 
  - and: function run(...)  ... {...}
    not:  ... *= ...
# This will match all solidity  version, including <0.8.0
metavars-regex:
  $CONTRACT: .* 
''',
        # Report
        {'id': 'solidity-test', 'message': 'This is the message', 'risk': 1, 'impact': 1, 'results': 1, 'metavars': {'CONTRACT': ['IntegerOverflowMinimal']}, 'bytesrange': [(26, 160)], 'linesrange': [((3, 0), (9, 1))]} 

    ),
]

@pytest.fixture()
def solquery():
    return SolidityQuery()


@pytest.mark.parametrize("src,query,report", testdata)
def test_solquery(solquery, src, query, report):
    src = src.strip()
    query = query.strip()
    solquery.load_source_string(src)
    # solquery.load_query_string(query)
    solquery.load_query_yaml_string(query)
    solquery.query()
    result = solquery.report()
    assert result == report


# @pytest.mark.parametrize("swc", range(100,101))
# def test_solquery(solquery, swc):
#     report = open('SWC/swc-{}.report'.format(swc)).read()


#     solquery.load_source_file('SWC/swc-{}.sol'.format(swc))
#     solquery.load_query_yaml_file('SWC/swc-{}.yaml'.format(swc))

#     solquery.query()

#     result = solquery.report()
#     report = eval(report)
#     assert result == report
