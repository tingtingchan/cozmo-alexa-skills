#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Hello World

Make Cozmo say 'Hello World' in this simple Cozmo SDK example program.
'''

import cozmo
from flask import Flask


app = Flask(__name__)

def cozmo_hello(name: str):
    def cozmo_hello_inner(robot: cozmo.robot.Robot):
        robot.say_text('Hello ' + name).wait_for_completed()
    return cozmo_hello_inner

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/hello/<name>")
@app.route("/hello")
def say_hello(name="world"):
    cozmo.run_program(cozmo_hello(name))
    return "Cozmo says hello {}!".format(name)

if __name__ == '__main__':
    app.run(debug=True)
