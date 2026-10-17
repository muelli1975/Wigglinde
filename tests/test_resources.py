import unittest
from wigglinde.resources import plan_views,GIB

class RenderResourcesTests(unittest.TestCase):
    def test_available_cpu_capacity_is_used_when_memory_allows(self):
        p=plan_views(320,160,31,12,32*GIB,24*GIB)
        self.assertEqual(p['workers'],12)
        self.assertLessEqual(p['workers']*p['threads_per_view'],12)

    def test_high_resolution_limits_concurrency_not_quality(self):
        p=plan_views(3840,2160,31,16,32*GIB,14*GIB)
        self.assertEqual(p['workers'],5)
        self.assertLessEqual(p['estimated_bytes_per_view']*p['workers'],p['memory_budget_bytes'])

    def test_near_exhausted_or_unknown_memory_keeps_serial_operation(self):
        for available in (None,0,64*1024**2):
            p=plan_views(1620,1080,31,12,32*GIB,available)
            self.assertEqual(p['workers'],1)

    def test_short_sequences_do_not_create_unused_workers(self):
        p=plan_views(320,160,3,16,32*GIB,24*GIB)
        self.assertEqual(p['workers'],3)
        self.assertLessEqual(p['workers']*p['threads_per_view'],16)
