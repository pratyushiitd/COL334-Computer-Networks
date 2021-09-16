import matplotlib.pyplot as plt
import time
# x axis values
# Writing to file
file1 = open('res/rtt_vals.txt', 'r')
count = 0
 # corresponding y axis values
y = []
x = []
for line in file1:
    count += 1
    x.append(count)
    y.append((float)(line))
file1.close()
# plotting the points 
plt.plot(x, y)
  
# naming the x axis
plt.xlabel('Hops')
# naming the y axis
plt.ylabel("Round Return Time (sec)")
  
# giving a title to my graph
plt.title('Round Trip Time vs Hops')
  
# function to show the plot
plt.savefig('plot.png', dpi=300, bbox_inches='tight')
plt.show()
plt.close()