"""New OpenStudio educational scaffold. SPDX-License-Identifier: Apache-2.0."""
import json, math
from pathlib import Path
UNITS = {'kg': ('mass', 1), 'g': ('mass', .001), 'tonne': ('mass', 1000), 't': ('mass', 1000), 'l': ('volume', 1), 'ml': ('volume', .001)}
def compare(left, right):
    for record in (left, right):
        if not isinstance(record.get('quantity'), (int, float)) or isinstance(record['quantity'], bool) or not math.isfinite(record['quantity']) or record['quantity'] < 0:
            raise ValueError('Quantity must be finite and nonnegative')
        if not record.get('entity') or not record.get('purpose'):
            raise ValueError('Entity and purpose are required')
    errors = [key for key in ('entity', 'purpose', 'currency') if left.get(key, '') != right.get(key, '')]
    a, b = UNITS.get(left['unit']), UNITS.get(right['unit'])
    if not a or not b:
        return {'status': 'mismatch' if errors else 'unresolved', 'differences': errors, 'unresolved': ['unit']}
    if a[0] != b[0]: errors.append('dimension')
    elif not math.isclose(left['quantity'] * a[1], right['quantity'] * b[1], rel_tol=1e-9, abs_tol=1e-9): errors.append('quantity')
    return {'status': 'mismatch' if errors else 'equivalent', 'differences': errors}
if __name__ == '__main__':
    data = json.loads((Path(__file__).parent / 'data/input.json').read_text(encoding='utf-8'))
    print(json.dumps(compare(data['left'], data['right']), ensure_ascii=False, indent=2))
