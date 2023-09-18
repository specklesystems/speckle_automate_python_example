from automate_sdk import AutomationResult, ObjectResult, ObjectResultLevel

res = AutomationResult()


res.object_results["foobar"].append(
    ObjectResult(level=ObjectResultLevel.ERROR, status_message="foobar")
)

print(res.model_dump(by_alias=True))
