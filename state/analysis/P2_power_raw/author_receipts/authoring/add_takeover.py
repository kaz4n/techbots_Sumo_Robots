from pathlib import Path
p=Path('tests/tooling/test_power_unoq.py');s=p.read_text();s=s.replace('    def test_b5_native_contract(self):','    def test_b5_partial_claim_is_reset_only(self):\n        self.execute(self.variant(case="takeover_cases.cc"))\n\n    def test_b5_native_contract(self):');p.write_text(s)
