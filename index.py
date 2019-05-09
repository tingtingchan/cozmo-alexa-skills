import cozmo
  from flask import Flask


def cozmo_program(robot: cozmo.robot.Robot):
robot.say_text("Hello World").wait_for_completed()

app = Flask(__name__)

@app.route("/")
def hello():
return "Hello World!"

@app.route("/hello")
def say_hello():
cozmo.run_program(cozmo_program)
return "Cozmo says hello!"

