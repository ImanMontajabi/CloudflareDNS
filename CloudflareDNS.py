from PyQt6.QtGui import QIcon, QFont, QPixmap, QRegularExpressionValidator
from PyQt6.QtCore import QSize, QObject, QThread, pyqtSignal, Qt, QRegularExpression
import sys
import os
import re
import requests
import json
from PyQt6.QtWidgets import (
     QApplication,
     QMainWindow,
     QLabel,
     QPushButton,
     QFileDialog,
     QLineEdit,
     QPlainTextEdit
     )

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
icon = os.path.join(base_path, './assets/logo.png')
github = os.path.join(base_path, './assets/github.png')
twitter = os.path.join(base_path, './assets/twitter.png')
output_file = os.path.join(base_path, './assets/file.png')
listpng = os.path.join(base_path, './assets/list.png')
createpng = os.path.join(base_path, './assets/create.png')
deletepng = os.path.join(base_path, './assets/delete.png')
exportpng = os.path.join(base_path, './assets/exportpng.png')
max_ips = 100

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(tuple)
    def list(self):
        with open('user_id.json', 'r') as json_file:
            user_data = json.load(json_file)

        email = user_data['email']
        api_token = user_data['api_token']
        zone_id = user_data['zone_id']
        domain = user_data['domain']
        dns_record_name = user_data['ip_dns_record']
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'


        headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_token,
            'Content-Type': 'application/json'
        }
        dns_records = []
        page_num = 1
        while True:  # loop over all pages
            params = {'page': page_num, 'per_page': 100}  # update pagination params
            response = requests.request('GET', url, headers=headers, params=params)
            data = response.json()['result']
            if not data:  # no more records to fetch
                break
            for record in data:  # add records to the list
                dns_records.append(record)
            page_num += 1
        i_num = 0
        for record in dns_records:
            subdomain = record['name']
            this_domain = record['zone_name']
            this_dns_record = subdomain.replace(f".{this_domain}", "")
            if this_dns_record == dns_record_name:
                content = record['content']
                self.progress.emit((i_num + 1, subdomain, content, ""))
                i_num += 1
            self.finished.emit()
        self.finished.emit()
# export list 
    def export_list(self):
        with open('user_id.json', 'r') as json_file:
            user_data = json.load(json_file)

        email = user_data['email']
        api_token = user_data['api_token']
        zone_id = user_data['zone_id']
        domain = user_data['domain']
        dns_record_name = user_data['ip_dns_record']
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'


        headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_token,
            'Content-Type': 'application/json'
            }
        dns_records = []
        page_num = 1
        export_list = []
        while True:  # loop over all pages
            params = {'page': page_num, 'per_page': 100}  # update pagination params
            response = requests.request('GET', url, headers=headers, params=params)
            data = response.json()['result']
            if not data:  # no more records to fetch
                    break
            for record in data:  # add records to the list
                dns_records.append(record)
            page_num += 1
        i_num = 0
        for number, record in enumerate(dns_records):
            subdomain = record['name']
            this_domain = record['zone_name']
            this_dns_record = subdomain.replace(f".{this_domain}", "")
            if this_dns_record == dns_record_name:
                content = record['content']
                export_list.append(f"{number} - {content}")
                self.progress.emit((i_num + 1, subdomain, content,"✓"))
                i_num += 1
        with open(f"{dns_record_name}.{domain}.txt", "w") as f:
            f.write("\n".join(export_list))
            f.close()
            self.finished.emit()
        self.finished.emit()
# craete DNS record from scan file
    def create(self): 
        def scan_to_iplist():
            with open(self.json_path_create, 'r') as f:
                data = json.load(f)
            ip_list = [i['ip'] for i in data['workingIPs']]
            f.close()
            return ip_list
        def linux_scan_to_iplist():
            with open(self.json_path_create, 'r') as f:
                data = f.readlines()
            ips = []
            for item in data:        # iterate over the list items
                result = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', item) # extract the IP using regular expression
                if result:          # check if IP is found and add to the list
                    ips.append(result.group(0))
            return ips
        def iplist_to_iptext():
            try:
                iplist = scan_to_iplist()
            except:
                iplist = linux_scan_to_iplist()
            with open('ip.txt', 'w') as f:
                    f.write('\n'.join(iplist))
        iplist_to_iptext()
        def ip_list():
            with open ('ip.txt', 'r') as f:
                myip = [line.strip() for line in f]
                f.close()
                return myip

        all_ips = ip_list()
        len_all_ips = len(all_ips)
        def bestip():
            filename = "best_ip.txt"
            topUnder100ip = []
            
            ipn = 0
            while(ipn < len_all_ips): 
                topUnder100ip.append(all_ips[ipn])
                ipn += 1
                if  ipn >= max_ips:
                    break

            with open(filename, "w") as f:
                f.write("\n".join(topUnder100ip))
            f.close()
        bestip()
        with open("best_ip.txt", "r") as ip:
            lines = ip.readlines()
        topUnder100ipList = [line.strip() for line in lines]

        with open('user_id.json', 'r') as json_file:
            user_data = json.load(json_file)
        email = user_data['email']
        api_token = user_data['api_token']
        zone_id = user_data['zone_id']
        record_name = user_data["ip_dns_record"]
        domain = user_data["domain"]
        try:
            max_ip_user = int(user_data["max_ip"])
        except:
            max_ip_user = len(topUnder100ipList)

        params_name = f'{record_name}.{domain}'
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        headers = {
                    "Content-Type": "application/json",
                    "X-Auth-Email": email,
                    "X-Auth-Key": api_token
                }
        ipn = 0
        while(ipn < len(topUnder100ipList)):
            data = {
                "type": "A",
                "name": params_name,
                "content": f"{topUnder100ipList[ipn]}",
                "ttl": 1,
                "proxied": False
            }
            if (ipn >= max_ip_user):
                break
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                subdomain = response.json()["result"]["name"]
                message_content = response.json()["result"]["content"]
                self.progress.emit((ipn + 1, subdomain, message_content," ✓ added"))
                ipn += 1
            if response.status_code == 400:
                subdomain = f"{record_name}.{domain}"
                message_content = topUnder100ipList[ipn]    
                self.progress.emit((ipn + 1, subdomain, message_content, " ✘ exist"))
                ipn += 1
            if  ipn >= max_ips:
                break
        self.finished.emit()
        # ===================================================================================
    def delete(self):
        with open('user_id.json', 'r') as json_file:
            user_data = json.load(json_file)
                
        email = user_data['email']
        api_token = user_data['api_token']
        zone_id = user_data['zone_id']
        domain = user_data['domain']
        dns_record_name = user_data["ip_dns_record"]
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
        headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_token,
        'Content-Type': 'application/json'
        }
        page_num = 1
        i_num = 0    
        while True:
            params = {"page": page_num,"per_page": 100}
            response = requests.request("GET", url, headers=headers, params=params)
            data = response.json()["result"]
            if not data:
                break

            for record in data:
                if record["name"] == f"{dns_record_name}.{domain}":
                    url_del = f"{url}/{record['id']}"
                    requests.delete(url_del, headers=headers)
                    self.progress.emit((i_num + 1, record["name"], record["content"], " ✓ deleted"))
                    i_num += 1
            page_num += 1
        self.finished.emit()
# Main WindowApp
class CloudflareDNS(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
# open file dialog window to select result file
        self.createButton.setEnabled(False)
        self.json_path_create = None
        self.browse_dialog = QFileDialog(self)
        self.browse_dialog.setNameFilter('SCAN files (*.json *.cf)')
        self.browse_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.browse_dialog.fileSelected.connect(self.open_file)
# open user_id file
        file_path = 'user_id.json'
        if os.path.exists(file_path):
            self.load_input_values()
# setup UI of main Window 
    def setupUi(self):
        self.setFixedSize(260, 405)
        self.move(5, 5)
        self.setWindowTitle("CloudflareDNS")
        self.setWindowIcon(QIcon(icon))
        self.label_1 = QLabel(self)
        self.label_1.move(5, 365)
        image_1 = QPixmap(github)     
        self.label_1.setPixmap(image_1)
        self.label_1.setOpenExternalLinks(True)
        self.label_1.setText(f'<a href="https://github.com/ImanMontajabi/CloudflareDNS"><img src="{github}"></a>')
        self.label_2 = QLabel(self)
        self.label_2.move(50, 365)
        image_2 = QPixmap(twitter)
        self.label_2.setPixmap(image_2)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setText(f'<a href="https://twitter.com/ImanMontajabi"><img src="{twitter}"></a>')
        self.email()
        self.api_token()
        self.zone_id()
        self.domain()
        self.name()
        self.show_output()
        self.maxip()

        self.listButton = QPushButton(self)        # list button
        self.listButton.setGeometry(5, 160, 37, 37)
        self.listButton.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.listButton.setIcon(QIcon(listpng))
        self.listButton.setIconSize(QSize(45, 48))
        self.listButton.clicked.connect(self.list_clicked)

        self.exportlistButton = QPushButton(self)        # list button
        self.exportlistButton.setGeometry(46, 160, 37, 37)
        self.exportlistButton.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.exportlistButton.setIcon(QIcon(exportpng))
        self.exportlistButton.setIconSize(QSize(37, 28))
        self.exportlistButton.clicked.connect(self.exportlist_clicked)
        
        self.createButton = QPushButton(self)        # create button
        self.createButton.setGeometry(175, 160, 37, 37)
        self.createButton.setIcon(QIcon(createpng))
        self.createButton.setIconSize((QSize(40, 40)))
        self.createButton.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.createButton.clicked.connect(self.create_clicked)
        # delete button
        self.deleteButton = QPushButton(self)        
        self.deleteButton.setGeometry(215, 160, 37, 37)
        self.deleteButton.setIcon(QIcon(deletepng))
        self.deleteButton.setIconSize((QSize(43, 43)))
        self.deleteButton.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.deleteButton.clicked.connect(self.delete_clicked)
        #result.json button
        self.resultButton = QPushButton(self)   
        self.resultButton.setGeometry(87, 160, 85, 37)
        self.resultButton.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.resultButton.setIcon(QIcon(output_file))
        self.resultButton.setIconSize(QSize(70, 70))
        self.resultButton.clicked.connect(self.get_file_path)
        self.resultButton.clicked.connect(self.refresh_buttons)

        
    def get_file_path(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter('SCAN files (*.json *.cf)')
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.fileSelected.connect(self.open_file)
        file_dialog.show()

    def open_file(self, file_path):
        if file_path:
            self.json_path = file_path
            self.json_path_create = file_path
            self.refresh_buttons()
            
    def refresh_buttons(self):
        is_create_enabled = False
        if self.json_path_create:
            is_create_enabled = True
        self.createButton.setEnabled(is_create_enabled)
# show output in a QPlainText
    def show_output(self):
        self.otext = QPlainTextEdit(self)
        self.otext.setGeometry(5, 240, 250, 120)
        self.otext.setStyleSheet("background-color: black; color: white; border-radius : 10px")
        self.otext.setFont(QFont("Cascadia Code", 10))
        self.otext.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.otext.setReadOnly(True)
# set user id in user_id file
    def email(self):                                
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("email")
        self.input_text.setGeometry(5, 10, 250, 25)
        self.input_text.setFont(QFont("Comic Sans MS", 10, QFont.Weight.Bold))
        self.input_text.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.input_text.setPlaceholderText("example@mail.com")
    def api_token(self):
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("api_token")
        self.input_text.setFont(QFont("Comic Sans MS", 9, QFont.Weight.Bold))
        self.input_text.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.input_text.setGeometry(5, 40, 250, 25)
        self.input_text.setPlaceholderText("Global API Key")
    def zone_id(self):
        self.input_text = QLineEdit(self)
        self.input_text.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.input_text.setFont(QFont("Comic Sans MS", 9, QFont.Weight.Bold))
        self.input_text.setObjectName("zone_id")
        self.input_text.setGeometry(5, 70, 250, 25)
        self.input_text.setPlaceholderText("Zone ID")
    def domain(self):
        self.input_text = QLineEdit(self)
        self.input_text.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.input_text.setFont(QFont("Comic Sans MS", 10, QFont.Weight.Bold))
        self.input_text.setObjectName("domain")
        self.input_text.setGeometry(5, 100, 250, 25)
        self.input_text.setPlaceholderText("mydomain.com")
    def name(self):
        self.input_text = QLineEdit(self)
        self.input_text.setStyleSheet("border-radius : 10px; border : 2px solid black")
        self.input_text.setFont(QFont("Comic Sans MS", 10, QFont.Weight.Bold))
        self.input_text.setObjectName("name")
        self.input_text.setGeometry(5, 130, 250, 25)
        self.input_text.setPlaceholderText("DNS record name")
    def maxip(self):
        self.input_text = QLineEdit(self)
        self.input_text.setStyleSheet("border-radius : 10px; border : 2px solid black")
        reg_ex = QRegularExpression("(?!0)\\d{1,2}|100")
        validator = QRegularExpressionValidator(reg_ex, self.input_text)
        self.input_text.setValidator(validator)
        self.input_text.setFont(QFont("Comic Sans MS", 8, QFont.Weight.Bold))
        self.input_text.setObjectName("maxip")
        self.input_text.setGeometry(5, 205, 90, 25)
        self.input_text.setPlaceholderText("1≤max ip≤100")

    def load_input_values(self):
        with open('user_id.json', 'r') as f:
            user_data = json.load(f)
        self.findChild(QLineEdit, "email").setText(user_data['email'])
        self.findChild(QLineEdit, "api_token").setText(user_data['api_token'])
        self.findChild(QLineEdit, "zone_id").setText(user_data['zone_id'])
        self.findChild(QLineEdit, "domain").setText(user_data['domain'])
        self.findChild(QLineEdit, "name").setText(user_data['ip_dns_record'])
        self.findChild(QLineEdit, "maxip").setText(user_data['max_ip'])
        self.refresh_buttons()

    def get_input_values(self):
        user_data = {}
        user_data['email'] = self.findChild(QLineEdit, "email").text()
        user_data['api_token'] = self.findChild(QLineEdit, "api_token").text()
        user_data['zone_id'] = self.findChild(QLineEdit, "zone_id").text()
        user_data['domain'] = self.findChild(QLineEdit, "domain").text()
        user_data['ip_dns_record'] = self.findChild(QLineEdit, "name").text()
        user_data['max_ip'] = self.findChild(QLineEdit, "maxip").text()
        return user_data
    def save_input_values(self):
        with open('user_id.json', 'w') as f:
            json.dump(self.get_input_values(), f)

    def update_text(self, data):
        row_num, ip, message = data[0], data[2], data[3]
        text = f"{row_num}) {ip} {message}\n"
        self.otext.insertPlainText(text)
        
    def list_clicked(self):
        self.save_input_values()
        self.thread = QThread()
        self.worker = Worker()
        self.otext.clear()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_text)
        self.thread.started.connect(self.worker.list)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.exportlistButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.exportlistButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.refresh_buttons())
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.resultButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.resultButton.setEnabled(True))

    def exportlist_clicked(self):
        self.save_input_values()
        self.thread = QThread()
        self.worker = Worker()
        self.otext.clear()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_text)
        self.thread.started.connect(self.worker.export_list)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.exportlistButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.exportlistButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.refresh_buttons())
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.resultButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.resultButton.setEnabled(True))
        
    def create_clicked(self):
        self.save_input_values()
        self.thread = QThread()
        self.worker = Worker()
        self.otext.clear()
        self.worker.json_path_create = self.json_path
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_text)
        self.thread.started.connect(self.worker.create)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.exportlistButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.exportlistButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.createButton.setEnabled(True))
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.resultButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.resultButton.setEnabled(True))

    def delete_clicked(self):
        self.save_input_values()       
        self.thread = QThread()
        self.worker = Worker()
        self.otext.clear()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_text)
        self.thread.started.connect(self.worker.delete)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.exportlistButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.exportlistButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.refresh_buttons())
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.resultButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.resultButton.setEnabled(True))

app = QApplication(sys.argv)
window = CloudflareDNS()
window.show()
sys.exit(app.exec())