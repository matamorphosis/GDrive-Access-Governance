#!/usr/bin/python3
import pickle, os.path, sys, argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
Scope = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def Read_File(File_Name):

    try:
        with open(File_Name) as File:
            File_Contents = File.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        File_Contents_List = [x.strip() for x in File_Contents]
        print("[+] Contents of Provided File:")
        print(", ".join(File_Contents_List))

        return File_Contents_List

    except Exception as e:
        sys.exit('[-] ' + str(e))

class Main:

    def __init__(self, Credentials_File):

        try:
            Credentials = None

            if os.path.exists('token.pickle'):

                with open('token.pickle', 'rb') as token:
                    Credentials = pickle.load(token)

            if not Credentials or not Credentials.valid:

                if Credentials and Credentials.expired and Credentials.refresh_token:
                    Credentials.refresh(Request())

                else:
                    flow = InstalledAppFlow.from_client_secrets_file(Credentials_File, Scope)
                    Credentials = flow.run_local_server(port=0)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(Credentials, token)

            self.Service = build('drive', 'v3', credentials=Credentials)

        except Exception as e:
            sys.exit('[-] ' + str(e))

    def Governance_Check(self, Page_Size, **kwargs):
        Response = self.Service.files().list(pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()

        if 'nextPageToken' in Response:
            Page = 1
            
            while 'nextPageToken' in Response:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print('[-] No files found.')

                else:
                    print('[+] Pages broken down into ' + str(Page_Size) + ' results at a time. Searching for risky files on page ' + str(Page) + '.')

                    for Item in Result_Items:

                        try:

                            if "permitted_domains" in kwargs:
                                File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                                Permission_Details = File_Permissions.get('permissions', [])
                                
                                for Permission_Detail in Permission_Details:

                                    if any(substring not in Permission_Detail['emailAddress'] for substring in kwargs['permitted_domains']):
                                        print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                            elif "non_permitted_domains" in kwargs:
                                File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                                Permission_Details = File_Permissions.get('permissions', [])
                                
                                for Permission_Detail in Permission_Details:

                                    if any(substring in Permission_Detail['emailAddress'] for substring in kwargs['non_permitted_domains']):
                                        print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                            elif "permitted_emails" in kwargs:
                                File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                                Permission_Details = File_Permissions.get('permissions', [])
                                
                                for Permission_Detail in Permission_Details:

                                    if Permission_Detail['emailAddress'] not in kwargs['permitted_emails']:
                                        print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                            elif "non_permitted_emails" in kwargs:
                                File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                                Permission_Details = File_Permissions.get('permissions', [])
                                
                                for Permission_Detail in Permission_Details:

                                    if Permission_Detail['emailAddress'] in kwargs['non_permitted_emails']:
                                        print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                            else:
                                sys.exit('[-] No valid keyword arguments supplied.')

                        except:
                            pass

                Response = self.Service.files().list(pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()
                Page += 1

        else:
            Result_Items = Response.get('files', [])

            if not Result_Items:
                print('[-] No files found.')

            else:
                print('[+] Searching for risky files.')

                for Item in Result_Items:

                    try:

                        if "permitted_domains" in kwargs:
                            File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                            Permission_Details = File_Permissions.get('permissions', [])
                            
                            for Permission_Detail in Permission_Details:

                                if any(substring not in Permission_Detail['emailAddress'] for substring in kwargs['permitted_domains']):
                                    print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                        elif "non_permitted_domains" in kwargs:
                            File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                            Permission_Details = File_Permissions.get('permissions', [])
                            
                            for Permission_Detail in Permission_Details:

                                if any(substring in Permission_Detail['emailAddress'] for substring in kwargs['non_permitted_domains']):
                                    print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                        elif "permitted_emails" in kwargs:
                            File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                            Permission_Details = File_Permissions.get('permissions', [])
                            
                            for Permission_Detail in Permission_Details:

                                if Permission_Detail['emailAddress'] not in kwargs['permitted_emails']:
                                    print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                        elif "non_permitted_emails" in kwargs:
                            File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                            Permission_Details = File_Permissions.get('permissions', [])
                            
                            for Permission_Detail in Permission_Details:

                                if Permission_Detail['emailAddress'] in kwargs['non_permitted_emails']:
                                    print("\033[41mFile ID: " + Item['id'] + " - Name: " + Item['name'] + " - Accessible by " + Permission_Detail['displayName'] + " - " + Permission_Detail['emailAddress'] + "\033[40m")

                        else:
                            sys.exit('[-] No valid keyword arguments supplied.')

                    except:
                        pass

            Response = self.Service.files().list(pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()

if __name__ == '__main__':
    Page_Size_Int = 1000

    try:
        Parser = argparse.ArgumentParser(description='Tool that provdes a list of files that potentially untrusted persons have access to..')
        Parser.add_argument('-pd', '--permitteddomain', help='This option is used to specify a file with permitted domains to check for users that do not belong to those domains. To run. ./Google_Drive_Governance -pd domains.txt')
        Parser.add_argument('-pe', '--permittedemail', help='This option is used to specify a file with permitted email addresses to check for users whose emails are not in that list. To run. ./Google_Drive_Governance -pe emails.txt')
        Parser.add_argument('-nd', '--nonpermitteddomain', help='This option is used to specify a file with non-permitted domains to check for users that do belong to those domains. To run. ./Google_Drive_Governance -nd domains.txt')
        Parser.add_argument('-ne', '--nonpermittedemail', help='This option is used to specify a file with non-permitted email addresses to check for users whose emails are in that list. To run. ./Google_Drive_Governance -ne emails.txt./Google_Drive_Governance -ne emails.txt -ps 1000')
        Parser.add_argument('-ps', '--pagesize', help='This optional argument specifies the how many results are returned in each request. The largest number available is 1000 and this is also the default length. ./Google_Drive_Governance -ne emails.txt -ps 1000')
        Arguments = Parser.parse_args()

        if Arguments.pagesize:

            try:

                if int(Arguments.pagesize) > 0 and int(Arguments.pagesize) <= 1000:
                    Page_Size_Int = int(Arguments.pagesize)

                else:
                    sys.exit('[-] Invalid page size provided. Either > 1000 or < 0.')

            except Exception as e:
                sys.exit('[-] ' + str(e))

        if Arguments.permitteddomain:
            File = Read_File(str(Arguments.permitteddomain))
            Google_Drive = Main('credentials.json')
            Google_Drive.Governance_Check(Page_Size_Int, permitted_domains=File)
            sys.exit('[+] Finished.')

        elif Arguments.permittedemail:
            File = Read_File(str(Arguments.permittedemail))
            Google_Drive = Main('credentials.json')
            Google_Drive.Governance_Check(Page_Size_Int, permitted_emails=File)
            sys.exit('[+] Finished.')

        elif Arguments.nonpermitteddomain:
            File = Read_File(str(Arguments.nonpermitteddomain))
            Google_Drive = Main('credentials.json')
            Google_Drive.Governance_Check(Page_Size_Int, non_permitted_domains=File)
            sys.exit('[+] Finished.')

        elif Arguments.nonpermittedemail:
            File = Read_File(str(Arguments.nonpermittedemail))
            Google_Drive = Main('credentials.json')
            Google_Drive.Governance_Check(Page_Size_Int, non_permitted_emails=File)
            sys.exit('[+] Finished.')

        else:
            sys.exit("[-] No argument supplied.")

    except Exception as e:
        sys.exit('[-] ' + str(e))