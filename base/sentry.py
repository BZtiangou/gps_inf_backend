import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


sentry_dsn = os.environ.get("SENTRY_DSN", None)
if sentry_dsn is not None:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            DjangoIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
