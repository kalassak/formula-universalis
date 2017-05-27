# this file tests for unicode support

import codecs

name = u"xap'\u0160t celentir lsang\u00edv"

file = codecs.open("yay.txt", "w", "utf-8")
file.write(name)
file.close()

print name