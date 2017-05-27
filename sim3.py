import random
import codecs
import math

POWER = 1.0/150.0
CRASH = .3 #stdev of random factor in crash function
LAPS = 85
QUALIFYING = False

class Car:
	def __init__(self, turning, topspeed, braking, acceleration, pitting, tires, tiretype, time, bestlap, pits, team):
		self.t = turning
		self.s = topspeed
		self.b = braking
		self.a = acceleration
		self.p = pitting
		self.tires = tires
		self.tiretype = tiretype
		self.time = time
		self.bestlap = bestlap
		self.pits = pits
		self.team = team

class Driver:
	def __init__(self, corners, overtaking, defending, tirewear, technical, adaptability, starting, number, name):
		self.c = corners
		self.o = overtaking
		self.d = defending
		self.t = tirewear
		self.technical = technical
		self.a = adaptability
		self.startpos = starting
		self.num = number
		self.name = name

class Track:
	def __init__(self, corners, technical, straights, weather, length):
		self.c = corners
		self.technical = technical
		self.s = straights
		self.w = weather
		self.l = length
		
def run_lap(track, qualifying, car, driver, car_ahead_time, driver_ahead_def, car_behind_time, lap, rainstat_flag, was_raining, was_wet):
	base = track.l
	power1 = POWER
	power2 = POWER
	power3 = POWER
	power4 = POWER
	power5 = POWER
	power6 = POWER
	power7 = POWER
	power8 = POWER
	power9 = POWER
	power10 = POWER
	if car.t > track.c:
		power1 = POWER*1/car.t**(1.0/3.0)
	if driver.c > track.c:
		power2 = POWER*1/driver.c**(1.0/3.0)
	if car.s > track.s:
		power3 = POWER*1/car.s**(1.0/3.0)
	if car.b > track.c:
		power4 = POWER*1/car.b**(1.0/3.0)
	if car.b > track.technical:
		power5 = POWER*1/car.b**(1.0/3.0)
	if driver.t > track.c:
		power6 = POWER*1/driver.t**(1.0/3.0)
	if driver.t > track.technical:
		power7 = POWER*1/driver.t**(1.0/3.0)
	if car.a > track.c:
		power8 = POWER*1/car.a**(1.0/3.0)
	if car.a > track.technical:
		power9 = POWER*1/car.a**(1.0/3.0)
	if driver.technical > track.technical:
		power10 = POWER*1/driver.technical**(1.0/3.0)
	cornering = (1/(car.t/track.c)**power1 + 1/(driver.c/track.c)**power2)/2
	topspeed = 1/(car.s/track.s)**power3
	braking = (1/(car.b/track.c)**power4 + 1/(car.b/track.technical)**power5)/2
	acceleration = (1/(car.a/track.c)**power8 + 1/(car.a/track.technical)**power9)/2
	brkacc = (1/(driver.t/track.c)**power6 + 1/(driver.t/track.technical)**power7)/2
	technical = 1/(driver.technical/track.technical)**power10
	wear = 1/(car.tires/80)**(POWER*2)
	
	#determine if it's raining for status updates
	if rainstat_flag == True and intensity[int(math.floor(car.time/60))] > 0 and was_raining == False:
		print "it has begun to rain"
		crashes.append((driver.name,4,lap,False))
		was_raining = True
		was_wet = True
	if rainstat_flag == True and intensity[int(math.floor(car.time/60))] == 0 and was_raining == True:
		print "the rain has ended"
		crashes.append((driver.name,5,lap,False))
		was_raining = False
	if rainstat_flag == True and wetness[int(math.floor(car.time/60))] == 0 and was_wet == True:
		print "track is dry"
		crashes.append((driver.name,6,lap,False))
		was_wet = False
	
	#weather effects
	current_wetness = wetness[int(math.floor(car.time/60))]
	if car.tiretype == "DRY":
		weather = (95/90-1)*track.l*current_wetness*2*math.exp(-driver.a/10) #base 5 s per 90 s lap * wetness parameter * adaptability
	else: #on wets
		weather = ((95/90-1)*track.l*(1-current_wetness)*2+2)*math.exp(-driver.a/10)

	#tirewear
	tirewear = track.l/40 * (1/track.c**POWER + 1/track.technical**POWER)/2 * 1/(driver.t)**POWER * 1/(car.tires/100)**.5 #base * track length * track wear * driver skill * how worn tires are already
	if car.tiretype == "WET":
		tirewear *= ((1-current_wetness)*2+1)*math.exp(-driver.a/10) #if the track is dry rip your tires, it's fine if this is < 1 though cause wet tires stronk
	car.tires -= tirewear
	
	#overtaking
	overtaking = 1
	overtaking_flag = False
	pit = False
	pit_time = 0
	if qualifying == False:
		if car.time - car_ahead_time < 1:
			'''if driver.o >= driver_ahead_def:
				overtaking = 1/(driver.o/driver_ahead_def)**POWER * 1.01
			else:
				overtaking = 1/(driver.o/driver_ahead_def/2)**POWER * 1.01'''
			overtaking = 1/(driver.o/driver_ahead_def)**POWER * 1.01 #delete this line ONLY if you add the commented part back in
			overtaking_flag = True
			
		if car_behind_time - car.time < 1:
			overtaking = 1.01
			overtaking_flag = True
		
		#pitting
		#if you pit you automatically replace your tires
		if car.tires < 40 and random.random() < .5:
			pit = True
		elif car.tires < 30 and random.random() < .75:
			pit = True
		elif car.tires < 20 and random.random() < .9:
			pit = True
		elif car.tires < 10:
			pit = True
		#set appropriate tire type when track conditions change
		if current_wetness <= .5 and car.tiretype == "WET":
			car.tiretype = "DRY"
			pit = True
		elif current_wetness >= .5 and car.tiretype == "DRY":
			car.tiretype = "WET"
			pit = True
		if pit == True:
			pit_time = 12 + 5 * 1/(car.p/5)**(POWER*20) + random.random()-.5
			pit_time += current_wetness #a little slower if it's wet
			car.tires = 100
			car.pits += 1
		else:
			pit_time = 0
	
	#crashing
	#high tire wear, poor skill, weather, and overtaking play into whether or not you will crash each lap
	#three types of crashes: small mistake/disruption, off the course (requires pit), race-ruining (driver dnfs)
	crash = 1 + 1/car.tires*10 + (track.c/car.t + track.c/driver.c + track.technical/driver.technical)/30 + random.gauss(0, CRASH)
	out = False	
	crash_prob = .1 * 130.0/track.l * 1/(car.tires) + (track.c/car.t + track.c/driver.c + track.technical/driver.technical)/3000 * (1+current_wetness*math.exp(-driver.a/10))
	if overtaking_flag == True:
		crash_prob += random.random()*.01
	if random.random() < crash_prob:
		type = random.random() * 10
		if type < 8:
			print 'crash (small)'
			crashes.append((driver.name,1,lap,overtaking_flag))
			crash_time = random.gauss(1.5 * (1+current_wetness),.5 * (1+current_wetness))
		elif type < 9:
			print 'crash (pits)'
			crashes.append((driver.name,2,lap,overtaking_flag))
			crash_time = 12 + 5 * 1/(car.p/5)**(POWER*20) * (crash) + random.random()-.5 #pitting plus severity of crash for repairs
			crash_time += current_wetness #a little slower if it's wet
			car.tires = 100
			car.pits += 1
			pit = True
		else:
			print 'crash (out)'
			crashes.append((driver.name,3,lap,overtaking_flag))
			crash_time = 0
			out = True
	else:
		crash_time = 0
	
	laptime = base * cornering * topspeed * braking * acceleration * brkacc * technical * wear * overtaking + weather + pit_time + crash_time + random.random()-.5
	car.time += laptime
	return laptime, pit, car.tiretype, out, was_raining, was_wet
		
cars = []
drivers = []

retcars = []
retdrivers = []
crashes = []
		
track1 = Track(10.0, 10.0, 10.0, 0, 30.0)
kaeshar_gp = Track(5.0, 4.0, 7.0, 6, 100.10)
aeridani_gp = Track(3.0, 8.0, 2.0, 8, 89.84)
ethanthova_gp = Track(3.0, 2.0, 6.0, 2, 55.40)
tjedigar_gp = Track(3.0, 6.0, 1.0, 3, 104.22)
aiyota_gp = Track(2.0, 9.0, 10.0, 6, 84.03)
czalliso_gp = Track(5.0, 10.0, 5.0, 3, 117.53)
blaland_gp = Track(10.0, 9.0, 7.0, 4, 100.22)
sagua_gp = Track(10.0, 5.0, 1.0, 5, 88.78)
aahrus_gp = Track(8.0, 6.0, 5.0, 6, 131.70)
auspikitan_gp = Track(2.0, 7.0, 3.0, 5, 106.16)
darvincia_gp = Track(5.0, 2.0, 5.0, 4, 103.36)
wyverncliff_gp = Track(5.0, 1.0, 2.0, 5, 90.00)
solea_gp = Track(7.0, 8.0, 9.0, 7, 122.68)
barsein_gp = Track(5.0, 7.0, 1.0, 1, 106.24)
dotruga_gp = Track(4.0, 6.0, 5.0, 4, 121.51)
bielosia_gp = Track(8.0, 1.0, 7.0, 4, 86.55)
bongatar_gp = Track(5.0, 5.0, 4.0, 4, 77.20)
space_gp = Track(1.0, 1.0, 10.0, 0, 73.63)
#               TURN SPD  BRAK ACC  PIT
cars.append(Car(6.0, 9.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Solea Racing")) #27
cars.append(Car(6.0, 9.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Solea Racing"))
cars.append(Car(6.0, 9.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Solea Racing"))
cars.append(Car(6.0, 7.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Dotruga Formula Racing")) #26
cars.append(Car(6.0, 7.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Dotruga Formula Racing"))
cars.append(Car(6.0, 7.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Dotruga Formula Racing"))
cars.append(Car(6.0, 7.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Cows Go Moo Racing")) #23
cars.append(Car(6.0, 7.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Cows Go Moo Racing"))
cars.append(Car(6.0, 7.0, 6.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Cows Go Moo Racing"))
cars.append(Car(6.0, 8.0, 6.0, 6.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "BONGATAR")) #
cars.append(Car(6.0, 8.0, 6.0, 6.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "BONGATAR"))
cars.append(Car(6.0, 8.0, 6.0, 6.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "BONGATAR"))
cars.append(Car(5.0, 10.0, 3.0, 9.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team V.V. Imperial")) #25
cars.append(Car(5.0, 10.0, 3.0, 9.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team V.V. Imperial"))
cars.append(Car(5.0, 10.0, 3.0, 9.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team V.V. Imperial"))
cars.append(Car(8.0, 7.0, 7.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Diigikwk Racers")) #26
cars.append(Car(8.0, 7.0, 7.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Diigikwk Racers"))
cars.append(Car(8.0, 7.0, 7.0, 7.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Diigikwk Racers"))
cars.append(Car(5.0, 5.0, 3.0, 4.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Vincent")) #16
cars.append(Car(5.0, 5.0, 3.0, 4.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Vincent"))
cars.append(Car(5.0, 5.0, 3.0, 4.0, 1.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Vincent"))
cars.append(Car(5.0, 7.0, 3.0, 4.0, 2.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Blaland Racing"))
cars.append(Car(5.0, 7.0, 3.0, 4.0, 2.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Blaland Racing"))
cars.append(Car(5.0, 7.0, 3.0, 4.0, 2.0, 100.0, "DRY", 0.0, 999.0, 0, "Team Blaland Racing"))
#					  CRN  OVTK DEF  FINE TECH ADPT
drivers.append(Driver(6.0, 6.0, 2.0, 4.0, 5.0, 3.0, 17, 47, u"ketila léqa pavúteka")) #17
drivers.append(Driver(5.0, 3.0, 4.0, 3.0, 2.0, 2.0, 10, 19, u"khélok atep zailunaɰ")) #17
drivers.append(Driver(3.0, 2.0, 3.0, 5.0, 2.0, 1.0, 5, 31, u"xap'ít celentir šaŋév")) #17
drivers.append(Driver(5.0, 5.0, 4.0, 6.0, 7.0, 4.0, 1, 29, "Sago Aludetsei")) #18
drivers.append(Driver(4.0, 2.0, 3.0, 2.0, 4.0, 1.0, 23, 11, "Tuto Keget")) #14
drivers.append(Driver(4.0, 2.0, 4.0, 3.0, 2.0, 1.0, 20, 98, "Gorga Motxev")) #15
drivers.append(Driver(4.0, 3.0, 3.0, 3.0, 3.0, 1.0, 9, 41, "Olga Candy")) #15
drivers.append(Driver(4.0, 3.0, 3.0, 3.0, 2.0, 1.0, 13, 69, "Marisa Sanchez")) #15
drivers.append(Driver(9.0, 6.0, 3.0, 5.0, 4.0, 1.0, 4, 42, "Frank Oosterhout")) #21
drivers.append(Driver(7.0, 7.0, 5.0, 6.0, 7.0, 5.0, 11, 30, "Josh Wise")) #23
drivers.append(Driver(3.0, 3.0, 4.0, 1.0, 5.0, 1.0, 19, " 2", "Body Hide")) #14
drivers.append(Driver(1.0, 2.0, 1.0, 5.0, 5.0, 1.0, 16, " 3", "Bob")) #14
drivers.append(Driver(7.0, 8.0, 3.0, 5.0, 4.0, 4.0, 2, 80, u"Ifloenne é Aya")) #19
drivers.append(Driver(4.0, 3.0, 2.0, 4.0, 3.0, 1.0, 15, 81, u"Lyǽs Kæræsekæræn")) #16
drivers.append(Driver(3.0, 3.0, 3.0, 3.0, 3.0, 1.0, 12, " 1", "Robbie Rotten")) #8
drivers.append(Driver(3.0, 5.0, 4.0, 3.0, 4.0, 2.0, 6, 74, u"Bařàsiz Konoca")) #18
drivers.append(Driver(5.0, 5.0, 3.0, 3.0, 3.0, 2.0, 14, 94, u"At'ipi Nesbeksë")) #18
drivers.append(Driver(2.0, 1.0, 3.0, 4.0, 6.0, 2.0, 7, 53, u"Ešuro Tàcràɰë")) #15
drivers.append(Driver(5.0, 5.0, 5.0, 5.0, 2.0, 2.0, 18, 20, "Mac")) #17
drivers.append(Driver(6.0, 6.0, 5.0, 3.0, 2.0, 2.0, 22, 21, "Orson")) #16
drivers.append(Driver(5.0, 5.0, 5.0, 5.0, 2.0, 2.0, 21, 22, "Philipe")) #15
drivers.append(Driver(8.0, 5.0, 2.0, 5.0, 7.0, 3.0, 3, " 4", "Zaku Blaxon"))
drivers.append(Driver(2.0, 2.0, 1.0, 1.0, 2.0, 1.0, 24, " 5", "Naxan Noxokolonaxon"))
drivers.append(Driver(4.0, 3.0, 2.0, 4.0, 4.0, 2.0, 8, 44, "Kaxon Kaxutak"))
#1 2 3 4 5 11 19 20 21 22 29 30 31 41 42 44 47 53 69 74 80 81 94 98

TRACK = space_gp

#generate weather conditions
wet = 0
wetness = []
intensity = []
seconds_of_rain_left = 0.0
if TRACK.w == 1: #desert winter
	rfreq = 3.0
	rint = 4.0
	rdur = 7.0
elif TRACK.w == 2: #desert summer
	rfreq = 3.0
	rint = 7.0
	rdur = 3.0
elif TRACK.w == 3: #temperate winter
	rfreq = 7.0
	rint = 5.0
	rdur = 9.0
elif TRACK.w == 4: #temperate summer
	rfreq = 4.0
	rint = 2.0
	rdur = 2.0
elif TRACK.w == 5: #tropics wet
	rfreq = 5.0
	rint = 9.0
	rdur = 5.0
elif TRACK.w == 6: #tropics dry
	rfreq = 1.0
	rint = 7.0
	rdur = 4.0
elif TRACK.w == 7: #subtropic winter
	rfreq = 4.0
	rint = 4.0
	rdur = 7.0
elif TRACK.w == 8: #subtropic summer
	rfreq = 5.0
	rint = 6.0
	rdur = 5.0
elif TRACK.w == 0: #space
	rfreq = 0.0
	rint = 0.0
	rdur = 0.0
else:
	print 'no weather'
#is it raining at start?
if random.random() < rfreq/20.0: #it is raining
	RAIN_FLAG = True
	WET_FLAG = True
	#how long has it been raining?
	seconds_rained = random.random()*rdur*720 #seconds rained for
	#how wet is the track?
	initial_wetness = rint*seconds_rained/5/720
	if initial_wetness > 1:
		initial_wetness = 1.0
	wetness.append(initial_wetness)
	wet = initial_wetness
	#how heavily is it raining?
	intensity.append(math.fabs(random.gauss(rint, rint/5.0)))
	#how long will it continue to rain for?
	seconds_of_rain_left = math.fabs(random.gauss(1, .2))*rdur*720
	seconds_of_rain_left -= seconds_rained
	if seconds_of_rain_left < 0:
		seconds_of_rain_left = 0
	print 'it is raining'
else: #it is dry
	RAIN_FLAG = False
	WET_FLAG = False
	wetness.append(0.0)
	intensity.append(0.0)

#fill in weather values for every 60 seconds
for min in xrange(0, 240): #run for 4 hours
	#it needs to start raining randomly during the race
	if seconds_of_rain_left <= 0: #it's not raining
		intflag = False
		if random.random() < rfreq/20/120: #chance per minute to start raining
			#how heavily is it raining?
			intensity.append(math.fabs(random.gauss(rint, rint/5.0)))
			intflat = True
			#update track wetness
			wet += intensity[-1]*60/5/720
			#how long will it continue to rain for?
			seconds_of_rain_left = math.fabs(random.gauss(1, .2))*rdur*720
		if intflag == False:
			intensity.append(0.0)
		wet -= .003 + wetness[-1]**2/10 #track dries automatically
		if wet > 1:
			wetness.append(1.0)
		elif wet < 0:
			wetness.append(0.0)
		else:
			wetness.append(wet)
	else: #it's raining
		seconds_of_rain_left -= 60
		#how heavily is it raining?
		intensity.append(math.fabs(random.gauss(rint, rint/5.0)))
		#update track wetness
		wet += intensity[-1]*60/5/720
		wet -= .003 + wetness[-1]**2/10 #track dries automatically
		if wet > 1:
			wetness.append(1.0)
		elif wet < 0:
			wetness.append(0.0)
		else:
			wetness.append(wet)

#adjust laptimes during rain based on wetness, adaptability = faster when wetness is closer to .5
#change to wet tires at .5 wetness
#check every lap for wetness and therefore what tires to be on

wfile = open("wetness.txt", "w+")
for value in wetness:
	wfile.write("%.3f\n" % value)
wfile.close()

#determine starting tire
if wetness[0] > 0.5:
	starting_tire_type = "WET"
else:
	starting_tire_type = "DRY"

#starting grid
if QUALIFYING == False:
	for car, driver in zip(cars, drivers):
		car.time = (driver.startpos-1)/2/10.0

#race
file = codecs.open("yay.txt", "w", "utf-8") #open output file
file.write("-- LAP TIMES --\n")
#lap 0 stats first
lap_stats = []
for car, driver in zip(cars, drivers):
	lap_stats.append((driver.num, car.time, False)) #lap 0 stats
	car.tiretype = starting_tire_type #update starting tires to wet if needed
	
file.write('Lap 0\t')

temp = zip(cars, drivers, lap_stats)
temp.sort(key=lambda x: x[0].time, reverse=False)
cars, drivers, lap_stats = [list(a) for a in zip(*temp)]

for stat in lap_stats:
	pit = "    "
	if stat[2] == True:
		pit = stat[3] #DRY or WET
	q = "%s %.3f %s\t" % (stat[0], stat[1], pit)
	file.write(q)
file.write('\n')
#now really race
for k in xrange(0,LAPS):
	lap_stats = []
	retire = []
	
	last_time = 0 #first car is not behind anyone
	last_def = 1 #...
	next_time = 0 #for when the last car is not ahead of anyone
	i = 0 #index for getting driver_behind's distance
	
	file.write('Lap %i\t' % (k+1))
	
	for car, driver in zip(cars, drivers):
		i += 1
		if i <= len(cars)-1:
			next_time = cars[i].time
		RAIN_STATUS_FLAG = False
		if i == 1:
			RAIN_STATUS_FLAG = True
		laptime, pit, tire, out, RAIN_FLAG, WET_FLAG = run_lap(TRACK, QUALIFYING, car, driver, last_time, last_def, next_time, k+1, RAIN_STATUS_FLAG, RAIN_FLAG, WET_FLAG)
		lap_stats.append((driver.num, laptime, pit, tire))
		
		if laptime < car.bestlap:
			car.bestlap = laptime
		
		if out == True:
			retire.append(i-1)
		
		last_time = car.time - laptime #subtract previous laptime because it was just updated
		last_def = driver.d
	
	j = 0
	for retiree_index in retire:
		retcars.append(cars.pop(retiree_index-j))
		retdrivers.append(drivers.pop(retiree_index-j))
		j += 1
		
	temp = zip(cars, drivers, lap_stats)
	temp.sort(key=lambda x: x[0].time, reverse=False)
	cars, drivers, lap_stats = [list(a) for a in zip(*temp)]
	
	for stat in lap_stats:
		pit = "    "
		if stat[2] == True:
			pit = stat[3] #DRY or WET
		q = "%s %.3f %s\t" % (stat[0], stat[1], pit)
		file.write(q)
	file.write('\n')

#final results
temp = zip(cars, drivers)
if QUALIFYING == False:
	temp.sort(key=lambda x: x[0].time, reverse=False)
if QUALIFYING == True:
	temp.sort(key=lambda x: x[0].bestlap, reverse=False)
cars, drivers = zip(*temp)

if len(retcars) > 0:
	temp = zip(retcars, retdrivers)
	temp.sort(key=lambda x: x, reverse=True)
	retcars, retdrivers = zip(*temp)

i = 0
file.write("\n-- OFFICIAL RESULTS --\n")
file.write("Pos\t#No\tDriver\t\t\t\t\t\tTeam\t\t\t\t\tTime\t\tDiff\t\tPits\tBest\n")
first = cars[0].time
for car, driver in zip(cars,drivers):
	i += 1
	if i < 10:
		i1 = "0%i" % i
	else:
		i1 = i
	last_name = driver.name.split(' ')[-1][:3].upper()
	hours = car.time/3600
	minutes = car.time%3600/60
	seconds = car.time%60
	if seconds < 10:
		seconds = "0%.3f" % seconds
	else:
		seconds = "%.3f" % seconds
	diff = car.time - first
	
	#truncate yqtnames
	if len(driver.name) > 23:
		driver_name = driver.name[:23]
	else:
		driver_name = driver.name
	tab1t = len(driver_name)/4
	tab1 = "\t"*(6-tab1t)
	tab2t = len(car.team)/4
	tab2 = "\t"*(6-tab2t)
	diff = "%.3f" % diff
	tab3t = (len(str(diff))+1)/4
	tab3 = "\t"*(3-tab3t)
	p = "%s\t#%s\t%s\t%s%s%s%s%i:%i:%s\t-%s%s%i\t\t%.3f\n" % (i1, driver.num, last_name, driver_name, tab1, car.team, tab2, hours,minutes,seconds, diff, tab3, car.pits, car.bestlap)
	file.write(p)

for car, driver in zip(retcars, retdrivers):
	i += 1
	last_name = driver.name.split(' ')[-1][:3].upper()
	
	#truncate yqtnames
	if len(driver.name) > 23:
		driver_name = driver.name[:23]
	else:
		driver_name = driver.name
	tab1t = len(driver_name)/4
	tab1 = "\t"*(6-tab1t)
	tab2t = len(car.team)/4
	tab2 = "\t"*(6-tab2t)
	
	p = "%s\t#%s\t%s\t%s%s%s%sRETIRED\t\tDNF\t\t\t%i\t\t%.3f\n" % (i, driver.num, last_name, driver_name, tab1, car.team, tab2, car.pits, car.bestlap)
	file.write(p)
	
file.write("\n-- RACE INCIDENT REPORT --\n")

for incident in crashes:
	severity = incident[1]
	lap = incident[2]
	#truncate yqtnames
	if len(incident[0]) > 23:
		driver = incident[0][:23]
	else:
		driver = incident[0]
	if severity == 1:
		type = "made a mistake"
	if severity == 2:
		type = "made a pit stop to repair damage caused by a large incident"
	if severity == 3:
		type = "crashed out"
	overtake = ""
	if incident[3] == True:
		overtake = " while attempting an overtake"
	if severity < 4:
		p = "%s %s%s on lap %i.\n" % (driver, type, overtake, lap)
	elif severity == 4:
		p = "It began to rain on lap %i.\n" % lap
	elif severity == 5:
		p = "The rain ceased on lap %i.\n" % lap
	elif severity == 6:
		p = "The track dried on lap %i.\n" % lap
	file.write(p)

file.close()

#turning - increases time on corners
#topspeed - increases time on straights
#braking - increases time into corners/technical sections
#acceleration - increases time out of corners/in technical sections

#corners - skill in corners
#overtaking - skill at passing people when near them
#defending - skill at preventing passes
#tirewear -
#technical - skill in technical sections