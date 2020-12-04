import io

import requests
from PyPDF2 import PdfFileReader
import csv
import time

apiKey = ""

def getBillText(url):
    r = requests.get(url)
    f = io.BytesIO(r.content)
    reader = PdfFileReader(f)
    pgs = reader.getNumPages()
    # neaten the text
    contents = " ".join([reader.getPage(n).extractText() for n in range(pgs)])
    contents = " ".join([n.lstrip('0123456789.- ') for n in contents.split("\n")])
    return contents

## test getBillText
# print(getBillText('http://www.legis.ga.gov/Legislation/20212022/195566.pdf'))



## just so console counts
billCount = 0

# there are 460 pages of 20 bills, so we need 23 sets
for setNo in range(23):
    with open('gaBills' + str(setNo) + '.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, ["status", "passDate", "text"])
        dict_writer.writeheader()
        startPg = setNo * 20 + 1
        endPg = (setNo+1) * 20
        print("[SET]" + str(setNo))
        for pg in range(startPg, endPg):
            apiUrl = "https://v3.openstates.org/bills?jurisdiction=Georgia&sort=updated_desc&include=versions&page=" + str(pg) + "&per_page=20&apikey=" + apiKey
            bills = requests.get(apiUrl).json()
            # go through them
            try:
                for bill in bills["results"]:
                    try:
                        status = bill["latest_action_description"]
                        passDate = bill["latest_passage_date"]
                        txt = getBillText(bill["versions"][0]["links"][0]["url"])
                        dict_writer.writerow({"status":status, "passDate":passDate, "text":txt})
                        billCount += 1
                        print("[BILL]" + str(billCount))
                    except Exception as e:
                        print("error with bill format: " + str(e))
                # we are rate limited
                print("[PG]" + str(pg))
                time.sleep(10)
            except Exception as e:
                print(bills)
                print(bills.keys())
                print("error with bills format: " + str(e))
