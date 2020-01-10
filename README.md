# Google Drive Access Governance
A simple snitch tool which alerts any Google Drive user who has access to their files who may pose a security risk.

## Use Cases
For small businesses using Google Suite, Google provides built in access controls for all users within that company's Google Suite; however, what if someone in the business shares files within Google Drive with someone outside the organisation? This tool provides a simple and effective way of returning any files that can be accessed by potentially untrusted persons.

Additionally this tool is recommended for promoting personal security too by allowing individuals to govern who they give access to.

## Usage
There are four options for running this tool:  
1. Permitted Email Addresses - a text file containing email addresses that are safe. (Will report any files that can be accessed by email addresses that are not in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -pe emails.txt
```
2. Non-Permitted Email Addresses - a text file containing email addresses that are safe. (Will report any files that can be accessed by email addresses that are in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -ne risky_emails.txt
```
3. Permitted Domains - a text file containing domains that are safe. (Will report any files that can be accessed by email addresses that do not belong to the domain names in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -pe domains.txt
```
4. Non-Permitted Domains - a text file containing domains that are safe. (Will report any files that can be accessed by email addresses that belong to the domain names in the file.)
```
user@linux:~$ python3 Google_Drive_Governance.py -ne risky_domains.txt
```

Lastly, there is one additional argument -ps or --pagesize. This argument controls the pagination of Google Drive. Each API call can only return a maximum of 1000 results. To thread more lightly you can request 100 items per page. The tool will still search the entire Google Drive, just in smaller chunks. If you don't specify this option it will request 1000 items per page.

Below there is an example of the output that can be expected. The names and email addresses have been excluded for privacy purposes.

![Results](/Example_Output.png)
