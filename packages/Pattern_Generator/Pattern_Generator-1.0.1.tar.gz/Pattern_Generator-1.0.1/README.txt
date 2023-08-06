Pattern Generator V1.0.0
Initial version

Generates a byte array of given length with fixed values, random data or running byte sequence.
A start offset, minimum and maximum value of the running byte sequence can be changed by parameters.
All pattern types support 2 bytes of pattern length in front which can be switched on and off.

Example:

patGen = PatternGenerator()
patGen.set_random(True, 10)
data = patGen.get_data_pattern()
for i in data:
print(hex(i))

patGen.set_value(True, 1024, 0xaa)
data = patGen.get_data_pattern()
for i in data:
print(hex(i))

patGen.set_running_byte(False, True, 1, minValue=0x00, maxValue=0x1F)
for i in range(20):
print("Data",i+1)
data = patGen.get_data_pattern(numData = i+1)
for i in data:
    print (hex(i))

V1.0.1
Bugfix: Running byte generator didn't generate a pattern of 128 bytes on special circumstances  
