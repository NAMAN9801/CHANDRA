import pytest

pytest.importorskip("cv2", exc_type=ImportError)

import numpy as np

from OptimizedPSRAnalyzer import OptimizedPSRAnalyzer


def test_detect_psr_multi_returns_expected_masks():
    analyzer = OptimizedPSRAnalyzer()
    image = np.array(
        [
            [0, 20, 80, 120],
            [10, 60, 90, 140],
            [30, 70, 110, 200],
            [40, 85, 130, 255],
        ],
        dtype=np.uint8,
    )

    results = analyzer.detect_psr_multi(image)

    assert set(results.keys()) == {"threshold", "adaptive", "edges"}
    for mask in results.values():
        assert mask.shape == image.shape
        assert mask.dtype == np.uint8


def test_calculate_statistics_computes_image_and_coverage_values():
    analyzer = OptimizedPSRAnalyzer()
    image = np.array([[0, 10], [20, 30]], dtype=np.uint8)
    masks = {
        "threshold": np.array([[255, 0], [255, 0]], dtype=np.uint8),
        "adaptive": np.array([[255, 255], [0, 0]], dtype=np.uint8),
        "edges": np.array([[0, 0], [0, 0]], dtype=np.uint8),
    }

    stats = analyzer.calculate_statistics(image, masks)

    assert stats["image_stats"]["mean"] == 15.0
    assert stats["image_stats"]["min"] == 0
    assert stats["image_stats"]["max"] == 30
    assert stats["image_stats"]["dynamic_range"] == 30
    assert stats["psr_coverage"]["threshold"] == 50.0
    assert stats["psr_coverage"]["adaptive"] == 50.0
    assert stats["psr_coverage"]["edges"] == 0.0


def test_assess_landing_safety_marks_safe_when_conditions_met():
    analyzer = OptimizedPSRAnalyzer()
    terrain_analysis = {"roughness": np.full((3, 3), 10.0)}
    psr_results = {"edges": np.zeros((10, 10), dtype=np.uint8)}

    is_safe, explanation = analyzer.assess_landing_safety(terrain_analysis, {}, psr_results)

    assert is_safe is True
    assert "FINAL ASSESSMENT: SAFE for landing" in explanation


def test_assess_landing_safety_marks_unsafe_on_high_roughness_and_edges():
    analyzer = OptimizedPSRAnalyzer()
    terrain_analysis = {"roughness": np.full((3, 3), 100.0)}
    edges = np.zeros((10, 10), dtype=np.uint8)
    edges[:6, :] = 255
    psr_results = {"edges": edges}

    is_safe, explanation = analyzer.assess_landing_safety(terrain_analysis, {}, psr_results)

    assert is_safe is False
    assert "Terrain Roughness: UNSAFE" in explanation
    assert "Edge Density: UNSAFE" in explanation
    assert "FINAL ASSESSMENT: UNSAFE for landing" in explanation
