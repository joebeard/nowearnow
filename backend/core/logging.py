import logging
import re


class RedactLinks(logging.Filter):
    """Keep bearer URLs out of Django request/access logs, including error paths."""

    def filter(self, record):
        record.msg = re.sub(
            r"(/(?:api/v1/)?(?:scan|s|invitations)/)[^\s/?]+", r"\1[redacted]", record.getMessage()
        )
        record.args = ()
        return True
