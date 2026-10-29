from .config import get_settings

def enqueue(workflow_id: str) -> str:
    settings = get_settings()
    if settings.queue_backend == "sqs" and settings.sqs_queue_url:
        import boto3
        boto3.client("sqs", region_name=settings.aws_region).send_message(QueueUrl=settings.sqs_queue_url, MessageBody=workflow_id)
        return "sqs"
    from .worker import execute_workflow
    execute_workflow.delay(workflow_id)
    return "celery"
