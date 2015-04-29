
import random

# EXAMPLE STATE MACHINE
class MantisBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.target = None

  def handle_event(self, message, details):

    if self.state is 'idle':

      if message == 'timer':
        # go to a random point, wake up sometime in the next 10 seconds
        world = self.body.world
        x, y = random.random()*world.width, random.random()*world.height
        self.body.go_to((x,y))
        self.body.set_alarm(random.random()*10)

      elif message == 'collide' and details['what'] == 'Slug':
        # a slug bumped into us; get curious
        self.state = 'curious'
        self.body.set_alarm(1) # think about this for a sec
        self.body.stop()
        self.target = details['who']

    elif self.state == 'curious':

      if message == 'timer':
        # chase down that slug who bumped into us
        if self.target:
          if random.random() < 0.5:
            self.body.stop()
            self.state = 'idle'
          else:
            self.body.follow(self.target)
          self.body.set_alarm(1)
      elif message == 'collide' and details['what'] == 'Slug':
        # we meet again!
        slug = details['who']
        slug.amount -= 0.01 # take a tiny little bite
    
class SlugBrain:

  def __init__(self, body):
    self.body = body
    self.selec_slug_attack = None
    self.selec_slug_build = None
    self.selec_slug_resource= None
    self.have_resource = False
    self.state = 'idle'
    self.tempstate = 'idle'
  def handle_event(self, message, details):

    if message == 'order':
      world = self.body.world
      if details == 'i':
        self.state = 'idle'      
      elif details == 'a':
        self.state = 'attack'
        self.selec_slug_attack = self.body
        self.body.set_alarm(1)
      elif details == 'b':
        self.state = 'build'
        self.selec_slug_build = self.body
        self.body.set_alarm(1)
      elif details == 'h':
        self.state = 'harvest' 
        self.selec_slug_resource = self.body
        self.body.set_alarm(1)
      elif (not isinstance (details, dict)) and not None and (not isinstance (details, str)): 
        self.state = 'goto'
        self.dest = details
        self.selec_slug_attack = None
        self.selec_slug_build = None
        self.selec_slug_resource= None
      else:
        print('invalue key. i for idle; a for attack; b for build; h for harvest; right_botton_down for go_to')

    if self.state == 'flee':
        self.target = self.body.find_nearest('Nest')
        self.body.go_to(self.target)
        if message == 'collide' and details['what'] == 'Nest':
          self.body.amount += 0.01
          if self.body.amount == 1:
            self.state = self.tempstate
            
    if self.state == 'goto':
      if self.body.amount < 0.5:
        self.state = 'flee'
        self.tempstate = 'idle'
      self.target = self.dest
      self.body.go_to(self.target)

    if self.state == 'idle':
      if self.body.amount < 0.5:
        self.state = 'flee'
        self.tempstate = 'idle'
      self.body.stop()

    if self.state == 'attack':
      if self.body.amount < 0.5:
        self.state = 'flee'
        self.tempstate = 'attack'
      if message == 'timer':
        try:  
          self.target = self.body.find_nearest('Mantis')
          self.body.follow(self.target)
        except ValueError:
          self.state = 'idle'
      elif message == 'collide' and details['what'] == 'Mantis' and self.selec_slug_attack == self.body:
        mantis = details['who']
        mantis.amount -= 0.05
      self.body.set_alarm(1)

    if self.state == 'build':
      if self.body.amount < 0.5:
        self.state = 'flee'
        self.tempstate = 'build'
      if message == 'timer': 
        self.target = self.body.find_nearest('Nest')
        self.body.go_to(self.target)
      elif message == 'collide' and details['what'] == 'Nest' and self.selec_slug_build == self.body:
        nest = details['who']
        nest.amount += 0.01
      self.body.set_alarm(1)

    if self.state == 'harvest':
      if self.body.amount < 0.5:
        self.state = 'flee'
        self.tempstate = 'harvest'
      if self.have_resource:
        if message == 'timer':
          self.target = self.body.find_nearest('Nest')
          self.body.go_to(self.target)
        elif message == 'collide' and details['what'] == 'Nest'and self.selec_slug_build == self.body:
          nest = details['who']
          #nest.amount += 0.01
          self.have_resource = False
      else:
        if message == 'timer':
          self.target = self.body.find_nearest('Resource')
          self.body.go_to(self.target)
        elif message == 'collide' and details['what'] == 'Resource' and self.selec_slug_resource == self.body:
          self.selec_slug_build = self.selec_slug_resource
          resources = details['who']
          resources.amount -= 0.25
          self.have_resource = True
      self.body.set_alarm(1)

    # TODO: IMPLEMENT THIS METHOD
    #  (Use helper methods and classes to keep your code organized where
    #  approprioate.)    

world_specification = {
  #'worldgen_seed': 13, # comment-out to randomize
  'nests': 2,
  'obstacles': 5,
  'resources': 5,
  'slugs': 5,
  'mantises': 10,
}

brain_classes = {
  'mantis': MantisBrain,
  'slug': SlugBrain,
}
