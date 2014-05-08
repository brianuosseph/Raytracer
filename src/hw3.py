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

def sphereRayIntersection(ray, sphere):
	# Quadratic formula to find distance: ad^2 + bd + c = 0
	a = dot(ray.direction, ray.direction)
	b = 2.*dot(ray.direction, sub(ray.origin, sphere.center))
	c = dot(sub(ray.origin, sphere.center), sub(ray.origin, sphere.center)) - (sphere.radius*sphere.radius)
	discriminant = (b*b) - (4.*a*c)
	if discriminant < 0.:		# No intersection
		return False
	# elif discriminant == 0.: # One intersection
	# 	d = (-1.*b - discrimRoot) / (2.*a)
	# 	point = add(ray.origin, mult(d, ray.direction))
	# 	return Intersection(point, d, self.surfaceNormal(point), self)
	else:
		discrimRoot = math.sqrt(discriminant)
		d0 = (-1.*b + discrimRoot) / (2.*a)
		d1 = (-1.*b - discrimRoot) / (2.*a)
		if d0 > d1:
			d0, d1 = d1, d0
		if d1 < 0.:
			return False
		else:
			return True

def planeRayIntersection(ray, plane):
	n = plane.normal
	if dot(ray.direction, n) == 0:
		return False
	else:
		dist = -1.*(dot(ray.direction, n) + plane.coefficients[3])/ dot(ray.direction, n)
		if dist > 0:
			return True
		return False

def getDistance(p1, p2):
	dx = p2[0]-p1[0]
	dy = p2[1]-p1[1]
	dz = p2[2]-p1[2]
	return math.sqrt( (dx*dx) + (dy*dy) + (dz*dz))

def getBulbLightDistance(intersect, light):
	l = light.position
	p = intersect.point
	dx = l[0]-p[0]
	dy = l[1]-p[1]
	dz = l[2]-p[2]
	return math.sqrt( (dx*dx) + (dy*dy) + (dz*dz))


class Ray:
	def __init__(self, origin, direction):
		self.origin = origin
		self.direction = direction
	def initializeFromVectors(self, eye, forward, s, right, t, up):
		self.origin = eye
		self.direciton = add(forward, add(mult(s, right), mult(t, up)))
	# def intializeFromImagePos(self, eye, forward, x, right, y, up):
	# 	s = (2.*x - WIDTH)/MAX
	# 	t = (HEIGHT - 2.*y)/MAX
	# 	self.origin = eye
	# 	self.direction = add(forward, add(mult(s, right), mult(t, up)))

class Intersection:
	def __init__(self, point, distance, normal, obj):
		self.point = point
		self.distance = distance
		self.normal = normal
		self.object = obj

class Object3D:
	def __init__(self, geometryName, p1, p2, p3, p4, p5, p6, p7):
		self.type = geometryName
		self.param1 = p1
		self.param2 = p2
		self.param3 = p3
		self.param4 = p4
		self.color = (p5,p6,p7)
class Sphere:
	def __init__(self, x, y, z, radius, r, g, b):
		self.type = "sphere"
		self.center = (x,y,z)
		self.radius = radius
		self.color = (r,g,b)
	def intializeFromObject3D(self, obj):
		self.center = (obj.param1,obj.param2,obj.param3)
		self.radius = obj.param4
		self.color = obj.color
	def rayIntersection(self, ray):
		# Quadratic formula to find distance: ad^2 + bd + c = 0
		a = dot(ray.direction, ray.direction)
		b = 2.*dot(ray.direction, sub(ray.origin, self.center))
		c = dot(sub(ray.origin, self.center), sub(ray.origin, self.center)) - (self.radius*self.radius)
		discriminant = (b*b) - (4.*a*c)
		if discriminant < 0.:		# No intersection
			return Intersection((0.,0.,0.), -1, (0.,0.,0.), self)
		# elif discriminant == 0.: # One intersection
		# 	d = (-1.*b - discrimRoot) / (2.*a)
		# 	point = add(ray.origin, mult(d, ray.direction))
		# 	return Intersection(point, d, self.surfaceNormal(point), self)
		else:
			discrimRoot = math.sqrt(discriminant)
			d0 = (-1.*b + discrimRoot) / (2.*a)
			d1 = (-1.*b - discrimRoot) / (2.*a)
			if d0 > d1:
				d0, d1 = d1, d0
			if d1 < 0.:
				return Intersection((0.,0.,0.), -1, (0.,0.,0.), self)
			else:
				if d0 < 0.:			# d1 is only positive solution
					point = add(ray.origin, mult(d1, ray.direction))
					return Intersection(point, d1, self.surfaceNormal(point), self)
				else:				# d0 is smallest positive soution
					point = add(ray.origin, mult(d0, ray.direction))
					return Intersection(point, d0, self.surfaceNormal(point), self)
	def surfaceNormal(self, point):
		return normalize(sub(point, self.center))
class Plane:
	def __init__(self, A, B, C, D, r, g, b):
		self.type = "plane"
		self.coefficients = (A,B,C,D)
		self.normal = normalize((A,B,C))
		self.color = (r,g,b)
	def initializeFromObject3D(self, obj):
		self.coefficients = (obj.param1, obj.param2, obj.param3, obj.param4)
		self.normal = normalize( (obj.param1, obj.param2, obj.param3) )
		self.color = obj.color
	def rayIntersection(self, ray):
		denominator = dot(ray.direction, self.normal)
		if denominator == 0.:		# Check if dividing by zero
			return Intersection((0.,0.,0.), -1, (0.,0.,0.), self)
		else:
			if self.coefficients[0] != 0.:
				arbitraryPoint = ((-1.*self.coefficients[3]/self.coefficients[0]), 0., 0.) # X-intercept
			elif self.coefficients[1] != 0.:
				arbitraryPoint = (0., (-1.*self.coefficients[3]/self.coefficients[1]), 0.) # Y-intercept
			elif self.coefficients[2] != 0.:
				arbitraryPoint = (0., 0., (-1.*self.coefficients[3]/self.coefficients[2])) # Z-intercept
			# Don't have a case for handling when A = B = C = 0
			d = dot(sub( arbitraryPoint, ray.origin), self.normal)/denominator
			if d > 0.:
				point = add(ray.origin, mult(d, ray.direction))
				return Intersection(point, d, self.normal, self)
			return Intersection((0.,0.,0.), -1, (0.,0.,0.), self)

		# n = self.normal
		# if dot(ray.direction, n) == 0:
		# 	return Intersection((0.,0.,0.), -1, (0.,0.,0.), self)
		# else:
		# 	d = -1.*(dot(ray.direction, n) + self.coefficients[3])/ dot(ray.direction, n)
		# 	if d > 0:
		# 		point = add(ray.origin, mult(d, ray.direction))
		# 		return Intersection(point, d, self.normal, self)
		# 	return Intersection((0.,0.,0.), -1, (0.,0.,0.), self)


class Light:
	def __init__(self, lightType, x, y, z, r, g, b):
		self.type = lightType
		self.x = x
		self.y = y
		self.z = z
		self.r = r
		self.g = g
		self.b = b
class Sunlight(Light):
	def __init__(self, x, y, z, r, g, b):
		self.type = "sun"
		self.direction = normalize((x,y,z))
		self.color = (r,g,b)
	def initalizeFromLight(self, light):
		self.type = light.type
		self.direction = normalize((light.x,light.y,light.z))
		self.color = (light.r,light.g,light.b)
	def illuminate(self, intersect, objects):
		shadowRay = Ray(intersect.point, normalize(l.direction))
		normalDotDirection = dot(intersect.normal, shadowRay.direction)
		if normalDotDirection < 0.:
			return (-1,-1,-1)

		if len(objects) < 2:
			return mult( normalDotDirection, multColor(intersect.object.color, l.color) )
		else:
			otherObjects = list(objects)
			otherObjects.remove(intersect.object)
			for o in otherObjects:	
			# Works, but will test with code below for more detailed observation of data
				if o.rayIntersection(shadowRay).distance < 0.:
					return (-1,-1,-1)
				else:
					return mult( normalDotDirection, multColor(intersect.object.color, l.color) )


				# # Shadows are not exactly correct --> Some intersection algorithm is wrong
				# if o.type.__eq__("sphere"):
				# 	# Part of lack of shadows bug for dodeca is here
				# 	if sphereRayIntersection(shadowRay, o):
				# 		print "Help I'm in a shadow!"
				# 		return (-1,-1,-1)
				# 	else:
				# 		return mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, self.color) )
				# elif o.type.__eq__("plane"):
				# 	if planeRayIntersection(shadowRay, o):
				# 		print "Help I'm in a shadow!!"
				# 		return (-1,-1,-1)
				# 	else:
				# 		return mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, self.color) )
class Bulblight(Light):
	def __init__(self, x, y, z, r, g, b):
		self.type = "bulb"
		self.position = (x,y,z)
		self.color = (r,g,b)
	def initializeFromLight(self, light):
		self.type = light.type
		self.posiiton = (light.x,light.y,light.z)
		self.color = (light.r,light.g,light.b)
	def illuminate(self, intersect, objects):
		shadowRay = Ray(intersect.point , normalize(sub(self.position, intersect.point)))
		lightDistance = getBulbLightDistance(intersect, self)

		# Not sure if clamping this did anything...
		normalDotDirection = dot(intersect.normal, shadowRay.direction)
		if normalDotDirection < 0.:
			return (-1,-1,-1)

		if len(objects) < 2:
			return mult( normalDotDirection, multColor(intersect.object.color, self.color) )
		elif normalDotDirection <= 0.:
			return (-1,-1,-1)
		else:
			otherObjects = list(objects)
			otherObjects.remove(intersect.object)
			for o in otherObjects:
			# Works, but will test with code below for more detailed observation of data
				shadowIntersect = o.rayIntersection(shadowRay)
				if lightDistance > shadowIntersect.distance > 0:	# This makes it equivalent with code below
					return (-1,-1,-1)
				else:
					return mult( normalDotDirection, multColor(intersect.object.color, self.color) )


				# # Lack of shadows bug for strange is here
				# if o.type.__eq__("sphere"):
				# 	if sphereRayIntersection(shadowRay, o):		
				# 		shadowIntersect = o.rayIntersection(shadowRay)	
				# 		if lightDistance > shadowIntersect.distance > 0:
				# 			return (-1,-1,-1)
				# 		else:
				# 			return mult( normalDotDirection, multColor(intersect.object.color, self.color) )	
				# 	else:
				# 		return mult( normalDotDirection, multColor(intersect.object.color, self.color) )
				# elif o.type.__eq__("plane"):
				# 	if planeRayIntersection(shadowRay, o):
				# 		shadowIntersect = o.rayIntersection(shadowRay)	
				# 		if lightDistance > shadowIntersect.distance > 0:
				# 			return (-1,-1,-1)		
				# 		else:
				# 			return mult( normalDotDirection, multColor(intersect.object.color, self.color) )	
				# 	else:
				# 		return mult( normalDotDirection, multColor(intersect.object.color, self.color) )
						
						 


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

				# Projection Specification
				elif args[0].__eq__("eye"):
					eye = (float(args[1]), float(args[2]), float(args[3]))
				elif args[0].__eq__("forward"):
					forward = (float(args[1]), float(args[2]), float(args[3]))
					right = normalize(cross(forward, up))
					up = normalize(cross(right, forward))
				elif args[0].__eq__("up"):
					t = (float(args[1]), float(args[2]), float(args[3]))
					right = normalize(cross(forward, t))
					up = normalize(cross(right, forward))

				# Light Specification				
				elif args[0].__eq__("sun"):
					x = float(args[1])
					y = float(args[2])
					z = float(args[3])
					r = float(args[4])
					g = float(args[5])
					b = float(args[6])
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
					sphere = Sphere(x,y,z,radius,r,g,b)
					objects.append(sphere)
				elif args[0].__eq__("plane"):
					A = float(args[1])
					B = float(args[2])
					C = float(args[3])
					D = float(args[4])
					r = float(args[5])
					g = float(args[6])
					b = float(args[7])
					plane = Plane(A,B,C,D,r,g,b)
					objects.append(plane)
				else:
					pass
		color = (0,0,0)
		MAX = WIDTH
		if (WIDTH < HEIGHT):
			MAX = HEIGHT
		for x in range(WIDTH):
			for y in range(HEIGHT):
				# (s,t) is postion in scene, (x,y) is pixel on image
				s = (2.*x - WIDTH)/MAX
				t = (HEIGHT - 2.*y)/MAX
				direction = add(forward, add(mult(s, right), mult(t, up)))
				ray = Ray(eye, direction)
				intersect = Intersection((0.,0.,0.), -1., (0.,0.,0.), None)
				for o in objects:
					currentIntersection = o.rayIntersection(ray)
					if currentIntersection.distance > 0. and intersect.distance < 0.:
						intersect = currentIntersection
					elif intersect.distance > currentIntersection.distance > 0.:
						intersect = currentIntersection
					else:
						pass
				if intersect.object == None or intersect.distance < 0.:
					pass # Apparently ambient light would go here?
				else:
					# Make object two-side by inverting normal prior to lighting
					if dot(intersect.normal, sub(eye, intersect.point)) < 0.:
						intersect.normal = mult(-1., intersect.normal)
					test = True
					inShadow = False
					surfaceColor = (0,0,0)
					for l in lights:
						# Still getting clip shadow on bulb and neglight, missing shadows on strange and dodeca, and coloring is off on sunbulb
						color = l.illuminate(intersect, objects)
						if color == (-1,-1,-1) or color == None:		# Not sure why I get a None return on neglight.txt
							continue
						else: 
							surfaceColor = add(surfaceColor, color)
							#print (x,y), color, surfaceColor
					finalColor = (int(surfaceColor[0]*255.), int(surfaceColor[1]*255.), int(surfaceColor[2]*255.) )
					#print (x,y), "\t\tSurface color: "+str(surfaceColor)+"\t\tDrawn color: "+str(finalColor)
					image.putpixel((x,y), finalColor)

					# 	# Provides shadows for dodeca & strange
					# 	if l.type.__eq__("sun"):		# Shadows not correct
					# 		shadowRay = Ray(intersect.point, normalize(l.direction))
					# 		if len(objects) < 2:
					# 			accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 			surfaceColor = add(surfaceColor, accumulate)
					# 		elif dot(intersect.normal, l.direction) < 0:
					# 			pass
					# 		else:
					# 			otherObjects = list(objects)
					# 			otherObjects.remove(intersect.object)
					# 			for o in otherObjects:
					# 				# # Should work, but plane shadows are missing
					# 				# if o.rayIntersection(shadowRay) < 0:
					# 				# 	accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 				# 	surfaceColor = add(surfaceColor, accumulate)
					# 				# else:
					# 				# 	inShadow == True
									
					# 				# Works, but shadows are not exactly correct --> Some intersection algorithm is wrong
					# 				if o.type.__eq__("sphere"):
					# 					# Dodeca bug
					# 					if sphereRayIntersection(shadowRay, o):
					# 						inShadow = True
					# 					else:
					# 						accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 						surfaceColor = add(surfaceColor, accumulate)
					# 				elif o.type.__eq__("plane"):
					# 					if planeRayIntersection(shadowRay, o):
					# 						inShadow = True
					# 					else:
					# 						accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 						surfaceColor = add(surfaceColor, accumulate)
					# 				else:
					# 					accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 					surfaceColor = add(surfaceColor, accumulate)
					# 	if l.type.__eq__("bulb"):
					# 		shadowRay = Ray(intersect.point , normalize(sub(l.position, intersect.point)))
					# 		lightDistance = getBulbLightDistance(intersect, l)
					# 		if len(objects) < 2:
					# 			accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 			surfaceColor = add(surfaceColor, accumulate)
					# 		elif dot(intersect.normal, shadowRay.direction) <= 0.:
					# 			pass
					# 		else:
					# 			otherObjects = list(objects)
					# 			otherObjects.remove(intersect.object)
					# 			for o in otherObjects:
					# 				# # Should work, but plane shadows are missing
					# 				# shadowIntersect = o.rayIntersection(shadowRay)
					# 				# if shadowIntersect < 0: #if shadowIntersect.distance < 0:	# This makes it equivalent with code below
					# 				# 	accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 				# 	surfaceColor = add(surfaceColor, accumulate)
					# 				# else:
					# 				# 	#print (x,y), "in Shadow"
					# 				# 	inShadow == True

					# 				# Works, but shadows overlapping on sphere
					# 				if o.type.__eq__("sphere"):
					# 					if sphereRayIntersection(shadowRay, o):	
					# 						# Strange bug here	
					# 						distanceFromIntersect = getDistance(intersect.point, o.rayIntersection(shadowRay).point)	
					# 						#print lightDistance, distanceFromIntersect				# Need distance check to properly place shadows
					# 						if lightDistance > distanceFromIntersect > 0.:
					# 							inShadow = True		# Need to ignore light source, not just color black
					# 					else:
					# 						accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 						surfaceColor = add(surfaceColor, accumulate)
					# 				elif o.type.__eq__("plane"):
					# 					if planeRayIntersection(shadowRay, o): 	# Need distance check to properly place shadows
					# 						distanceFromIntersect = getDistance(intersect.point, o.rayIntersection(shadowRay).point)	
					# 						#print lightDistance, distanceFromIntersect				# Need distance check to properly place shadows
					# 						if lightDistance > distanceFromIntersect > 0.:
					# 							inShadow = True # Need to ignore light source, not just color black
					# 					else:
					# 						accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 						surfaceColor = add(surfaceColor, accumulate)
					# 				# else:
					# 				# 	accumulate = mult( dot(intersect.normal, shadowRay.direction), multColor(intersect.object.color, l.color) )
					# 				# 	surfaceColor = add(surfaceColor, accumulate)
					# 	if inShadow:
					# 		continue
					# if not inShadow:
					# 	finalColor = (int(surfaceColor[0]*255.), int(surfaceColor[1]*255.), int(surfaceColor[2]*255.) )
					# 	image.putpixel((x,y), finalColor)
					# 	if test:
					# 		print (x,y), "\t\tSurface color: "+str(surfaceColor)+"\t\tDrawn color: "+str(finalColor)
					# else:
					# 	image.putpixel((x,y), (0,0,0))
					# 	if test:
					# 		print (x,y), "\t\tDrawn color: "+str((0,0,0))

					

		image.save(OUTPUT_FILE)