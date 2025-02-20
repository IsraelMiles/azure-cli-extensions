# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from typing import Any, Optional, TYPE_CHECKING

from azure.mgmt.core import AsyncARMPipelineClient
from msrest import Deserializer, Serializer

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential

from ._configuration import StreamAnalyticsManagementClientConfiguration
from .operations import Operations
from .operations import StreamingJobsOperations
from .operations import InputsOperations
from .operations import OutputsOperations
from .operations import TransformationsOperations
from .operations import FunctionsOperations
from .operations import SubscriptionsOperations
from .. import models


class StreamAnalyticsManagementClient(object):
    """Stream Analytics Client.

    :ivar operations: Operations operations
    :vartype operations: stream_analytics_management_client.aio.operations.Operations
    :ivar streaming_jobs: StreamingJobsOperations operations
    :vartype streaming_jobs: stream_analytics_management_client.aio.operations.StreamingJobsOperations
    :ivar inputs: InputsOperations operations
    :vartype inputs: stream_analytics_management_client.aio.operations.InputsOperations
    :ivar outputs: OutputsOperations operations
    :vartype outputs: stream_analytics_management_client.aio.operations.OutputsOperations
    :ivar transformations: TransformationsOperations operations
    :vartype transformations: stream_analytics_management_client.aio.operations.TransformationsOperations
    :ivar functions: FunctionsOperations operations
    :vartype functions: stream_analytics_management_client.aio.operations.FunctionsOperations
    :ivar subscriptions: SubscriptionsOperations operations
    :vartype subscriptions: stream_analytics_management_client.aio.operations.SubscriptionsOperations
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param subscription_id: The ID of the target subscription.
    :type subscription_id: str
    :param str base_url: Service URL
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no Retry-After header is present.
    """

    def __init__(
        self,
        credential: "AsyncTokenCredential",
        subscription_id: str,
        base_url: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        if not base_url:
            base_url = 'https://management.azure.com'
        self._config = StreamAnalyticsManagementClientConfiguration(credential, subscription_id, **kwargs)
        self._client = AsyncARMPipelineClient(base_url=base_url, config=self._config, **kwargs)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        self._deserialize = Deserializer(client_models)

        self.operations = Operations(
            self._client, self._config, self._serialize, self._deserialize)
        self.streaming_jobs = StreamingJobsOperations(
            self._client, self._config, self._serialize, self._deserialize)
        self.inputs = InputsOperations(
            self._client, self._config, self._serialize, self._deserialize)
        self.outputs = OutputsOperations(
            self._client, self._config, self._serialize, self._deserialize)
        self.transformations = TransformationsOperations(
            self._client, self._config, self._serialize, self._deserialize)
        self.functions = FunctionsOperations(
            self._client, self._config, self._serialize, self._deserialize)
        self.subscriptions = SubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize)

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "StreamAnalyticsManagementClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)
