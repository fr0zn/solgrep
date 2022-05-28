# Solgrep

Solgrep is a tool that allows static semantic aware search on Solidity code. The source code is parsed and stored as an AST. The search queries are written using plan Solidity with extended syntax for ellipsis (aka skipping sibling/child nodes on the AST). The query tree and the source code tree are then compared using a BFS algorithm to determine if both trees are equal or not. Node comparison do include regex support and metavars definitions for matching the most complex rules that you could possibly imagine. The system allows writing the rules in a YAML file which will be used to query the source code.

## Example rule

The following example do show a query rule that would match any function with a given `$NAME` that do not have a `$VISIBILITY` set. `VISIBILITY` is a special metavar on the system that would match all valid visibilities on Solidity. More on this on the "Metavar" section.

```
id: solidity-visibility 
message: |
  We found {{ NAMES | comma }} which do not set their visibility.
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
```

As another example, the following rule will match any function that contains one of the defined mathematical operations inside the `and`. Finally all of those rules will only be valid if there is a matching root rule were the `pragma version` is below `0.8.0`.

```
id: solidity-overflow 
message: |
  The {{ NAMES | comma }} functions are vulnerable to underflow/overflow.
risk: 1
impact: 1
patterns:
  - pattern: function $NAME(...) ... {...}
  - and:
    - pattern: ... -= ...
    - pattern: ... += ...
    - pattern: ... *= ...
    - pattern: ... <<= ...
    - pattern: ... + ...
    - pattern: ... - ...
    - pattern: ... * ...
    - pattern: $_++ 
    - pattern: ++$_
        and:
        - pattern-root: pragma solidity $VERSION
# This will match all solidity  version, including <0.8.0
metavars-regex:
  $VERSION: (\d\.[0-7]\.\d*|<0\.8\.0)
```

## Usage

The the usage of the tool is very simple. One must import the `SolGrep` class from the `solgrep` file and create a new object:

```
from solgrep import SolGrep

sq = Solgrep()
```

### Loading the source code

The source code can be loaded in different ways, from a file or directly using an string:

```
// source.sol

pragma solidity 0.8.12;

contract Test {
    uint256 public a;

    function name() external {
        a = 1337;
    }
}
```

Loading the source code from the `source.sol` file:

```
sq.load_source_file("source.sol")
```

Loading the source code directly from a string:

```
src = '''
pragma solidity 0.8.12;

contract Test {
    uint256 public a;

    function name() external {
        a = 1337;
    }
}
'''

sq.load_source_string(src)
```

## Loading the query rule

Semgrep does support multiple query formats, including a single pattern search and complex YAML pattern syntax as seen in "Semgrep rule file".

## Displaying the AST and exporting a graph


## Semgrep rule file

Rules under semgrep are written using `YAML` syntax. Example rule file containing all the components that are required to satisfy a valid `semgrep` rule file:

```
id: issue-id 
message: |
  This is the message {{CONTRACTS | comma}}
risk: 1
impact: 1
patterns:
  - pattern: contract $CONTRACT {...}
    and:
      - pattern: function $FUN(...) ... {...}
        and:
        - pattern: ... -= ...
        - pattern: ... *= ...
        - pattern: ... += ...
metavars-regex:
  $CONTRACT: .*
  $FUN: admin.*
```

Each component is explained here:

- id
: The id is used to identify the rule and used on the reported in case of multiple rules defined.

- message
: The message is used on the reporter to describe the issue. Placeholders can be used to represent the found metavars, as an example the `{{ CONTRACTS | comma }}` will print in a comma separated list, all the `CONTRACT` metavars that do match the `patterns` section. More on the placeholder under "Semgrep message placeholders" 

- risk and impact
: This is used to represent the severity of the described found issue or rule. Any number or value can be inserted here and will be shown on the reporter.

- patterns
: This is the most complex and were all the semgrep power comes in. This section does allow multiple rules to be concatenated and matched against each other in an hierarchy way. A rule can be searched inside a rule by indenting it and using a combiner node, such as `not`, `and`, `and-either`, `not-either` and more. If multiple patterns are allowed, they can be listed inside `- patterns:`. More on the `patterns` under "Semgrep patterns".

- metavars-regex
: This node does allow describing how metavars will be matched on the system. Since metavars do match a full token regex patterns are supported. Each token matching the node type for the metavar will be compared with this description, if it does match it will be considered a valid token node. If the type of the node is the same but the regex does not satisfy the token will be considered as different. The example does describe 2 metavars, the `CONTRACT` and `FUN`, used on the patterns section to match any contract witch contain any function with a list of patterns inside it. The `CONTRACT` metavars does match any token name `.*`. However, the `FUN` metavar will only match functions starting with `admin` followed by anything, on the function name only. The `*` (asterisk) and `+` (plus) sign on regex will only match the current token, the `*`/`+` does not match until the end of the line as regex would do.


## Semgrep message placeholders

The message field under the rule file of semgrep does support complex parametrization and placeholders. The system is using Jinja2 for the templating system. That means that any placeholder as long as it has been defined can be used.

The following contract  will be used to showcase all possible scenarios:

```
pragma solidity 0.8.12;

contract Test() {

    uint256 public value;

    function func_add(uint256 a, uint256 b) external {
        value = a + b;
    }

    function func_sub(uint256 a, uint256 b) external {
        value = a - b;
    }

    function do_multiply(uint256 a, uint256 b) external {
        value = a * b;
    }
}
```

For every single defined metavar a pluralized placeholder will be used containing a list of all valid tokens for that metavars in case of multiple matches. If a none or single match is found, the pluralized token is still used. As an example, the following simplified rule file will display the message below it:  

```
message: The found functions starting with func_ are: {{FUNCS}}
patterns:
  - pattern: function $FUNC(...) ... {...}
metavars-regex:
  $FUNC: func_.*
```

```
The found function starting with func_ are: ['func_add', 'func_sub']
```

The placeholders can be extended by using filters. Filters are a way of manipulating the placeholder information to be represented in a different way. As an example, the following snippet does display a message rule field and the output for it using the same rule as the previous example.

``` 
message: The found function starting with func_ are: {{FUNCS | comma}}

Result:

The found functions starting with func_ are: func_add, func_sub
```

The output is filters and comma separated when using the `comma` filter on the placeholder. The system does support multiple placeholders and they can be designed to achive any output needs:

- pluralize(list, singular="", plural="s")
: The pluralize can be used in combination with a word to pluralize it in case the filter value contains more than 1 item. As an example, `The function{{ FUNCS | pluralize }}` will either return `The function` or `The functions` depending if `FUNCS` has more than one item.
The command can be customized on the fly with the arguments. As an example, using is with `There {{ FUNCS | pluralize("is a function", "are multiple functions")}}` would either produce, `There is a function` or `There are multiple functions` depending on the length of the `FUNCS` metavar list.

- comma(list, wrap="")
: It allows to comma separate the values on a metavar result list and represent them as an string. `{{ FUNCS | comma }}` would produce an string list with all the values separated by a `,` character. The comma does accept the `wrap` parameter, which allows adding a token or string before and after each element of the list. As an example `{{ FUNCS | comma('*')}}`, would add `'` to the beggining and end of each element of the metavar list. The example would produce `The found functions starting with func_ are *func_add*, *func_sub*`.

- list(list, pattern="{}", endline="\\n")
: This one allows full customization on the output of the metavar list, by default it does print each element in a new line. For example, this method could be used to create a Markdown list of all elements by using the `{{ FUNCS | list("- {}") }}` filter. You can create the same effect as the `comma` filter by using `{{ FUNCS | list(endline=",") }}`.

Finally, there is one internal placeholder named `CONTENTS`. This placeholder contains a list of the found query results content. As an example, the following snippet shows the content of this placeholder for the same source code and rule file as previous examples. 

``` 
['''
    function func_add(uint256 a, uint256 b) external {
      value = a + b;
    }
  ''',
  '''
    function func_sub(uint256 a, uint256 b) external {
      value = a - b;
    }
  ''']
```

## Semgrep patterns {#sec:semgreppatterns}


The pattern system allows complex declarations to be formed. It allow multiple rules to be concatenated and matched against each other in an hierarchy way. There exist multiple rules and definitions that can be used with others, and all of them do support metavar expressions inside the rules. There are two categories of rules: 

- Simple rules
: They are used to define the query content and used in conjunction with merging rules to create complex queries. They are, `pattern` and `pattern-root`.

- Merging rules
: They are rules which do not contain a query definition by themselves but do use simple rules to create complex query definitions. They can be combined and merged to satisfy the needs for the query. They are `patterns`, `and`, `not`, `and-either` and `not-either`.

Each rule description and an example showcasing the usage can be found can be found on the following section.

### Sempgrep patterns rules

- pattern
: This is the simplest definition. It is used to declare a valid `semgrep` rule containing pattern syntax code. It can be used as the base for the `YAML` rule file instead of the `patterns` to only match a single pattern. It can be used in combination with the root `patterns` to match multiple patterns in a single query rule. An example can be seen in the following snippet:

``` 
...
message: ... 
pattern: function $FUNC(...) ... {...}
metavars-regex:
  $FUNC: .*
  ...
```

- patterns
: This is used only on the root `YAML` file to indicate that the query does contain complex patterns or combination of different patterns not just a single pattern, although a single pattern can be used as well. An example can be seen under the following snippet were a query would match any function that starts with either `admin_` or `user_`. This query could be simplified by using a single `- pattern` declaration with an `|` (or) regex expression such as `admin_.*|user_.*`.

``` 
...
message: ... 
patterns: 
  - pattern: function $FUNC1(...) ... {...}
  - pattern: function $FUNC2(...) ... {...}
metavars-regex:
  $FUNC1: admin_.*
  $FUNC2: user_.*
  ...
```

- and
: This declaration can only be used in conjunction with a previous `pattern` to match sub-patterns or filter the main pattern for sub-conditions. The following snippet example does show a query that would match any function (see the metavar regex expression) and that contains at least one `+` operation with any two operands.

``` 
...
message: ... 
patterns: 
  - pattern: function $VAR(...) ... {...}
  - and: ... + ...
metavars-regex:
  $VAR: .*
  ...
```

- pattern-root
: This allows to look for pattern starting from the top of the source file. It can be used in conjunction with the `and` rule to filter other rules based on outer scope patterns. As an example the following snippet does show the usage of the `root` pattern in combination with the `and` pattern. The example, does find all `-=` and `+=` operations with a top level rule of the pragma version being less than `0.8.0`. This query could also be achieved by filtering the `-=` and `+=` rules with an `and` expression of the pragma. However, that would require writing the same filtering pattern twice.

``` 
...
message: ... 
patterns: 
  - pattern: ... -= ...
  - pattern: ... += ...
  - and:
    - pattern-root: pragma solidity $VERSION
metavars-regex:
  $VERSION: (\d\.[0-7]\.\d*|<0\.8\.0)
  ...
```

- not
: This definition is used to filter simple patterns or the results of previous complex patterns for none matching queries. It can be used to filter exceptions for `and` complex rules that would be otherwise complex to achieve with a single or regex expression. The following example, does show a rule that would match any function but will filter the results with the ones that do not have a visibility set (`VISIBILITY` is an especial metavar type, see "Metavars" section).

``` 
message: ... 
patterns:
  - pattern: | 
      function $NAME(...) ... {
        ...
      }
  - not: |
      function $NAME(...) $VISIBILITY {
        ...
      } 
```

- and-either and not-either
: At the time of writing this paper, those rules are currently being refactored. They allow as the name states, list multiple simple patterns underneath to obtain multiple `and` results or filter based on multiple `not` rules.

## Metavars


### Comparing Nodes and metavar support {#sec:metavarsupport}

By definition, two nodes will be the same if the underlying tokens do match on every single element. As an example, the contract name `ContractName` will only match with compared node if every single character is the same, in this case the comparer node should be `ContractName`. 

For example, writing a query for the code shown on the following snippet that would match both, `func1` and `func2`, the latter calling the former, could be possible accomplished by using ellipsis as shown on the query snippet. However, that would also match `func3` being called by `func4` and moreover, `func4` calling `func1`, which is not something that the code states. Since ellipsis can match anything it is possible to match invalid statements that do not truly represent the real source code.

``` 
contract ContractName {
  function func1() external {}
  function func2() external {
    func1();
  }

  function func3() external {
  }
  function func4() external {
    func3();
  }
}
```

``` 
contract ContractName {
  ... // match any previous code
  function ...() external {}
  function ...() external {
    ...();
  }
  ... // match any following code
}
```

With the implications seen on relying only on ellipsis a new way of representing tokens was introduced. Any identifier under solgrep can be prefixed with the `$` symbol (dollarsign). When comparing literal tokens, aka nodes, this value will be checked. If the identifier starts with this symbol, solgrep will keep a reference to its literal value which can be later referenced during the query. As an example, the previous query file could be rewritten as shown:

```
contract ContractName {
  ... // match any previous code
  function $FNC external {
    ...;
  }
  function $CALLER external {
    $FNC();
  }
  ... // match any following code
}
```

The code will now keep valid metavars references and find all possibilities that do match those metavars. Solgrep, will keep a reference of valid metavars while scanning the query tree. With the previous query, the `$FNC` metavar will initially be filled by `func1`, `func2`, `func3` and `func4`, since they all match the `$FNC` definition (there is an internal ellipsis indicating that this function can contain "any" or "none" body). Once solgrep does start to interpret the `$CALLER` definition, the `func2` and `func4` literals on `$FNC` will be discarded. The `$CALLER` metavar will be store with `func2` and `func4` as valid. 

> The metavar system will never detect false positives since the literal representation of the placeholder metavar variables is compared against the queried source code.

Some internal metavars are also defined, for example, `$TYPE a = 0;` query could be used to match `bool a = 0;`.:

- `$TYPE`: It will match any type, such as `uint256`, `bool`, `bytes`.
- `$VISIBILITY`: It will match any function visibility, such as `public`, `external`, `internal`.
- `$STATE`: It will match any function mutability, such as `view`, `pure`.
- `$STORAGE`: It will match any type memory storage, such as `memory`, `storage`, `calldata`.
- `$VERSION`: It will match any pragma solidity version, such as `0.8.4`, `>=7.0.0`.
- `$EXPERIMENTAL`: It will match any pragma experimental string, such as `ABIEncoderV2`, `SMTChecker`.

Once a metavar is used, the literal value that reference to is keep on the placeholder. This means, that further references to the same metavar do hold the last value. Sometimes, we do want to use those internal vars to match complex conditions. The previous stated listing, does match any function with any name, that takes one parameter of any type and returns a value of the same type. This function should call any function that takes the passed argument and the returned call value should be stored on a variable and returned from the main function. 

If we now want to have the same query but with the possibility of the returned value being the same or different type as the parameter type that would not work. The parameter type and return type should be the same as defined on the query. 

Thats why, internal metavars do support enumeration by appending a number to the definition. And as previous metavars identifiers they will hold the first value and all possible values that it matches. As an example, following snippet could be rewritten to support different argument and return values as shown in snippet below it, which defines two different any type, `$TYPE0` and `$TYPE1`.


``` 
contract $CONTRACT {

  function $FNC1($TYPE $VAR1) $VISIBILITY returns($TYPE){
    ...
    $TYPE $VAR2 = $FNC2($VAR1);
    ...
    return $VAR2;
  }
}
```

``` 
contract $CONTRACT {

  function $FNC1($TYPE0 $VAR1) $VISIBILITY returns($TYPE1){
    ...
    $TYPE1 $VAR2 = $FNC2($VAR1);
    ...
    return $VAR2;
  }
}
```