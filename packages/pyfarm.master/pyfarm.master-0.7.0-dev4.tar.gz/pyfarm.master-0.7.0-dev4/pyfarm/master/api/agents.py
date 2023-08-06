# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
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


from flask import request, abort
from flask.views import MethodView
from pyfarm.models.agent import AgentModel
from pyfarm.master.utility import JSONResponse


def try_or_fail(callable, error, description):
    try:
        return callable()
    except:
        abort(400)


# TODO: documentation
# TODO: on hold, POST/UPDATE for agents needs to be finished first
#class AgentsIndex(MethodView):
#    """
#    Endpoint for /agents
#    """
#    def get(self):
#        kwargs = {}
#        state = request.args.get("state")
#        if state:
#            state = try_or_fail(
#                lambda: int(state), "failed to convert `state`", None)
#
#        raise NotImplementedError("filtering from args")
#
#
#        # no parameters provided
#        data = dict(
#            (i.hostname, (i.id, i.state, i.freeram, i.ram, i.cpus))
#            for i in AgentModel.query)
#        return JSONResponse(data)
#
#    def post(self): # TODO: start here
#        pass
#
#    def update(self): # TODO: start here
#        pass