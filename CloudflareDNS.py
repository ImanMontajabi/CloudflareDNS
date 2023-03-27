from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import QSize, QObject, QThread, pyqtSignal, Qt
import sys
import os
import requests
import json
from PyQt6.QtWidgets import (
     QApplication,
     QMainWindow,
     QLabel,
     QPushButton,
     QTableWidget,
     QTableWidgetItem,
     QFileDialog,
     QLineEdit)

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
icon = os.path.join(base_path, './assets/logo.png')
github = os.path.join(base_path, './assets/github.png')
twitter = os.path.join(base_path, './assets/twitter.png')
jfile = os.path.join(base_path, './assets/file.png')

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
                i_num += 1
                self.progress.emit((i_num - 1, subdomain, content,"succeed", ""))
            self.finished.emit()



        """
        i_num = 0
        for i in range(len(data)):
            subdomain = data[i]['name']
            domain = data[i]['zone_name']
            record_name = subdomain.replace(f".{domain}", "")
            if record_name == ip_name:
                content = data[i]['content']
                i_num += 1"""
        


                #self.progress.emit((i_num - 1, subdomain, content,"succeed", ""))
        
        #self.finished.emit()
        # ===================================================================================
    def create(self):
        def scan_to_iplist():
            with open(self.json_path_create, 'r') as f:
                data = json.load(f)
            ip_list = [i['ip'] for i in data['workingIPs']]
            f.close()
            return ip_list
        def iplist_to_iptext():
            iplist = scan_to_iplist()
            with open('ip.txt', 'w') as f:
                    f.write('\n'.join(iplist))
        iplist_to_iptext()
        def ip_list():
            with open ('ip.txt', 'r') as f:
                myip = [line.strip() for line in f]
                f.close()
                return myip
        def bestip():
            filename = "best_ip.txt"
            top100ip = []
            for i in range(100):
                top100ip.append(ip_list()[i])
            with open(filename, "w") as f:
                f.write("\n".join(top100ip))
            f.close()
        bestip()
        with open("best_ip.txt", "r") as ip:
            lines = ip.readlines()
        top100ipList = [line.strip() for line in lines]
        with open('user_id.json', 'r') as json_file:
            user_data = json.load(json_file)
        email = user_data['email']
        api_token = user_data['api_token']
        zone_id = user_data['zone_id']
        record_name = user_data["ip_dns_record"]
        domain = user_data["domain"]
        params_name = f'{record_name}.{domain}'
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        headers = {
                    "Content-Type": "application/json",
                    "X-Auth-Email": email,
                    "X-Auth-Key": api_token
                }
        for i in range(100):
            data = {
                "type": "A",
                "name": params_name,
                "content": f"{top100ipList[i]}",
                "ttl": 1,
                "proxied": False
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                subdomain = response.json()["result"]["name"]
                message_content = response.json()["result"]["content"]
                self.progress.emit((i, subdomain, message_content,"added", ""))
            if response.status_code == 400:
                subdomain = f"{record_name}.{domain}"
                message_content = top100ipList[i]    
                self.progress.emit((i, subdomain, message_content,"already exist", ""))
        self.finished.emit()
        # ===================================================================================
    def delete(self):
        def listip():
            with open('user_id.json', 'r') as json_file:
                user_data = json.load(json_file)
                
            email = user_data['email']
            api_token = user_data['api_token']
            zone_id = user_data['zone_id']
            ip_name = user_data["ip_dns_record"]
            url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
            headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_token,
            'Content-Type': 'application/json'
            }
            response = requests.request('GET', url, headers=headers)
            data = response.json()['result']
            ip = []
            for i in range(len(data)):
                a = data[i]['name']
                b = data[i]['zone_name']
                c = a.replace(f".{b}", "")
                if c == ip_name:
                    ip.append(data[i]['content'])
            return ip
        with open('user_id.json', 'r') as json_file:
            user_data = json.load(json_file)
        email = user_data['email']
        api_token = user_data['api_token']
        zone_id = user_data['zone_id']
        ip_name = user_data["ip_dns_record"]
        params_name = f'{user_data["ip_dns_record"]}.{user_data["domain"]}'
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": email,
            "X-Auth-Key": api_token
        }
        params = {
            "name": params_name,
            "per_page": 100
        }
        response = requests.get(url, headers=headers, params=params)
        dns_response_result = response.json()['result']
        iplist = listip()
        i = 0
        for ip in iplist:
            for record in dns_response_result:
                if record["content"] == ip:
                    url_del = f"{url}/{record['id']}"
                    response = requests.delete(url_del, headers=headers)
                    if response.status_code == 200:
                        self.progress.emit((i, record["name"], record["content"], "deleted", ""))
                        i += 1
        self.finished.emit()
#=============================================================================
class CloudflareDNS(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_table)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.browse_dialog = QFileDialog(self)
        self.browse_dialog.setNameFilter('JSON files (*.json)')
        self.browse_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.browse_dialog.fileSelected.connect(self.open_file)
        file_path = 'user_id.json'
        if os.path.exists(file_path):
            self.load_input_values()
            
    def setupUi(self):
        self.setFixedSize(700, 400)
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

        self.table()

        self.listButton = QPushButton("List", self)        # list button
        self.listButton.setGeometry(5, 208, 70, 45)
        self.listButton.setFont(QFont("arial", 16))
        self.listButton.clicked.connect(self.list_clicked)

        self.createButton = QPushButton("Create", self)        # create button
        self.createButton.setGeometry(95, 208, 70, 45)
        self.createButton.setFont(QFont("arial", 16))
        self.createButton.clicked.connect(self.create_clicked)


        self.deleteButton = QPushButton("Delete", self)        # delete button
        self.deleteButton.setGeometry(185, 208, 70, 45)
        self.deleteButton.setFont(QFont("arial", 16))
        self.deleteButton.clicked.connect(self.delete_clicked)

        self.jsonbutton = QPushButton("result.json", self)   #result.json button
        self.jsonbutton.setGeometry(5, 160, 250, 45)
        self.jsonbutton.setFont(QFont("arial", 16))
        self.jsonbutton.setIcon(QIcon(jfile))
        self.jsonbutton.setIconSize(QSize(22, 22))
        self.jsonbutton.clicked.connect(self.get_file_path)
        
    def get_file_path(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter('JSON files (*.json)')
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.fileSelected.connect(self.open_file)
        file_dialog.show()

    def open_file(self, file_path):
        if file_path:
            self.json_path = file_path

    def table(self):
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(265, 10, 420, 390)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(1000)
        self.tableWidget.setHorizontalHeaderLabels(["Subdomain", "IP", "Message"])
        self.tableWidget.horizontalHeaderItem(0).setFont(QFont("arial", 12, QFont.Weight.Bold))
        self.tableWidget.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.horizontalHeaderItem(1).setFont(QFont("arial", 12, QFont.Weight.Bold))
        self.tableWidget.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.horizontalHeaderItem(2).setFont(QFont("arial", 12, QFont.Weight.Bold))
        self.tableWidget.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setFixedHeight(380)  # fixed size of table
        self.tableWidget.horizontalHeaderItem
        self.tableWidget.setColumnWidth(0, 180)
        self.tableWidget.setColumnWidth(1, 85)
        self.tableWidget.setColumnWidth(2, 100)
        
        
    def email(self):                                # set user id
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("email")
        self.input_text.setGeometry(5, 10, 250, 25)
        self.input_text.setPlaceholderText("example@mail.com")
    def api_token(self):
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("api_token")
        self.input_text.setGeometry(5, 40, 250, 25)
        self.input_text.setPlaceholderText("Global API Key")
    def zone_id(self):
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("zone_id")
        self.input_text.setGeometry(5, 70, 250, 25)
        self.input_text.setPlaceholderText("Zone ID")
    def domain(self):
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("domain")
        self.input_text.setGeometry(5, 100, 250, 25)
        self.input_text.setPlaceholderText("mydomain.com")
    def name(self):
        self.input_text = QLineEdit(self)
        self.input_text.setObjectName("name")
        self.input_text.setGeometry(5, 130, 250, 25)
        self.input_text.setPlaceholderText("DNS record name")
    def load_input_values(self):
        with open('user_id.json', 'r') as f:
            user_data = json.load(f)
        self.findChild(QLineEdit, "email").setText(user_data['email'])
        self.findChild(QLineEdit, "api_token").setText(user_data['api_token'])
        self.findChild(QLineEdit, "zone_id").setText(user_data['zone_id'])
        self.findChild(QLineEdit, "domain").setText(user_data['domain'])
        self.findChild(QLineEdit, "name").setText(user_data['ip_dns_record'])

    def get_input_values(self):
        user_data = {}
        user_data['email'] = self.findChild(QLineEdit, "email").text()
        user_data['api_token'] = self.findChild(QLineEdit, "api_token").text()
        user_data['zone_id'] = self.findChild(QLineEdit, "zone_id").text()
        user_data['domain'] = self.findChild(QLineEdit, "domain").text()
        user_data['ip_dns_record'] = self.findChild(QLineEdit, "name").text()
        return user_data
    def save_input_values(self):
        with open('user_id.json', 'w') as f:
            json.dump(self.get_input_values(), f)

    
    def update_table(self, data):
        row_num, subdomain, ip, message = data[0], data[1], data[2], data[3]
        item_subdomain = QTableWidgetItem(subdomain)
        item_subdomain.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_ip = QTableWidgetItem(ip)
        item_ip.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_message = QTableWidgetItem(message)
        item_message.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableWidget.setItem(row_num, 0, item_subdomain)
        self.tableWidget.setItem(row_num, 1, item_ip)
        self.tableWidget.setItem(row_num, 2, item_message)
        
    def list_clicked(self):
        self.save_input_values()
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_table)
        self.thread.started.connect(self.worker.list)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.createButton.setEnabled(True))
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.jsonbutton.setEnabled(False)
        self.thread.finished.connect(lambda:self.jsonbutton.setEnabled(True))
        
    def create_clicked(self):
        self.save_input_values()
        self.thread = QThread()
        self.worker = Worker()
        self.worker.json_path_create = self.json_path
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_table)
        self.thread.started.connect(self.worker.create)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.createButton.setEnabled(True))
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.jsonbutton.setEnabled(False)
        self.thread.finished.connect(lambda:self.jsonbutton.setEnabled(True))

    def delete_clicked(self):
        self.save_input_values()       
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_table)
        self.thread.started.connect(self.worker.delete)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.listButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.listButton.setEnabled(True))
        self.createButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.createButton.setEnabled(True))
        self.deleteButton.setEnabled(False)
        self.thread.finished.connect(lambda:self.deleteButton.setEnabled(True))
        self.jsonbutton.setEnabled(False)
        self.thread.finished.connect(lambda:self.jsonbutton.setEnabled(True))

app = QApplication(sys.argv)
window = CloudflareDNS()
window.show()
sys.exit(app.exec())