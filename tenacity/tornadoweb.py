# -*- coding: utf-8 -*-
# Copyright 2017 Elisey Zanko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from tenacity import BaseRetrying
from tenacity import DoAttempt
from tenacity import DoSleep
from tenacity import RetryCallState

from tornado import gen


class TornadoRetrying(BaseRetrying):

    def __init__(self,
                 sleep=gen.sleep,
                 **kwargs):
        super(TornadoRetrying, self).__init__(**kwargs)
        self.sleep = sleep

    @gen.coroutine
    def call(self, fn, *args, **kwargs):
        self.begin(fn)

        call_state = RetryCallState(fn=fn, args=args, kwargs=kwargs)
        while True:
            do = self.iter(call_state=call_state)
            if isinstance(do, DoAttempt):
                call_state.attempt_number += 1
                try:
                    result = yield fn(*args, **kwargs)
                except BaseException:
                    call_state.set_exception(sys.exc_info())
                else:
                    call_state.set_result(result)
            elif isinstance(do, DoSleep):
                call_state.prepare_for_next_attempt()
                yield self.sleep(do)
            else:
                raise gen.Return(do)
