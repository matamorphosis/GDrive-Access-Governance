# Google Drive Access Governance
A simple snitch tool which alerts any Google Drive user who has access to their files who may pose a security risk.  
**Web Application Appliance Now Available**
- GUI to interact with the script
- Revoke functionality for the web application.

## Use Cases
For small businesses using Google Suite, Google provides built in access controls for all users within that company's Google Suite; however, what if someone in the business shares files within Google Drive with someone outside the organisation? This tool provides a simple and effective way of returning any files that can be accessed by potentially untrusted persons.

Additionally this tool is recommended for promoting personal security too by allowing individuals to govern who they give access to.

The application itself allows anyone to use it, but you will have to authenticate to google to be able to run your tasks.

## Installation
1. Ensure you have python3 and python3-pip packages installed.
2. Clone this repository and navigating to the directory:
```console
user@linux:~$ git clone https://github.com/matamorphosis/GDrive-Access-Governance && cd GDrive-Access-Governance/installation
```
3. Install python requirements using the requirements.txt file in the directory:
```console
user@linux:~/Path/to/GDrive-Access-Governance/installation/$ pip3 install -r requirements.txt
```
4. You will need a `credentials.json` file. To obtain this file, log into your Google Account and navigate to the [Python Google Drive API Page here](https://developers.google.com/drive/api/v3/quickstart/python), then click the blue button called "Enable the Drive API". A pop-up box should come up and there will be another blue button called "DOWNLOAD CLIENT CONFIGURATION". Click this button to download your credentials.json file and then copy it to the following directories in your GDrive-Access-Governance directory.  
```
~/Path/to/GDrive-Access-Governance/app/config
~/Path/to/GDrive-Access-Governance/bin/config
~/Path/to/GDrive-Access-Governance/scripts
```
5. If not done already, ensure you have the Google Drive API enabled by navigating to the settings [here](https://console.developers.google.com/apis/api/drive.googleapis.com/overview).