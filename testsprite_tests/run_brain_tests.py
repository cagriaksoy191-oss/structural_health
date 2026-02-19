import unittest
import sys
import os

# Import specific brain test modules
import TC006_verify_building_year_scoring
import TC007_verify_floor_count_penalties
import TC008_verify_low_concrete_penalty
import TC009_verify_fuzzy_logic_consistency
import TC010_edge_case_years
import TC011_edge_case_floors
import TC012_edge_case_corrosion
import TC015_earthquake_risk_map_verification
import TC016_critical_facility_logic
import TC017_structural_defect_combinations
import TC018_service_failure_handling

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests from brain modules
    suite.addTests(loader.loadTestsFromModule(TC006_verify_building_year_scoring))
    suite.addTests(loader.loadTestsFromModule(TC007_verify_floor_count_penalties))
    suite.addTests(loader.loadTestsFromModule(TC008_verify_low_concrete_penalty))
    suite.addTests(loader.loadTestsFromModule(TC009_verify_fuzzy_logic_consistency))
    suite.addTests(loader.loadTestsFromModule(TC010_edge_case_years))
    suite.addTests(loader.loadTestsFromModule(TC011_edge_case_floors))
    suite.addTests(loader.loadTestsFromModule(TC012_edge_case_corrosion))
    suite.addTests(loader.loadTestsFromModule(TC015_earthquake_risk_map_verification))
    suite.addTests(loader.loadTestsFromModule(TC016_critical_facility_logic))
    suite.addTests(loader.loadTestsFromModule(TC017_structural_defect_combinations))
    suite.addTests(loader.loadTestsFromModule(TC018_service_failure_handling))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
