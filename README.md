[![Github Sponsorship](/installation/images/github_sponsor_btn.svg)](https://github.com/sponsors/matamorphosis)

# Google Drive Access Governance
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  
A simple snitch tool which alerts any Google Drive user who has access to their files who may pose a security risk.
**Version 1.1**  
- Improved GUI
- Converted to Dark Theme
- Clickable Graphs

## Use Cases
For small businesses using Google Suite, Google provides built in access controls for all users within that company's Google Suite; however, what if someone in the business shares files within Google Drive with someone outside the organisation? This tool provides a simple and effective way of returning any files that can be accessed by potentially untrusted persons.

Additionally this tool is recommended for promoting personal security too by allowing individuals to govern who they give access to.

## Installation  
Please refer to the installation guide, in the installation folder.

## Web Application Usage

### Dashboard
The dashboard shows the number of open findings and certified findings as well as the number of email tasks and domain tasks. These are displayed in two separate Pie-Charts accordingly. The difference between open findings and certified findings is explained in the Results section below.
![Dashboard](/installation/images/Dashboard.png)

### Domain Tasks and Email Tasks
Domain Tasks and Email Tasks are almost identical, where the only difference is a domain task searches for email addresses that fall under a domain name, whereas an email task searches for specifical email addresses.  
  
In both scenarios you can create, delete, and execute tasks. With the option of narrowing your search down to specific directories within your target Google Drive. Additionally, the option to either certify results or revoke results automatically is available, but should be only used when the user is 100% certain that is the action they want to take. Based on the parameters the tool will find any users that have access to files in your Google Drive that meet the conditions. Auto-Certify will move results immediately into the Certified Results database, which will protect the users against revocation, and being added to the Open Results database if re-discovered. Auto-Revoke will revoke any rights assigned to users who are discovered for both new results and open results.

**Creating a Domain Task**
![Domain_Task_1](/installation/images/Domain_Task_1.png)
![Domain_Task_2](/installation/images/Domain_Task_2.png)

**Creating an Email Task**
![Email_Task_1](/installation/images/Email_Task_1.png)

**Creating an Email Task within a Specified Directory with Auto-Revoke Enabled**
![Email_Task_3](/installation/images/Email_Task_3.png)

**Creating an Email Task within a Specified Directory**
![Email_Task_2](/installation/images/Email_Task_2.png)
![Email_Task_4](/installation/images/Email_Task_4.png)

### Results
There are two kinds of results, open and certified. Initially all discovered results will be open (Except for when either Auto-Certify or Auto-Revoke are turned on), at which point you can choose to either certify or revoke each result manually. Each result represents access a user has to a file. Certifying access moves them into a seperate table in the database, these results can be viewed on the Certified Results page. On the other hand, revoking access removes that email addresses rights to access and edit the file and deletes them from the open results database.

**Open Results**
![Open_Results_1](/installation/images/Open_Results_1.png)
![Open_Results_2](/installation/images/Open_Results_2.png)

**Certified Results**
![Certified_Result](/installation/images/Certified_Result.png)

## Script Usage
There are four options for running this tool:  
1. Permitted Email Addresses - a text file containing email addresses that are safe. (Will report any files that can be accessed by email addresses that are not in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -pe allowed_emails.txt
```
2. Non-Permitted Email Addresses - a text file containing email addresses that are safe. (Will report any files that can be accessed by email addresses that are in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -ne risky_emails.txt
```
3. Permitted Domains - a text file containing domains that are safe. (Will report any files that can be accessed by email addresses that do not belong to the domain names in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -pe allowed_domains.txt
```
4. Non-Permitted Domains - a text file containing domains that are safe. (Will report any files that can be accessed by email addresses that belong to the domain names in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -ne risky_domains.txt
```
5. Excluded Directories - a text file containing directories, or parents in the language of the GSuite API, that the search should omit from searching. 
```
user@linux:~$ python3 Google_Drive_Governance.py -pe allowed_domains.txt -ed directories_to_exclude.txt
```
6. Included Directories - a text file containing directories, or parents in the language of the GSuite API, that the search should restrict its searching to. 
```
user@linux:~$ python3 Google_Drive_Governance.py -pe allowed_domains.txt -id directories_to_include.txt
```

Lastly, there is one additional argument -ps or --pagesize. This argument controls the pagination of Google Drive. Each API call can only return a maximum of 1000 results. To thread more lightly you can request 100 items per page. The tool will still search the entire Google Drive, just in smaller chunks. If you don't specify this option it will request 1000 items per page.

Below there is an example of the output that can be expected. The names and email addresses have been excluded for privacy purposes.

![Results](/installation/images/Example_Terminal_Output.png)

# List of Current Monthly Sponsors
[Endure Secure Pty Ltd](https://endsec.com.au/)
<p align="left">
  <img width="231" height="72" src="https://github.com/matamorphosis/Scrummage/blob/master/installation/images_dark_theme/Sponsor_Endure_Secure.png">
</p>

## Become a Sponsor Now!
[![Github Sponsorship](/installation/images/github_sponsor_btn.svg)](https://github.com/sponsors/matamorphosis)