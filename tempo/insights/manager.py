import asyncio

from ..serve.metadata import DEFAULT_INSIGHTS_REQUEST_MODES, InsightRequestModes, InsightsPayload, InsightsTypes, DEFAULT_INSIGHTS_TYPE
from ..utils import logger
from .worker import start_insights_worker_from_async, start_insights_worker_from_sync
from tempo.magic import t

class InsightsManager:
    def __init__(
        self,
        worker_endpoint: str = "",
        batch_size: int = 1,
        parallelism: int = 1,
        retries: int = 3,
        window_time: int = None,
        mode_type: InsightRequestModes = DEFAULT_INSIGHTS_REQUEST_MODES,
        in_asyncio: bool = False,
    ):
        args = (
            worker_endpoint,
            batch_size,
            parallelism,
            retries,
            window_time,
        )
        logger.info(f"Initialising Insights Manager with Args: {args}")
        if worker_endpoint:
            if in_asyncio:
                logger.debug("Initialising async insights worker")
                self._q = start_insights_worker_from_async(*args)

                def log(self, data: any, insights_type: InsightsTypes = DEFAULT_INSIGHTS_TYPE):
                    payload = self._to_payload(data, insights_type=insights_type)
                    asyncio.create_task(self._q.put(payload))

                self.log = log.__get__(self, self.__class__)  # type: ignore # pylint: disable=E1120,E1111
                logger.debug("Async worker set up")
            else:
                logger.debug("Initialising sync insights worker")
                self._q = start_insights_worker_from_sync(*args)  # type: ignore

                def log(self, data, insights_type: InsightsTypes = DEFAULT_INSIGHTS_TYPE):
                    payload = self._to_payload(data, insights_type=insights_type)
                    self._q.put(payload)

                self.log = log.__get__(self, self.__class__)  # type: ignore # pylint: disable=E1120,E1111
                logger.debug("Sync worker set up")
        else:
            logger.warning("Insights Manager not initialised as empty URL provided.")

    def _to_payload(self, data: any, insights_type: InsightsTypes = DEFAULT_INSIGHTS_TYPE) -> InsightsPayload:
        return InsightsPayload(
            data=data,
            request_id=t.payload.request_id,  # pylint: disable=no-member
            insights_type=insights_type,
        )

    def log(self, data, insights_type: InsightsTypes = DEFAULT_INSIGHTS_TYPE):  # pylint: disable=E0202
        """
        By default function doesn't have any logic unless an endpoint is provided.
        """
        logger.warning("Attempted to log parameter but called manager directly, see documentation [TODO]")

    def log_request(self):  # pylint: disable=E0202
        """
        By default function doesn't have any logic unless an endpoint is provided.
        """
        logger.warning("Attempted to log request but called manager directly, see documentation [TODO]")

    def log_response(self):  # pylint: disable=E0202
        """
        By default function doesn't have any logic unless an endpoint is provided.
        """
        logger.warning("Attempted to log response but called manager directly, see documentation [TODO]")
