"""Data structure for storing tabulated results.

This module defines a data structure, Table, that stores the
output of a .tabulate() operation.  Typically, Table stores
the possible outcomes and their counts or relative frequencies.
"""
from .base import Arithmetic


TABLE_TEMPLATE = '''
<table>
  <thead>
    <th width="80%">Outcome</th>
    <th width="20%">Value</th>
  </thead>
  <tbody>
    {table_body}
  </tbody>
</table>
'''


def _get_row_html(outcome, count):
    return "<tr><td>%s</td><td>%s</td></tr>" % (outcome, count)


class Table(dict, Arithmetic):

    def __init__(self, hash_map, outcomes=None):
        self.outcomes = outcomes
        if outcomes is None:
            for outcome, count in hash_map.items():
                self[outcome] = count
        else:
            for outcome in outcomes:
                self[outcome] = (
                    hash_map[outcome] if outcome in hash_map
                    else 0
                )
                
    def ordered_keys(self):
        # get keys in order
        if self.outcomes is None:
            keys = list(self.keys())
            try:
                keys.sort()
            except Exception:
                pass
        else:
            # preserve ordering of outcomes, if specified
            keys = self.outcomes

        return keys
    
    def __repr__(self):
        keys = self.ordered_keys()
        keys_strings = [str(x) for x in keys]
        max_key_length = len(max(keys_strings, key=len))
        outcome_colname_length = len('Outcome')

        table_rows = []

        for i, key in enumerate(keys):
            if len(str(key)) <= outcome_colname_length:
                outcome_space = ' ' * (outcome_colname_length - len(str(key)))
            else:
                outcome_space = ' ' * (max_key_length - len(str(key)))
            table_rows.append(f"{key}{outcome_space} {self[key]}")

            if i >= 18:
                last_outcome = str(keys[-1])
                last_value = str(self[keys[-1]])
                table_rows.append(f"{'.' * len(last_outcome)}{outcome_space} "
                                  f"{'.' * len(last_value)}")
                table_rows.append(f"{last_outcome}{outcome_space} "
                                  f"{last_value}")
                break

        if max_key_length <= outcome_colname_length:
            outcome_header_space = ' '
            total_row_space = ' ' * (outcome_colname_length - len('Total'))
        else:
            outcome_header_space = ' ' * (max_key_length -
                                          outcome_colname_length + 1)
            total_row_space = ' ' * (max_key_length - len('Total'))

        total = str(sum(self.values()))
        table_rows.append(f"{total_row_space}Total {total}")
        table_rows.insert(0, f"Outcome{outcome_header_space}Value")

        return '\n'.join(table_rows)

    def _repr_html_(self):
        keys = self.ordered_keys()

        # get HTML for table body
        table_body = ""
        for i, key in enumerate(keys):
            table_body += _get_row_html(key, self[key])
            # if we've already printed 19 rows, skip to end
            if i >= 18:
                table_body += _get_row_html("...", "...")
                table_body += _get_row_html(keys[-1], self[keys[-1]])
                break
        total = str(sum(self.values()))
        table_body += _get_row_html("<b>Total</b>", "<b>%s</b>" % total)

        # return HTML for entire table
        return TABLE_TEMPLATE.format(table_body=table_body)

    # The Arithmetic superclass will use this to define all of the
    # usual arithmetic operations (e.g., +, -, *, /, **, ^, etc.).
    def _operation_factory(self, op):

        def _op_func(self, other):
            return Table(
                {outcome: op(count, other) for outcome, count in self.items()},
                self.outcomes
            )

        return _op_func
