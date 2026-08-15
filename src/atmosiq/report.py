import os

from atmosiq.utils.main_utils.utils import read_json_file


def latest_artifact_dir():
    base = "artifacts"
    if not os.path.isdir(base):
        return None
    ts = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])
    return os.path.join(base, ts[-1]) if ts else None


def latest_leaderboard():
    d = latest_artifact_dir()
    p = os.path.join(d, "model_evaluation", "leaderboard.json") if d else None
    return read_json_file(p) if p and os.path.exists(p) else []


def print_leaderboard(task=None, horizon=None):
    rows = latest_leaderboard()
    if task:
        rows = [r for r in rows if r.get("task") == task]
    if horizon:
        rows = [r for r in rows if r.get("horizon") == horizon]
    if not rows:
        print("No leaderboard yet. Run: atmosiq train")
        return
    header = f"{'model':<20}{'task':<22}{'hor':>4}  {'mae':>8}  {'rmse':>8}  {'skill':>7}  {'pr_auc':>7}"
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r.get('model','-'):<20}{r.get('task','-'):<22}{r.get('horizon','-'):>4}  "
              f"{r.get('mae', float('nan')):>8.3f}  {r.get('rmse', float('nan')):>8.3f}  "
              f"{r.get('skill_vs_persistence', float('nan')):>7.2f}  {r.get('pr_auc', float('nan')):>7.2f}")


def print_champions(session):
    from atmosiq.db.models import ModelVersion
    champs = session.query(ModelVersion).filter_by(stage="Champion").order_by(ModelVersion.task, ModelVersion.horizon_hours).all()
    if not champs:
        print("No champions yet.")
        return
    print(f"{'task':<24}{'hor':>4}  {'model':<20}{'version':<16}")
    print("-" * 70)
    for c in champs:
        print(f"{c.task:<24}{c.horizon_hours:>4}  {c.model_name:<20}{c.id:<16}")
