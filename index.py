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
import asyncio
import time

from flask import Flask
from cozmo.util import degrees, distance_mm, speed_mmps


app = Flask(__name__)


async def cozmo_opening(robot: cozmo.robot.Robot):
    r = await robot.say_text(
        'Hello, I am Cozmo. Welcome to the Hack-a-thon.').wait_for_completed()
    return r


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


def drive_to_charger(robot: cozmo.robot.Robot):
    robot.say_text("I am going to take a nap.").wait_for_completed()

    '''The core of the drive_to_charger program'''

    # If the robot was on the charger, drive them forward and clear of the charger
    if robot.is_on_charger:
        # drive off the charger
        robot.drive_off_charger_contacts().wait_for_completed()
        robot.drive_straight(distance_mm(
            100), speed_mmps(50)).wait_for_completed()
        # Start moving the lift down
        robot.move_lift(-3)
        # turn around to look at the charger
        robot.turn_in_place(degrees(180)).wait_for_completed()
        # Tilt the head to be level
        robot.set_head_angle(degrees(0)).wait_for_completed()
        # wait half a second to ensure Cozmo has seen the charger
        time.sleep(0.5)
        # drive backwards away from the charger
        robot.drive_straight(
            distance_mm(-60), speed_mmps(50)).wait_for_completed()

    # try to find the charger
    charger = None

    # see if Cozmo already knows where the charger is
    if robot.world.charger:
        if robot.world.charger.pose.is_comparable(robot.pose):
            print("Cozmo already knows where the charger is!")
            charger = robot.world.charger
        else:
            # Cozmo knows about the charger, but the pose is not based on the
            # same origin as the robot (e.g. the robot was moved since seeing
            # the charger) so try to look for the charger first
            pass

    if not charger:
        # Tell Cozmo to look around for the charger
        look_around = robot.start_behavior(
            cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try:
            charger = robot.world.wait_for_observed_charger(timeout=30)
            print("Found charger: %s" % charger)
        except asyncio.TimeoutError:
            print("Didn't see the charger")
        finally:
            # whether we find it or not, we want to stop the behavior
            look_around.stop()

    if charger:
        # Attempt to drive near to the charger, and then stop.
        action = robot.go_to_object(charger, distance_mm(65.0))
        action.wait_for_completed()
        print("Completed action: result = %s" % action)
        print("Done.")


@app.route("/")
def opening():
    cozmo.run_program(cozmo_opening)
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


@app.route("/drivetocharger")
def driveToCharger():
    # Cozmo can stay on charger for now
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    cozmo.run_program(drive_to_charger, use_viewer=True,
                      force_viewer_on_top=True)
    return "Cozmo is going to take a nap."


if __name__ == '__main__':
    app.run(debug=True)
