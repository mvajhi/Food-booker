import requests
from bs4 import BeautifulSoup
import csv
import pandas

def main():
    user_pass = get_user_pass()
    flag = False
    with requests.Session() as s:
        while flag == False:
            flag = login(s,user_pass)
            if flag == False:
                print("unsuccessful login!")
                flag = bool(input("try again? 0)yes 1)no"))
        
        info = id_not_scan()
        flag = True
        count = int(0)
        counter = int(0)
        while flag:
            if counter == count:
                counter = int(0)
                count = int(input("how meny do you want? "))
                if count == 0:
                    flag = False

            # send
            stu_request = create_stu_request(info["code"])
            request = s.post("https://dining2.ut.ac.ir/UserFriendGroup/SearchInfo", data=stu_request)
            # resive
            stu_info = ready_stu_info(request, info)
            # save
            if stu_info != []:
                #save_stu_info
                print(stu_info)
                save_stu(stu_info)
                print("Save!")
                #save_next_read_id_in_id.csv
            if int(info["id"]) != 999:
                info["code"] = int(info["code"]) + 1
                save_code()
            else:
                info = id_not_scan()

            counter = 1 + counter


def get_user_pass():
    username = input("enter username: ")
    password = input("enter password: ")
    user_pass = [username, password]
    return user_pass

def login(s,user_pass):
    #go to auth page
    request = s.get("https://dining.ut.ac.ir")
    soup = BeautifulSoup(request.text, "html.parser")
    print("now in " + soup.find("title").text)
    AList = soup.find_all("a")
    login_link_obj = AList[0]
    for i in AList:
        if i.text == "ورود به سامانه":
            login_link_obj = i

    login_link = login_link_obj["href"]
    request = s.get(login_link, verify=False)
    soup = BeautifulSoup(request.text, "html.parser")
    print("now in " + soup.find("title").text)

    #login
    login_post_body = create_login_post_body(soup, user_pass)
    counter = 0
    while True:
        counter = counter + 1
        request = s.post(login_link, data=login_post_body)
        request.text
        soup = BeautifulSoup(request.text, "html.parser")

        print ("try" + str(counter))
        if soup.find("title").text == 'صفحه اصلی - سامانه تغذیه':
            print ("now in " + soup.find("title").text)
            break
        elif counter == 5:
            print ("time out")
            break
    
    request = s.get("https://dining2.ut.ac.ir/UserFriendGroup/ViewSearch")
    soup = BeautifulSoup(request.text, "html.parser")
    if soup.find("title").text == "login":
        print("login :((((")
        return False
    else:
        print("now in " + soup.find("title").text)
        print("successful!!")
        return True


def create_login_post_body(soup, user_pass):
    #find execution
    execution = soup.find("input", attrs={"name":"execution"})["value"]
    print("execution: " + execution[0:20] + "...")
    info = {
        "username" : user_pass[0],
        "password" : user_pass[1],
        "execution": execution,
        "_eventId" : "submit",
        "geolocation":"",
        "submit" : "ÙØ±ÙØ¯"
    }
    return info
        
def create_stu_request(id):
    stu_request = {
        "FirstName" : "",
        "LastName"  : "",
        "IdNumber"  : id
    }
    return stu_request
    

def id_not_scan():
    ids = []
    with open("id.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ids.append(row)
    i = int(0)
    while int(ids[i]["id"]) == 999:
        i = i + 1
    ids [i]["code"] = int(ids[i]["class_id"] + ids[i]["id"])
    ids [i]["row"] = int(i)
    return ids[i]

def ready_stu_info(request, info):
    soup = BeautifulSoup(request.text, "html.parser")
    stuinfo = soup.find_all("td")
    counter = 0
    Sstuinfo = list()

    for i in stuinfo:
        if counter < 3:
            Sstuinfo.append(i.text.replace("\t", "").replace("\n", "").replace("\r",""))
        counter = counter + 1
    # print(Sstuinfo)
    if Sstuinfo == []:
        print("empty")
        return []
    stu_dic = {
        "stu_id"    : Sstuinfo[0],
        "first_name": Sstuinfo[1],
        "last_name" : Sstuinfo[2],
        "college"   : info["college"],
        "field"     : info["field"],
        "degree"    : info["degree"],
        "entrance"  : info["entrance"] 
    }
    return stu_dic

def save_code():
    ids = []
    with open("id.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ids.append(row)
    row = int(0)
    while int(ids[row]["id"]) == 999:
        row = row + 1
    ids[row]["id"] = "{:03d}".format(int(ids[row]["id"]) + 1)
    field = ['class_id', 'id', 'college', 'field', 'degree', 'entrance']

    with open("id.csv", 'w') as file:
        writer = csv.DictWriter(file, fieldnames=field)

        writer.writeheader()
        for i in ids:
            writer.writerow(i)

def save_stu(stu_info):
    field = ["stu_id", "first_name", "last_name", "college", "field", "degree", "entrance"]

    with open("stu_info.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=field)
        writer.writerow(stu_info)



main()