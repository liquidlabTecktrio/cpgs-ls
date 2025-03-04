
old = [{"name":"a"},{"li":"lfkjsld"},1,1]
new = [{"name":"a"},{"li":""},1,1]


indexThatchanged = []
status = 'unknown'
for index in range(len(old)):
        if old[index] != new[index]:
            indexThatchanged.append(index)
            if new[index]['li'] == "":
                  status = 'vacant'
            else:
                  status = "occupied"
print(indexThatchanged, status)