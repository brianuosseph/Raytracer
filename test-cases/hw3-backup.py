__author__ = 'brianuosseph'
import sys
import math
from PIL import Image

global TEXTFILE
global WIDTH
global HEIGHT
global OUTPUT_FILE
global image
global objects
global lights
global eye
global forward
global right
global up
#global collision_distance

def add(v1, v2):
	return [x+y for x,y in zip(v1,v2)]

def addConst(v1, c):
	return [x+c for x in v1]

def sub(v1, v2):
	return [x-y for x,y in zip(v1, v2)]

def mult(c, v1):
	return [c*v for v in v1]

def multColor(c1, c2):
	return [x*y for x,y in zip(c1,c2)]

def dot(v1, v2):
	return sum([x*y for x,y in zip(v1, v2)])

def cross(v1, v2):
	return [v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v2[0]-v1[0]*v2[2], v1[0]*v2[1]-v1[1]*v2[0]]

def normalize(v):
	return [x/math.sqrt(dot(v,v)) for x in v]

def trace_sphere(r, s, tmin, color):
    sr = sub(s[0], r[0])
    dsr = dot(sr, r[1])
    d = dsr*dsr - dot(sr,sr) + s[1]
    if d < 0: return
    d = math.sqrt(d)

    t1 = dsr + d
    if t1 < 0: return

    t2 = dsr - d
    if t2 > tmin[0]: return

    if t2 < 0:
        tmin[0] = t1
    else:
        tmin[0] = t2
    color[:] = [s[2]]

def trace_ray(ray, spheres):
    color = [(0, 0, 0)]
    tmin = [100000]
    for s in spheres:
        trace_sphere(ray, s, tmin, color)
    return color[0]

def sphereRayIntersection(ray, sphere):
	radius = sphere.param4
	d = sub(ray[1], ray[0])
	f = sub(ray[0], (sphere.param1, sphere.param2, sphere.param3))

	a = dot(d,d)
	b = 2.*dot(f,d)
	c = dot(f,f) - (radius*radius)
	discriminant = b*b - 4*a*c
	if discriminant < 0.:
		return False
	else:
		distSqrt = math.sqrt(discriminant)
		q = 0.
		if b < 0.:
			q = (-b - distSqrt)/(2.0*a)
		else:
			q = (-b + distSqrt)/(2.0*a)
		t0 = q/a
		t1 = c/q

		if t0 > t1:
			t0, t1 = t1, t0
		if t1 < 0.:
			return False
		else:
			if t0 < 0.:
				# t1 is interect
				return True
			else:
				# t0 is intersect
				return True

def planeRayIntersection(ray, plane):
	n = normalize((plane.param1, plane.param2, plane.param3))
	if dot(ray[1], n) == 0:
		return False
	else:
		dist = -1.*(dot(ray[0], n) + plane.param4)/ dot(ray[1], n)
		if dist > 0:
			return True
		return False

def trace(ray, objects):
	for o in objects:
		if o.type.__eq__("sphere"):
			if sphereRayIntersection(ray, o):
				return (0,0,0)
	return color

class Object3D:
	def __init__(self, geometryName, p1, p2, p3, p4, p5, p6, p7):
		self.type = geometryName
		self.param1 = p1
		self.param2 = p2
		self.param3 = p3
		self.param4 = p4
		self.param5 = p5
		self.param6 = p6
		self.param7 = p7

class Light:
	def __init__(self, lightType, x, y, z, r, g, b):
		self.type = lightType
		self.x = x
		self.y = y
		self.z = z
		self.r = r
		self.g = g
		self.b = b
		# if lightType.__eq__("sun"):
		# 	self.direction = normalize((x,y,z))
		# 	self.color = (r,g,b)
		# if: lightType.__eq__("bulb"):

class Sunlight(Light):
	def __init__(self, x, y, z, r, g, b):
		self.type = "sun"
		self.direction = normalize((x,y,z))
		self.color = (r,g,b)

class Bulblight(Light):
	def __init__(self, x, y, z, r, g, b):
		self.type = "bulb"
		self.position = (x,y,z)
		self.color = (r,g,b)

if (sys.argv.__len__() < 2):
	print "Kinda need a textfile argument to write anything..."
else:
	TEXTFILE = sys.argv[1]
	if (TEXTFILE.isspace() or not TEXTFILE):
		print "How about you give me a textfile to read!"
	else:
		with open(TEXTFILE, 'r') as input:
			for line in input:
				args = line.split();
				if not args:
					pass
				elif args[0].__eq__("png"):
					WIDTH = int(args[1])
					HEIGHT = int(args[2])
					OUTPUT_FILE = args[3]
					image = Image.new("RGBA", (WIDTH, HEIGHT))

					objects = []
					lights = []
					eye = (0.,0.,0.)
					forward = (0.,0.,-1.)
					right = (1.,0.,0.)		# Normalized
					up = (0.,1.,0.)			# Normalized
					collision_distance = 10000.

				# Projection Specification
				elif args[0].__eq__("eye"):
					#print "Before: "+str(eye)
					eye = (float(args[1]), float(args[2]), float(args[3]))
					#print "After: "+str(eye)
				elif args[0].__eq__("forward"):
					forward = (float(args[1]), float(args[2]), float(args[3]))
					right = normalize(cross(forward, up))
					up = normalize(cross(right, forward))
					# Recalc and normalize right and up
				elif args[0].__eq__("up"):
					t = (float(args[1]), float(args[2]), float(args[3]))
					right = normalize(cross(forward, t))
					up = normalize(cross(right, forward))
					# Recalc and normalize right and up

				# Light Specification				
				elif args[0].__eq__("sun"):
					x = float(args[1])
					y = float(args[2])
					z = float(args[3])
					r = float(args[4])
					g = float(args[5])
					b = float(args[6])

					# direction = normalize((x,y,z))
					sun = Sunlight(x,y,z,r,g,b)
					lights.append(sun)

				elif args[0].__eq__("bulb"):
					x = float(args[1])
					y = float(args[2])
					z = float(args[3])
					r = float(args[4])
					g = float(args[5])
					b = float(args[6])

					bulb = Bulblight(x,y,z,r,g,b)
					lights.append(bulb)

				# Object Specification
				elif args[0].__eq__("sphere"):
					x = float(args[1])
					y = float(args[2])
					z = float(args[3])
					radius = float(args[4])
					r = float(args[5])
					g = float(args[6])
					b = float(args[7])

					sphere = Object3D("sphere",x,y,z,radius,r,g,b)
					objects.append(sphere)

				elif args[0].__eq__("plane"):
					A = float(args[1])
					B = float(args[2])
					C = float(args[3])
					D = float(args[4])
					r = float(args[5])
					g = float(args[6])
					b = float(args[7])

					plane = Object3D("plane",A,B,C,D,r,g,b)
					objects.append(plane)

					# Ax + By + Cz + D = 0
					# Normal of plane = normalized(A,B,C)
				else:
					pass

		# Begin drawing after end of input (here)
		color = (0,0,0)
		intersectNormal = (0.,0.,0.)
		MAX = WIDTH
		if (WIDTH < HEIGHT):
			max = HEIGHT
		#print objects
		for x in range(WIDTH):
			for y in range(HEIGHT):
				# (s,t) is postion in scene, (x,y) is pixel on image
				s = (2.*x - WIDTH)/MAX
				t = (HEIGHT - 2.*y)/MAX

				direction = add(forward, add(mult(s, right), mult(t, up)))
				ray = (eye, direction)
				#print ray
				collision_distance = 10000.
				hitObject = None
				collisionPoint = (0., 0., 0.)
				objColor = (0,0,0)
				finalColor = (0,0,0)
				for o in objects:
					if o.type.__eq__("sphere"):
						radius = o.param4
						center = (o.param1, o.param2, o.param3)
						d = sub(ray[1], ray[0])
						f = sub(ray[0], (o.param1, o.param2, o.param3))

						a = dot(d,d)
						b = 2.*dot(f,d)
						c = dot(f,f) - (radius*radius)
						discriminant = b*b - 4*a*c
						if discriminant < 0.:
							pass
						else:
							distSqrt = math.sqrt(discriminant)
							q = 0.
							if b < 0.:
								q = (-b - distSqrt)/(2.0*a)
							else:
								q = (-b + distSqrt)/(2.0*a)
							t0 = q/a
							t1 = c/q

							if t0 > t1:
								t0, t1 = t1, t0
							if t1 < 0.:
								pass
							else:
								if t0 < 0.:
									# t1 is interect
									if t1 < collision_distance:
										collision_distance = t1
										hitObject = o
										objColor = (int(o.param5), int(o.param6), int(o.param7))
										collisionPoint = add(eye, mult(collision_distance, direction))
										intersectNormal = normalize(sub(collisionPoint, center))
										#image.putpixel((x,y), objColor)
								else:
									# t0 is intersect
									if t0 < collision_distance:
										collision_distance = t0
										hitObject = o
										objColor = (int(o.param5), int(o.param6), int(o.param7))
										collisionPoint = add(eye, mult(collision_distance, direction))
										intersectNormal = normalize(sub(collisionPoint, center))									
										#image.putpixel((x,y), objColor)
					elif o.type.__eq__("plane"):
						n = normalize((o.param1, o.param2, o.param3))
						if dot(ray[1], n) == 0:
							pass
						else:
							dist = -1.*(dot(ray[0], n) + o.param4)/ dot(ray[1], n)
							if dist > 0 and dist < collision_distance:
								collision_distance = dist
								hitObject = o
								objColor = (int(o.param5), int(o.param6), int(o.param7))
								intersectNormal = n
								#image.putpixel((x,y), objColor)
					else:
						pass
				if hitObject:
					test = False
					inShadow = False
					for l in lights:
						if l.type.__eq__("sun"):
							shadowRay = (collisionPoint, l.direction)
							otherObjects = objects[:]
							otherObjects.remove(hitObject)
							for o in otherObjects:
									if o.type.__eq__("sphere"):
										if sphereRayIntersection(shadowRay, o):
											# In hw3sun.txt, self-shadowing on surface of sphere
											inShadow = True
										else:
											accumulate = mult(dot(intersectNormal, shadowRay[1]), multColor(objColor, l.color) )
											finalColor = add(finalColor, accumulate)
											#print str(l.color)+"\t\t"+str(objColor)+"\t\t"+str(finalColor)
									elif o.type.__eq__("plane"):
										if planeRayIntersection(shadowRay, o):
											inShadow = True
										else:
											accumulate = mult(dot(intersectNormal, shadowRay[1]), multColor(objColor, l.color) )
											finalColor = add(finalColor, accumulate)
									else:
										pass
						if l.type.__eq__("bulb"):
							shadowRay = (collisionPoint, sub(l.position, collisionPoint))
							otherObjects = objects[:]
							otherObjects.remove(hitObject)
							for o in otherObjects:
								if o.type.__eq__("sphere"):
									if sphereRayIntersection(shadowRay, o):
										inShadow = True
									else:
										accumulate = mult(dot(intersectNormal, shadowRay[1]), multColor(objColor, l.color) )
										finalColor = add(finalColor, accumulate)
								elif o.type.__eq__("plane"):
									if planeRayIntersection(shadowRay, o):
										inShadow = True
									else:
										accumulate = mult(dot(intersectNormal, shadowRay[1]), multColor(objColor, l.color) )
										finalColor = add(finalColor, accumulate)
								else:
									pass
					if not inShadow:
						RGBColor = (int(finalColor[0]*255), int(finalColor[1]*255), int(finalColor[2]*255) )
						#print finalColor[2]
						if test:
							print (x,y)
						image.putpixel((x,y), RGBColor)
					else:
						if test:
							print (x,y)
						image.putpixel((x,y), (0,0,0))


		# Vector Operations Debug
		# print add((1,1,1), (2,2,2))
		# print sub((2,2,2), (1,1,1))
		# print mult(4, (1,1,1))
		# print dot((1,1,1), (1,1,1)) # = 3
		# print normalize((1,1,1))			# = (.577, .577, .577)

				#image.putpixel((x,y), color)
		image.save(OUTPUT_FILE)