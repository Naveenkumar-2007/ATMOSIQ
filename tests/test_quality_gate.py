from atmosiq.components.model_evaluation import ModelEvaluation
from atmosiq.entity.config_entity import ModelEvaluationConfig, TrainingPipelineConfig


def _evaluator(project_root):
    cfg = ModelEvaluationConfig(TrainingPipelineConfig())
    return ModelEvaluation(None, [], None, cfg)


def test_gate_blocks_failing_candidate(project_root):
    ev = _evaluator(project_root)
    board = [{"model": "xgboost", "task": "temperature", "horizon": 24, "mae": 1.0, "rmse": 1.5, "mase": 1.2, "skill_vs_persistence": -0.1}]
    gate = ev._quality_gate(board)
    assert gate["passed"] is False


def test_gate_allows_passing_candidate(project_root):
    ev = _evaluator(project_root)
    board = [{"model": "xgboost", "task": "temperature", "horizon": 24, "mae": 1.0, "rmse": 1.5, "mase": 0.5, "skill_vs_persistence": 0.2}]
    gate = ev._quality_gate(board)
    assert gate["passed"] is True
