# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Generator, Iterator

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import ExecutorError
from eva.models.storage.batch import Batch
from eva.parser.table_ref import AVTableRef, ImageTableRef, TableRef
from eva.plan_nodes.storage_plan import StoragePlan
from eva.storage.image_storage_engine import ImageStorageEngine
from eva.storage.sqlite_storage_engine import SQLStorageEngine
from eva.storage.video_storage_engine import OpenCVStorageEngine
from eva.utils.logging_manager import logger


class StorageExecutor(AbstractExecutor):
    def __init__(self, node: StoragePlan):
        super().__init__(node)

    def validate(self):
        pass

    def exec(self) -> Iterator[Batch]:
        try:
            if isinstance(self.node.table_ref, AVTableRef):
                return OpenCVStorageEngine().read(
                    self.node.table,
                    self.node.batch_mem_size,
                    predicate=self.node.predicate,
                    sampling_rate=self.node.sampling_rate,
                    sampling_type=self.node.sampling_type,
                    read_audio=self.node.table_ref.get_audio,
                    read_video=self.node.table_ref.get_video,
                )
            elif isinstance(self.node.table_ref, ImageTableRef):
                return ImageStorageEngine().read(self.node.table)
            elif isinstance(self.node.table_ref, TableRef):
                return SQLStorageEngine().read(
                    self.node.table, self.node.batch_mem_size
                )
            else:
                raise ExecutorError(
                    f"Unsupported TableType  {self.node.table.table_type} encountered"
                )
        except Exception as e:
            logger.error(e)
            raise ExecutorError(e)

    def __call__(self, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec()
