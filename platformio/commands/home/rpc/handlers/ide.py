# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

from ajsonrpc.core import JSONRPC20DispatchException

from platformio.compat import aio_get_running_loop


class IDERPC:
    def __init__(self):
        self._cmd_queue = []
        self._result_queue = {}

    async def listen_commands(self):
        self._cmd_queue.append(aio_get_running_loop().create_future())
        return await self._cmd_queue[-1]

    async def send_command(self, command, params=None):
        if not self._cmd_queue:
            raise JSONRPC20DispatchException(
                code=4005, message="PIO Home IDE agent is not started"
            )
        cmd_id = None
        while self._cmd_queue:
            cmd_id = f"ide-{command}-{time.time()}"
            self._cmd_queue.pop().set_result(
                {
                    "id": cmd_id,
                    "method": command,
                    "params": params,
                }
            )
        if not cmd_id:
            return
        self._result_queue[cmd_id] = aio_get_running_loop().create_future()
        return await self._result_queue[cmd_id]

    def on_command_result(self, cmd_id, value):
        self._result_queue[cmd_id].set_result(value)
