#coding: utf-8
# Name: WeatherAnywhereScene.py
# Author: John Coomler
# v1.0: 03/01/2015 to 03/04/2015-Created
'''
Inspiration behind this was @cclauss's
script,'WeatherAnywhereView.py in this
repository. I wanted the ability to
add weather icons and have them scroll
with the text, so a scene seemed to be the
best answer.
Basic scrolling example was by Dalorbi on
the forums @ http://omz-forums.appspot.
com/pythonista/post/4998190881308672.
Ability for scrolling scene with inertia
added by hroe @ https://gist.github.com
/henryroe/6724117.

Issues: Line and image placements are hard
coded so they don't auto adjust if text
size is changed from the current 12 pts.
Increasing text size results in missing
text for last 2 days of extended forecast.
'''
import console
import scene
from scene import *
from math import exp
from threading import Thread
import datetime
import requests
import WeatherAnywhere as wa

# Use functions in WeatherAnywhere.py to get the needed weather specs & icons
def get_weather_now(w):
  w = wa.get_current_weather(w)
  fmt = '{}'
  return fmt.format(w)

def get_forecast(f):
  f = wa.get_forecast(f)
  fmt = '{}\n\nWeather information provided by openweathermap.org'
  return fmt.format(f)

def get_icons(w,f):
  icons = wa.get_weather_icons(w,f)
  return icons

print('='*20)
try:
  w,f=wa.pick_your_weather()
except requests.ConnectionError:
  print('=' * 20)
  sys.exit('Weather servers are busy. Try again in a few minutes...')

weather_now = get_weather_now(w)
forecast = get_forecast(f)
weather_icons = get_icons(w,f)

# Y coordinates for placement of icons
y=[180,-20,-155,-292,-430,-568,-705,-845]

class MyScene (Scene):
  def setup(self):
    self.dx = self.size.w / 2
    self.dy = self.size.h / 2 + 10
    self.xy_velocity = None
    self.velocity_decay_timescale_seconds = 0.4
    self.max_retained_touch_points = 6
    self.min_velocity_points_per_second = 50
    self.cur_touch = None
    # Load icons before scene opens
    self.images = [scene.load_image_file(icon) for icon in weather_icons]

  def draw(self):
    if self.xy_velocity is not None and self.cur_touch is None:
      #self.dx += self.xy_velocity[0] * self.dt
      self.dy += self.xy_velocity[1] * self.dt
      decay = exp( - self.dt / self.velocity_decay_timescale_seconds )
      self.xy_velocity = (self.xy_velocity[0] * decay, self.xy_velocity[1] * decay)
      if ((abs(self.xy_velocity[0]) <= self.min_velocity_points_per_second) and (abs(self.xy_velocity[1]) <= self.min_velocity_points_per_second)):
        self.xy_velocity = None

    # Dark red
    background(.5, 0, 0)
    translate(self.dx, self.dy)
    fill(1, 1, 1)
    stroke(1, 1, 1)
    # Line thickness
    stroke_weight(1)

    # Vertical lines
    line(-150,-931,-150,255)
    line(150,-931,150,255)

    # Horizontal lines
    line(-150,255,150,255)
    line(-150,230,150,230)
    line(-150,60,150,60)
    line(-150,35,150,35)
    line(-150,-104,150,-104)
    line(-150,-241,150,-241)
    line(-150,-379,150,-379)
    line(-150,-517,150,-517)
    line(-150,-655,150,-655)
    line(-150,-794,150,-794)
    line(-150,-931,150,-931)

    '''
    Text will be white by default and
    images drawn in their natural colors
    unless tint(r,g,b,a) function is used
    '''
    scene.text(weather_now,font_size=12,x=-140,y=250, alignment=3)
    scene.text(forecast,font_size=12,x=-140,y=55, alignment=3)

    # Insert icons into scene
    for i, image in enumerate(self.images):
      scene.image(image,75,y[i])

  # Routines to handle inertia scrolling
  def touch_began(self, touch):
    if self.cur_touch is None:
      self.cur_touch = touch.touch_id
      self.xy_velocity = None
      self.touch_log = []

  def touch_moved(self, touch):
    if touch.touch_id == self.cur_touch:
      # Killed left-rt, rt-left scrolling
      #self.dx += touch.location.x - touch.prev_location.x
      self.dy += touch.location.y - touch.prev_location.y
      self.touch_log.append((datetime.datetime.utcnow(), touch.location))
      self.touch_log = self.touch_log[-self.max_retained_touch_points:]

  def touch_ended(self, touch):
    if touch.touch_id == self.cur_touch:
      self.xy_velocity = None
      if len(self.touch_log) >= 2:
        dt = (self.touch_log[-1][0] - self.touch_log[0][0]).total_seconds()
        if dt > 0:
          x_velocity = (self.touch_log[-1][1].x - self.touch_log[0][1].x) / dt
          y_velocity = (self.touch_log[-1][1].y - self.touch_log[0][1].y) / dt
          self.xy_velocity = (x_velocity, y_velocity)
      self.cur_touch = None

run(MyScene())
