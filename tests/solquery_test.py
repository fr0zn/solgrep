from solquery import *
import pytest

testdata = [
    (
'''
pragma solidity 0.7.0;
''',
'''
pragma solidity 0.7.0
''',
        # Matching
        [ True, ],
        # Metavars
        [
            {},
        ],
        # Match from/to
        [ (0,22), ]

    ),
    (
'''
pragma solidity >0.7.0 <=0.8.0;
''',
'''
pragma solidity $VERSION;
''',
        # Matching
        [ True, ],
        # Metavars
        [
            {b'$VERSION': b'>0.7.0 <=0.8.0'},
        ],
        # Match from/to
        [ (0,31), ]

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
string memory $A = '$STRING_5';
''',
        # Matching
        [ True, ],
        # Metavars
        [
            {b'$A': b'a', '$STRING_5': 'asdfmore'},
        ],
        # Match from/to
        [ (21,75), ]

    ),
    (
'''
function setVars(address _contract, uint256 num) public payable {
}
''',
'''
function $NAME(..., address $C, ..., uint256 $NUM, ...) ... {
    ...
}
''',
        # Matching
        [ True, ],
        # Metavars
        [
            {b'$NAME': b'setVars', b'$C': b'_contract', b'$NUM': b'num'},
        ],
        # Match from/to
        [ (0,67), ]

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
        # Matching
        [ True, ],
        # Metavars
        [
           {b'$NAME': b'Test', b'$TYPE': b'uint', b'$VISIBILITY': b'public', b'$Y': b'y', b'$FNC': b'one', b'$STATE': b'view', b'$NUM': b'10', b'$VAR': b'a'},
        ],
        # Match from/to
        [ (0,173), ]

    ),
]

@pytest.fixture()
def solquery():
    return SolidityQuery()


@pytest.mark.parametrize("src,query,matchings,metavars,matchbytes", testdata)
def test_solquery(solquery, src, query, matchings, metavars, matchbytes):
    src = src.strip()
    query = query.strip()
    solquery.load_source_string(src)
    solquery.load_query_string(query)
    result = solquery.query()
    assert matchings == [x.is_match for x in result]
    assert metavars == [x.meta_vars for x in result]
    assert matchbytes == [x.get_range() for x in result]
