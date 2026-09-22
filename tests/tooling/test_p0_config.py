# Checks only the BEHAVIOR.md B16 starting defaults against the P0 scaffold.
# Prevents unrelated specification tables or diagnostic constants hiding drift.
# Run with Python unittest; this is source validation, not behavior or board proof.
from decimal import Decimal
from pathlib import Path
import re
import unittest


PROJECT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DEFAULTS = {
    'P0_SCROLL_MS': 100,
    'P0_COUNTER_MS': 1000,
    'P0_JITTER_SAMPLES': 60000,
    'P0_JITTER_HISTOGRAM_US': 1000,
    'P0_MONITOR_TIMEOUT_US': 100000,  # D-062 fixed-counter diagnostic deadline.
    'P0_MONITOR_BAUD_BPS': 115200,  # D-062 existing internal UART configuration.
    'P0_ADC_SAMPLES': 1000,  # D-063 exact startup-only A0 call count.
    'P0_ADC_PIN': 14,  # D-063 installed A0 diagnostic index; not PINMAP acceptance.
    'P0_GPIO_SAMPLES': 400,  # D-064 exact startup-only GPIO sample count.
    'P0_GPIO_PIN': 50,  # D-064 installed internal LED index; not PINMAP acceptance.
}
BEHAVIOR_EXTRA_DEFAULTS = {
    'VBAT_FILTER_MS': 1000,  # B6 one-second time constant.
    'REFLANK_WINDOW_MS': 10000,  # B11.3 existing ten-second rolling window.
    'LOG_EVENT_CAPACITY': 4096,  # B15/D-028 first-event retention capacity.
    'EDGE_SIDE_TURN_DEG': 45,  # Existing B4.2 side-row/B4.3 pivot, not new tuning.
    'TICK_OVERRUN_PERCENT': 1,  # Existing B14 strict-over-one-percent warning.
    'RECENT_EDGE_MS': 5000,  # Existing B8/B11 recent-escape interval.
    'SEARCH_SCAN_DEG': 360,  # Existing B8 full-scan angle.
    'MODE_SHORT_MS': 600,  # Existing B13 strict short-press bound, centralized by D-058.
}
BEHAVIOR_EXTRA_FLOAT_DEFAULTS = {'EDGE_FWD_INNER_RATIO': Decimal('0.70')}  # B4.2/D-021.
COUNTDOWN_SERVICE_DEFAULTS = {  # B3 and human-approved D-024; not physical tuning.
    'CAL_START_MS': 1500,
    'CAL_END_MS': 4500,
    'CAL_MIN_SAMPLES': 2,
    'COUNTDOWN_LINE_WARN_MS': 1000,
    'COUNTDOWN_SNAPSHOT_MS': 300,
}


def b16_defaults():
    document = (PROJECT / 'docs/BEHAVIOR.md').read_text(encoding='utf-8')
    heading = re.search(r'^## B16\. Tunables[^\n]*\n', document, re.MULTILINE)
    if heading is None:
        raise AssertionError('BEHAVIOR.md B16 heading is missing')
    section = re.split(r'^## ', document[heading.end():], maxsplit=1,
                       flags=re.MULTILINE)[0]
    defaults = {}
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        if not cells or not re.fullmatch(r'[A-Z][A-Z0-9_]*(?:\[\d+\])?', cells[0]):
            continue
        name, default = cells[:2]
        if name in defaults:
            raise AssertionError(f'Duplicate B16 row: {name}')
        defaults[name] = default
    return defaults


def config_declarations():
    source = (PROJECT / 'src/config.h').read_text(encoding='utf-8')
    source = re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.DOTALL)
    declarations = {}
    pattern = r'\bconstexpr\s+(\S+)\s+(\w+)(\[\d+\])?\s*=\s*([^;]+);'
    for kind, name, extent, initializer in re.findall(pattern, source):
        key = name + extent
        if key in declarations:
            raise AssertionError(f'Duplicate config declaration: {key}')
        declarations[key] = (kind, initializer.strip())
    return declarations


def number(token):
    token = re.sub(r'[uUfF]$', '', token.strip())
    return Decimal(int(token, 16)) if token.lower().startswith('0x') else Decimal(token)


class P0ConfigTests(unittest.TestCase):
    def test_b16_scope_has_76_defaults_and_excludes_b5_bearing_rows(self):
        defaults = b16_defaults()
        self.assertEqual(76, len(defaults))
        self.assertNotIn('FC', defaults)
        self.assertEqual('5000', defaults['COUNTDOWN_MS'])
        self.assertEqual('1', defaults['MODE_DEFAULT'])

    def test_only_b16_and_explicit_spec_diagnostic_defaults_are_declared(self):
        expected = (set(b16_defaults()) | set(DIAGNOSTIC_DEFAULTS) |
                    set(BEHAVIOR_EXTRA_DEFAULTS) | set(BEHAVIOR_EXTRA_FLOAT_DEFAULTS) |
                    set(COUNTDOWN_SERVICE_DEFAULTS))
        self.assertEqual(expected, set(config_declarations()))

    def test_b16_literal_categories_and_array_extent_are_preserved(self):
        declarations = config_declarations()
        for name, default in b16_defaults().items():
            with self.subTest(constant=name):
                self.assertIn(name, declarations)
                # B16 decimal defaults need floats; whole-number defaults use
                # the scaffold's fixed-width unsigned type, per AGENTS section 6.
                expected_type = 'float' if '.' in default else 'std::uint32_t'
                self.assertEqual(expected_type, declarations[name][0])
        for name in DIAGNOSTIC_DEFAULTS:
            with self.subTest(diagnostic=name):
                self.assertEqual('std::uint32_t', declarations[name][0])

    def test_p0_diagnostic_defaults_are_explicit_and_unchanged(self):
        declarations = config_declarations()
        for name, expected in DIAGNOSTIC_DEFAULTS.items():
            with self.subTest(diagnostic=name):
                self.assertEqual(expected, number(declarations[name][1]))

    def test_explicit_behavior_text_defaults_match_spec(self):
        declarations = config_declarations()
        for name, expected in BEHAVIOR_EXTRA_DEFAULTS.items():
            self.assertEqual('std::uint32_t', declarations[name][0])
            self.assertEqual(expected, number(declarations[name][1]))

    def test_b4_forward_inner_ratio_matches_seventy_percent(self):
        declarations = config_declarations()
        for name, expected in BEHAVIOR_EXTRA_FLOAT_DEFAULTS.items():
            self.assertEqual('float', declarations[name][0])
            self.assertEqual(expected, number(declarations[name][1]))

    def test_b3_service_defaults_match_d024(self):
        declarations = config_declarations()
        for name, expected in COUNTDOWN_SERVICE_DEFAULTS.items():
            with self.subTest(constant=name):
                self.assertEqual('std::uint32_t', declarations[name][0])
                self.assertEqual(expected, number(declarations[name][1]))

    def test_each_b16_default_matches_its_documented_value(self):
        declarations = config_declarations()
        for name, default in b16_defaults().items():
            with self.subTest(constant=name):
                initializer = declarations[name][1]
                if default.endswith(' each'):
                    count = int(re.search(r'\[(\d+)\]$', name).group(1))
                    self.assertTrue(initializer.startswith('{') and initializer.endswith('}'))
                    actual = [number(value) for value in initializer[1:-1].split(',')]
                    self.assertEqual([number(default[:-5])] * count, actual)
                else:
                    self.assertEqual(number(default), number(initializer))


if __name__ == '__main__':
    unittest.main()
