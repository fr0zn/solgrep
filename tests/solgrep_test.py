from solgrep import *
import pytest
import json

testdata = [
    (
'''
contract Test {
    function name() {

    }

    function name2() {

    }

    function name3() public {

    }

    function name4() external {

    }

}
''',
'''
id: solidity-test
message: |
  This is the message for testing {{ NAMES }}
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
        {'id': 'solidity-test', 'message': "This is the message for testing ['name', 'name2']", 'risk': 1, 'impact': 1, 'results': 2, 'metavars': [{'NAME': ['name']}, {'NAME': ['name2']}], 'bytesrange': [(20, 44), (50, 75)], 'linesrange': [((1, 4), (3, 5)), ((5, 4), (7, 5))]}

    ),
    (
'''
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
  This is the message {{ CONTRACTS }} {{FUNS}} {{VARS}}
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...}
  - and:
      - pattern: function $FUN(...)  ... {...}
        and:
          - pattern: $VAR[msg.sender] += ...
metavars-regex:
  $FUN: buy
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message ['TokenSaleChallenge'] ['buy'] ['balanceOf']", 'risk': 1, 'impact': 1, 'results': 1, 'metavars': [{'CONTRACT': ['TokenSaleChallenge'], 'FUN': ['buy'], 'VAR': ['balanceOf']}], 'bytesrange': [(26, 750)], 'linesrange': [((2, 0), (26, 1))]}

    ),
    (
'''
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
  This is the message {{CONTRACTS}}
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...}
  - and:
      - pattern: function init(...)  ... {...}
        and: ... -= ...
      - pattern: function run(...)  ... {...}
        not: ... -= ...
metavars-regex:
  $CONTRACT: .*
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message ['IntegerOverflowMappingSym1', 'IntegerOverflowMul']", 'risk': 1, 'impact': 1, 'results': 2, 'metavars': [{'CONTRACT': ['IntegerOverflowMappingSym1']}, {'CONTRACT': ['IntegerOverflowMul']}], 'bytesrange': [(752, 905), (1044, 1174)], 'linesrange': [((28, 0), (34, 1)), ((45, 0), (51, 1))]}

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
  This is the message {{CONTRACTS}}
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...}
  - and: function run(...)  ... {...}
    not:  ... *= ...
metavars-regex:
  $CONTRACT: .*
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message ['IntegerOverflowMinimal']", 'risk': 1, 'impact': 1, 'results': 1, 'metavars': [{'CONTRACT': ['IntegerOverflowMinimal']}], 'bytesrange': [(26, 160)], 'linesrange': [((3, 0), (9, 1))]}

    ),
    (
'''
pragma solidity >0.8.0;


contract IntegerOverflowMinimal {
    uint public count = 1;

    function run_div(uint256 input) public {
        count /= input;
    }

    function run(uint256 input) public {
        count -= input;
    }

    function run_more(uint256 input) public {
        count += input;
    }
}


contract IntegerOverflowMul {
    uint public count = 2;

    function run_2(uint256 input) public {
        count *= input;
    }
}
''',
'''
id: solidity-test
message: |
  This is the message {{CONTRACTS}} {{FUNS}}
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...}
    and:
      - pattern: function $FUN(...)  ... {...}
        and:
        - pattern: ... -= ...
        - pattern: ... *= ...
        - pattern: ... += ...
metavars-regex:
  $CONTRACT: .*
  $FUN: run_.*
''',
        # Report
        {'id': 'solidity-test', 'message': "This is the message ['IntegerOverflowMinimal', 'IntegerOverflowMul'] ['run_more', 'run_2']", 'risk': 1, 'impact': 1, 'results': 2, 'metavars': [{'CONTRACT': ['IntegerOverflowMinimal'], 'FUN': ['run_more']}, {'CONTRACT': ['IntegerOverflowMul'], 'FUN': ['run_2']}], 'bytesrange': [(26, 313), (316, 448)], 'linesrange': [((3, 0), (17, 1)), ((20, 0), (26, 1))]}

    ),
]

@pytest.fixture()
def solquery():
    return SolGrep()


@pytest.mark.parametrize("src,query,report", testdata)
def test_solquery(solquery, src, query, report):
    src = src.strip()
    query = query.strip()
    solquery.load_source_string(src)
    # solquery.load_query_string(query)
    solquery.load_query_yaml_string(query)
    solquery.query()
    result = solquery.report()
    print('RESULT')
    print('============================')
    print(result)
    print('============================')
    assert result == report
