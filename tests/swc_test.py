from solgrep import *
import pytest

@pytest.fixture()
def solquery():
    return SolGrep()

@pytest.mark.parametrize("swc", range(100,137))
def test_swc(solquery, swc):

    try:
      solquery.load_source_file('SWC/swc-{}.sol'.format(swc))
    except:
      pytest.skip("SWC does not exist")
    solquery.load_query_yaml_file('SWC/swc-{}.yaml'.format(swc))

    solquery.query()

    result = json.dumps(solquery.report())
    report = open('SWC/swc-{}.report'.format(swc)).read()

    assert result == report