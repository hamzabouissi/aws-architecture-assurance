
import time
import random
source = open("cloudformation/vpc-subnet-test.yml","r")
destination = open("cloudformation/vpc-subnet.yml","a")

while True:
    char = source.read(1)
    time.sleep(random.uniform(0.01,0.08))
    if not char:
        print('Reached end of file')
        break
    destination.write(char)
    destination.flush()

source.close()
destination.close()
