from .models import Step

CI_CD_STEPS = [("checkout", "source"), ("install_dependencies", "build"), ("lint", "quality"), ("unit_tests", "test"), ("security_scan", "security"), ("build_container", "build"), ("deploy_aws", "deploy")]

async def plan_pipeline(goal: str | None = None) -> list[Step]:
    steps = [Step(name=name, kind=kind, requires_approval=kind == "deploy") for name, kind in CI_CD_STEPS]
    if goal and "skip deploy" in goal.lower():
        steps = [step for step in steps if step.kind != "deploy"]
    return steps
