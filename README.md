# ![icons8-orange-48](https://user-images.githubusercontent.com/52942515/227339564-45d03a94-d3e1-44ba-bc60-229d039cf4ee.png) CloudflareDNS
[راهنمای‌ فارسی](https://github.com/ImanMontajabi/CloudflareDNS/discussions/3)
===============
CloudflareDNS is a Python-based graphical application that allows users to easily manage and modify DNS records on the popular cloud-hosting platform, Cloudflare. Using this application, users can quickly create, list, and delete DNS records associated with their domains on Cloudflare.

The application is built using the Python programming language and the Qt GUI toolkit. The CloudflareDNS application uses Cloudflare's API to perform DNS record management operations, like creating, listing, and deleting DNS records.
# Table of Contents
- Installation
- Usage
- License
# Installation
To use CloudflareDNS, Python 3 [installed](https://www.python.org/downloads/) must have on your system. You will need to install the following packages as dependencies:
`requests` and `PyQt6`
```
pip install requests
```
and:
```
pip install PyQt6
```
for create .exe file from this code:
```
pip install auto-py-to-exe
```
or easy way:
```
pip install -r requirements.txt
```
Then, clone the repository using git:
```
git clone https://github.com/ImanMontajabi/CloudflareDNS.git
```
# Usage
To start the application, navigate to the cloned repository's directory on your machine and run the `CloudflareDNS.py` python file:
```
python CloudflareDNS.py
```
This will launch the main window of the application, which prompts users to enter their email, API token, domain name, zone ID, and DNS record name. Once this information is entered, users can perform actions like List, Create, and Delete DNS records through the respective buttons.
- Easy-to-use GUI for managing Cloudflare DNS records
- Supports the ability to list, create, and delete DNS records
- Can read JSON formatted file and create records accordingly
- Concurrency through QThread implementation to allow for asynchronous Cloudflare API requests
# License
This project is distributed under the [MIT licence](https://github.com/ImanMontajabi/CloudflareDNS/blob/main/LICENSE)
