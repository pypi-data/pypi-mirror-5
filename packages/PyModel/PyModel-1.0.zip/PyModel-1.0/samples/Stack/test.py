"""
Stack tests
"""

cases = [
  ('Default random strategy, actions repeat',
   'pmt -n 10 -s 1 Stack'),

  ('ActionNameCoverage, Push and Pop alternate', 
   'pmt -n 10 -s 1 Stack -g ActionNameCoverage'),

  ('StateCoverage, repeat Push',
   'pmt -n 10 -s 1 Stack -g StateCoverage')
]
