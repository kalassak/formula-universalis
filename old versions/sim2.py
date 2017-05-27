import random
import codecs

POWER = 1.0/110.0
CRASH = .3 #stdev of random factor in crash function
LAPS = 95
QUALIFYING = False

class Car:
	def __init__(self, turning, topspeed, braking, acceleration, pitting, tires, time, bestlap, pits, team):
		self.t = turning
		self.s = topspeed
		self.b = braking
		self.a = acceleration
		self.p = pitting
		self.tires = tires
		self.time = time
		self.bestlap = bestlap
		self.pits = pits
		self.team = team

class Driver:
	def __init__(self, corners, overtaking, defending, tirewear, technical, starting, number, name):
		self.c = corners
		self.o = overtaking
		self.d = defending
		self.t = tirewear
		self.technical = technical
		self.startpos = starting
		self.num = number
		self.name = name

class Track:
	def __init__(self, corners, technical, straights, length):
		self.c = corners
		self.technical = technical
		self.s = straights
		self.l = length
		
def run_lap(track, qualifying, car, driver, car_ahead_time, driver_ahead_def, car_behind_time, lap):
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
		power1 = POWER*track.c/car.t
	if driver.c > track.c:
		power2 = POWER*track.c/driver.c
	if car.s > track.s:
		power3 = POWER*track.s/car.s
	if car.b > track.c:
		power4 = POWER*track.c/car.b
	if car.b > track.technical:
		power5 = POWER*track.technical/car.b
	if driver.t > track.c:
		power6 = POWER*track.c/driver.t
	if driver.t > track.technical:
		power7 = POWER*track.technical/driver.t
	if car.a > track.c:
		power8 = POWER*track.c/car.a
	if car.a > track.technical:
		power9 = POWER*track.technical/car.a
	if driver.technical > track.technical:
		power10 = POWER*track.technical/driver.technical
	cornering = (1/(car.t/track.c)**power1 + 1/(driver.c/track.c)**power2)/2
	topspeed = 1/(car.s/track.s)**power3
	braking = (1/(car.b/track.c)**power4 + 1/(car.b/track.technical)**power5)/2
	acceleration = (1/(car.a/track.c)**power8 + 1/(car.a/track.technical)**power9)/2
	brkacc = (1/(driver.t/track.c)**power6 + 1/(driver.t/track.technical)**power7)/2
	technical = 1/(driver.technical/track.technical)**power10
	wear = 1/(car.tires/80)**(POWER*2)

	#tirewear
	tirewear = track.l/40 * (1/track.c**POWER + 1/track.technical**POWER)/2 * 1/(driver.t)**POWER * 1/(car.tires/100)**.5 #base * track length * track wear * driver skill * how worn tires are already
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
		if pit == True:
			pit_time = 12 + 5 * 1/(car.p/5)**(POWER*20) + random.random()-.5
			car.tires = 100
			car.pits += 1
		else:
			pit_time = 0
	
	#crashing
	#high tire wear, poor skill, and overtaking play into whether or not you will crash each lap
	#three types of crashes: small mistake/disruption, off the course (requires pit), race-ruining (driver dnfs)
	crash = 1 + 1/car.tires*10 + (track.c/car.t + track.c/driver.c + track.technical/driver.technical)/30 + random.gauss(0, CRASH)
	out = False	
	crash_prob = .1 * 130.0/track.l * 1/(car.tires) + (track.c/car.t + track.c/driver.c + track.technical/driver.technical)/3000
	if overtaking_flag == True:
		crash_prob += random.random()*.01
	if random.random() < crash_prob:
		type = random.random() * 10
		if type < 8:
			print 'crash (small)'
			crashes.append((driver.name,1,lap,overtaking_flag))
			crash_time = random.gauss(1.5,.5)
		elif type < 9:
			print 'crash (pits)'
			crashes.append((driver.name,2,lap,overtaking_flag))
			crash_time = 12 + 5 * 1/(car.p/5)**(POWER*20) * (crash) + random.random()-.5 #pitting plus severity of crash for repairs
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
	
	laptime = base * cornering * topspeed * braking * acceleration * brkacc * wear * overtaking + pit_time + crash_time + random.random()-.5
	car.time += laptime
	return laptime, pit, out
		
cars = []
drivers = []

retcars = []
retdrivers = []
crashes = []
		
track1 = Track(3.0, 1.0, 5.0, 30.0)
teralm_gp = Track(2.0, 1.0, 9.0, 105.97)
aeridani_gp = Track(3.0, 8.0, 2.0, 89.84)
ethanthova_gp = Track(3.0, 2.0, 6.0, 55.40)
aiyota_gp = Track(2.0, 9.0, 10.0, 84.03)
czalliso_gp = Track(5.0, 10.0, 5.0, 117.53)
blaland_gp = Track(10.0, 9.0, 7.0, 100.22)
sagua_gp = Track(10.0, 5.0, 1.0, 88.78)
aahrus_gp = Track(8.0, 6.0, 5.0, 131.70)
darvincia_gp = Track(5.0, 2.0, 5.0, 103.36)
wyverncliff_gp = Track(5.0, 1.0, 2.0, 90.00)
dotruga_gp = Track(4.0, 6.0, 5.0, 121.51)
solea_gp = Track(7.0, 8.0, 9.0, 122.68)
bielosia_gp = Track(8.0, 1.0, 7.0, 86.55)
barsein_gp = Track(5.0, 7.0, 1.0, 106.24)
bongatar_gp = Track(5.0, 5.0, 4.0, 77.20)
#               TURN SPD  BRAK ACC  PIT
cars.append(Car(5.0, 5.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Solea Racing")) #27
cars.append(Car(5.0, 5.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Solea Racing"))
cars.append(Car(5.0, 5.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Solea Racing"))
cars.append(Car(7.0, 6.0, 6.0, 6.0, 1.0, 100.0, 0.0, 999.0, 0, "Dotruga Formula Racing")) #26
cars.append(Car(7.0, 6.0, 6.0, 6.0, 1.0, 100.0, 0.0, 999.0, 0, "Dotruga Formula Racing"))
cars.append(Car(7.0, 6.0, 6.0, 6.0, 1.0, 100.0, 0.0, 999.0, 0, "Dotruga Formula Racing"))
cars.append(Car(5.0, 5.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Cows Go Moo Racing")) #23
cars.append(Car(5.0, 5.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Cows Go Moo Racing"))
cars.append(Car(5.0, 5.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Cows Go Moo Racing"))
cars.append(Car(6.0, 5.0, 4.0, 6.0, 1.0, 100.0, 0.0, 999.0, 0, "BONGATAR")) #
cars.append(Car(6.0, 5.0, 4.0, 6.0, 1.0, 100.0, 0.0, 999.0, 0, "BONGATAR"))
cars.append(Car(6.0, 5.0, 4.0, 6.0, 1.0, 100.0, 0.0, 999.0, 0, "BONGATAR"))
cars.append(Car(5.0, 5.0, 4.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team V.V. Imperial")) #25
cars.append(Car(5.0, 5.0, 4.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team V.V. Imperial"))
cars.append(Car(5.0, 5.0, 4.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team V.V. Imperial"))
cars.append(Car(5.0, 4.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Diigikwk Racers")) #26
cars.append(Car(5.0, 4.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Diigikwk Racers"))
cars.append(Car(5.0, 4.0, 5.0, 5.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Diigikwk Racers"))
cars.append(Car(3.0, 5.0, 2.0, 2.0, 2.0, 100.0, 0.0, 999.0, 0, "Team Vikasani")) #
cars.append(Car(3.0, 5.0, 2.0, 2.0, 2.0, 100.0, 0.0, 999.0, 0, "Team Vikasani"))
cars.append(Car(3.0, 5.0, 2.0, 2.0, 2.0, 100.0, 0.0, 999.0, 0, "Team Vikasani"))
cars.append(Car(5.0, 5.0, 2.0, 3.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Vincent")) #16
cars.append(Car(5.0, 5.0, 2.0, 3.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Vincent"))
cars.append(Car(5.0, 5.0, 2.0, 3.0, 1.0, 100.0, 0.0, 999.0, 0, "Team Vincent"))
#					  CRN  OVTK DEF  FINE TECH
drivers.append(Driver(6.0, 5.0, 1.0, 4.0, 4.0, 2, 47, u"ketila léqa pavúteka")) #17
drivers.append(Driver(5.0, 3.0, 4.0, 3.0, 2.0, 7, 19, u"khélok atep zailunaɰ")) #17
drivers.append(Driver(3.0, 2.0, 3.0, 5.0, 2.0, 3, 31, u"xap'ít celentir šaŋév")) #17
drivers.append(Driver(5.0, 5.0, 4.0, 5.0, 4.0, 8, 29, "Sago Aludetsei")) #18
drivers.append(Driver(4.0, 2.0, 3.0, 2.0, 4.0, 12, 11, "Tuto Keget")) #14
drivers.append(Driver(4.0, 2.0, 4.0, 3.0, 2.0, 9, 98, "Gorga Motxev")) #15
drivers.append(Driver(4.0, 3.0, 3.0, 3.0, 3.0, 16, 41, "Olga Candy")) #15
drivers.append(Driver(4.0, 3.0, 3.0, 3.0, 2.0, 13, 69, "Marisa Sanchez")) #15
drivers.append(Driver(9.0, 5.0, 3.0, 5.0, 4.0, 1, 42, "Frank Oosterhout")) #21
drivers.append(Driver(7.0, 7.0, 5.0, 5.0, 5.0, 4, 30, "Josh Wise")) #23
drivers.append(Driver(3.0, 3.0, 4.0, 1.0, 5.0, 17, " 2", "Body Hide")) #14
drivers.append(Driver(1.0, 2.0, 1.0, 5.0, 5.0, 14, " 3", "Bob")) #14
drivers.append(Driver(7.0, 6.0, 3.0, 5.0, 4.0, 6, 80, u"Ifloenne é Aya")) #19
drivers.append(Driver(4.0, 3.0, 2.0, 4.0, 3.0, 11, 81, u"Lyǽs Kæræsekæræn")) #16
drivers.append(Driver(1.0, 1.0, 1.0, 2.0, 3.0, 18, 82, u"Nukki Savra Sanda")) #8
drivers.append(Driver(3.0, 5.0, 4.0, 3.0, 4.0, 10, 74, u"Bařàsiz Konoca")) #18
drivers.append(Driver(5.0, 5.0, 3.0, 3.0, 3.0, 5, 94, u"At'ipi Nesbeksë")) #18
drivers.append(Driver(2.0, 1.0, 3.0, 4.0, 6.0, 15, 53, u"Ešuro Tàcràɰë")) #15
drivers.append(Driver(3.0, 2.0, 3.0, 4.0, 4.0, 19, 35, u"Asaúni Akaleta")) #15
drivers.append(Driver(3.0, 3.0, 4.0, 3.0, 5.0, 21, 26, "Rikvisi Iliria")) #16
drivers.append(Driver(4.0, 3.0, 3.0, 3.0, 3.0, 20, 14, u"Daseno Húctu")) #15
drivers.append(Driver(5.0, 5.0, 5.0, 5.0, 2.0, 21, 20, "Mac")) #17
drivers.append(Driver(6.0, 5.0, 4.0, 3.0, 2.0, 17, 21, "Orson")) #16
drivers.append(Driver(5.0, 5.0, 5.0, 3.0, 2.0, 15, 22, "Philipe")) #15
#2 3 11 14 19 20 21 22 26 29 30 31 35 41 42 47 53 69 74 80 81 82 94 98

#race 3 upgrades
#blotz - updated
#dar - updated
#kal - updated
#tmc - updated
#matty - 
#tuto - updated
#fiah - updated
#swonx - 
#https://www.facebook.com/groups/178891018828976/
#automated tracking, before bonnie so it makes its own track
#organize ibtracs database
#update imgget with archived

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
	
file.write('Lap 0\t')

temp = zip(cars, drivers, lap_stats)
temp.sort(key=lambda x: x[0].time, reverse=False)
cars, drivers, lap_stats = [list(a) for a in zip(*temp)]

for stat in lap_stats:
	pit = "    "
	if stat[2] == True:
		pit = "PIT"
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
		laptime, pit, out = run_lap(bongatar_gp, QUALIFYING, car, driver, last_time, last_def, next_time, k+1)
		lap_stats.append((driver.num, laptime, pit))
		
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
			pit = "PIT"
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
	p = "%s %s%s on lap %i.\n" % (driver, type, overtake, lap)
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