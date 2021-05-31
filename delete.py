import os

for i in range(50):
    name = "img_to_client_ver_{}.jpg".format(i)
    if os.path.exists(name):
        os.remove(name)
if os.path.exists("img_to_server.jpg"):
    os.remove("img_to_server.jpg")

ar = os.listdir()
for i in range(len(ar)):
    if ar[i].__contains__("archived") or ar[i].__contains__("c2") or ar[i].__contains__("c3"):
        os.remove(ar[i])
