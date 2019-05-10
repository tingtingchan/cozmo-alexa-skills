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
from cozmo.util import distance_mm, speed_mmps
from flask import Flask


app = Flask(__name__)


def cozmo_hello(name: str):
    def cozmo_hello_inner(robot: cozmo.robot.Robot):
        robot.say_text('Hello ' + name).wait_for_completed()
    return cozmo_hello_inner


def move_forward(robot: cozmo.robot.Robot):
    robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()


def move_backward(robot: cozmo.robot.Robot):
    robot.drive_straight(distance_mm(-150), speed_mmps(50)
                         ).wait_for_completed()


def cube_stack(robot: cozmo.robot.Robot):
    # Attempt to stack 2 cubes

    # Lookaround until Cozmo knows where at least 2 cubes are:
    lookaround = robot.start_behavior(
        cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(
        num=2, object_type=cozmo.objects.LightCube, timeout=60)
    lookaround.stop()

    if len(cubes) < 2:
        print("Error: need 2 Cubes but only found", len(cubes), "Cube(s)")
    else:
        # Try and pickup the 1st cube
        current_action = robot.pickup_object(cubes[0], num_retries=3)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Pickup Cube failed: code=%s reason='%s' result=%s" %
                  (code, reason, result))
            return

        # Now try to place that cube on the 2nd one
        current_action = robot.place_on_object(cubes[1], num_retries=3)
        current_action.wait_for_completed()
        if current_action.has_failed:
            code, reason = current_action.failure_reason
            result = current_action.result
            print("Place On Cube failed: code=%s reason='%s' result=%s" %
                  (code, reason, result))
            return

        print("Cozmo successfully stacked 2 blocks!")


@app.route("/")
def hello():
    return "Welcome to the Cozmo API Server!"


@app.route("/hello/<name>")
@app.route("/hello")
def say_hello(name="world"):
    cozmo.run_program(cozmo_hello(name))
    return "Cozmo says hello {}!".format(name)


@app.route("/move/<direction>")
def move(direction):
    if direction == "forward":
        cozmo.run_program(move_forward)
        return "Moved " + direction
    elif direction == "backward":
        cozmo.run_program(move_backward)
        return "Moved " + direction
    return direction + " is not a recognized direction"


@app.route("/cubestack")
def cubeStack():
    cozmo.run_program(cube_stack)
    return "Cozmo is stacking cubes"


if __name__ == '__main__':
    app.run(debug=True)
