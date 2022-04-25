const standard_grammar = require('./tree-sitter-solidity/grammar.js');

function commaSep1(rule) {
  return seq(
      rule,
      repeat(
          seq(
              ',',
              rule
          )
      ),
      optional(','),
  );
}

function commaSep(rule) {
  return optional(commaSep1(rule));
}

// function colonSep1(rule) {
//   return seq(
//       rule,
//       repeat(
//           seq(
//               ';',
//               rule
//           )
//       ),
//       optional(';'),
//   );
// }

// function colonSep(rule) {
//   return optional(colonSep1(rule));
// }

module.exports = grammar(standard_grammar, {
  /*
    We can't rename the grammar to 'csharp' because it relies on a custom
    lexer ('scanner.c') which comes with the inherited grammar and provides
    a function 'tree_sitter_c_sharp_external_scanner_create'.
    The code generator ('tree-sitter generate') however expects this function
    name to match the grammar name, so if we rename it here to 'csharp',
    it will generate glue code that calls
    'tree_sitter_csharp_external_scanner_create'
    while only 'tree_sitter_c_sharp_external_scanner_create' is available.
  */
  name: 'solidity',

  rules: {

    // Entry point
    source_file: ($, previous) => {
      return choice(
        $._expression,
        previous
      );
    },

    // Allows to have:
    //  function () ... {}
    _function_extra: ($, previous) => {
      return choice(
        ...previous.members,
        $.ellipsis
      );
    },

    _contract_body: ($, previous) => {
      return choice(
        ...previous.members,
        $.ellipsis
      );
    },

    _primitive_type: ($, previous) => {
      return choice(
        ...previous.members,
        /\$TYPE([0-9]+)?/
      );
    },
    visibility: ($, previous) => {
      return choice(
        ...previous.members,
        /\$VISIBILITY([0-9]+)?/
      );
    },
    state_mutability: ($, previous) => {
      return choice(
        ...previous.members,
        /\$STATE([0-9]+)?/
      );
    },
    storage_location: ($, previous) => {
      return choice(
        ...previous.members,
        /\$STORAGE([0-9]+)?/
      );
    },

    pragma_versions: $ => choice(
      '$VERSION',
      repeat1(field("version_constraint", $._pragma_version_constraint)),
    ),

    solidity_directive: $ => seq(
      "solidity",
      $.pragma_versions,
    ),

    experimental_directives: $ => choice(
      '$EXPERIMENTAL',
      seq(optional('"'), $._experimental_directives, optional('"')),
    ),

    experimental_directive: $ => seq(
      "experimental",
      $.experimental_directives
    ),

    // Allows
    // function(..., uint256 x) {}
    parameter_list: $ => seq(
      '(',
      commaSep(choice($.parameter, $.ellipsis)),
      ')'
    ),

    // Metavariables
    //  identifier: ($, previous) => {
    //    return token(
    //      choice(
    //        previous,
    //        /\$[A-Z_][A-Z_0-9]*/
    //      )
    //    );
    //  },

    // Statement ellipsis: '...' not followed by ';'
    // expression_statement: ($, previous) => {
    //   return choice(
    //     previous,
    //     prec.right(101, seq($.ellipsis, optional(';'))),  // expression ellipsis
    //   );
    // },

    // Statement ellipsis: '...' not followed by ';'
    _statement: ($, previous) => {
      return choice(
        prec.right(100, seq($.ellipsis, ';')),  // expression ellipsis
        prec.right(100, $.ellipsis),  // statement ellipsis
        previous,
      );
    },

    _source_unit: ($, previous) => {
      return choice(
        ...previous.members,
        $._statement,
      );
    },

    // Expression ellipsis
     _expression: ($, previous) => {
       return choice(
         ...previous.members,
         $.ellipsis,
        //  $.deep_ellipsis
       );
     },

     _assignment_expression_left: ($, previous) => {
      return choice(
        ...previous.members,
        $.ellipsis,
      );
     },

     _lhs_expression: ($, previous) => {
      return choice(
        ...previous.members,
        prec.right(100, $.ellipsis),
      );
     },

    //  deep_ellipsis: $ => seq(
    //    '<...', $._expression, '...>'
    //  ),

    ellipsis: $ => '...',
  }
});
