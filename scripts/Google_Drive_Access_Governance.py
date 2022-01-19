#!/usr/bin/python3
# Google Drive External User Governance Tool Version 2.2.
import pickle, os.path, sys, argparse, time, colorama
from multiprocessing import Pool
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
Scope = ['https://www.googleapis.com/auth/drive.metadata.readonly']
Exclude_Directories = ""
Include_Directories = ""
colorama.init()
start = time.time()

def Write_Out(Output_File_Name):
    f = open(Output_File_Name,'w')
    sys.stdout = f

def Print_Red(To_Print):
    Start = "\033[1;31m"
    End = "\033[0;0m"
    print(f"{Start}{To_Print}{End}")

def Read_File(File_Name):

    try:
        with open(File_Name) as File:
            File_Contents = File.readlines()

        File_Contents_List = [x.strip() for x in File_Contents]
        print(f"[+] Contents of Provided File:")
        print(f", ".join(File_Contents_List))

        return File_Contents_List

    except Exception as e:
        sys.exit(f'[-] {str(e)}')

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

            self.Service = build('drive', 'v3', credentials=Credentials, cache_discovery=False)

        except Exception as e:
            sys.exit(f'[-] {str(e)}')

    def Iteration(self, Item):

        try:
            File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
            Permission_Details = File_Permissions.get('permissions', [])
            Current_File_ID = ""
            Current_Prints = []

            if "permitted_domains" in self.kwargs:

                for Permission_Detail in Permission_Details:

                    if 'emailAddress' in Permission_Detail:

                        if Permission_Detail['emailAddress'] and any(substring not in Permission_Detail['emailAddress'] for substring in self.kwargs['permitted_domains']) and Current_File_ID != Item['id']:
                            Print_Red("\n".join(Current_Prints))
                            Current_File_ID = Item['id']
                            Current_Prints = []
                            Current_Prints.append(f"File ID: {Item['id']} - File Name: {Item['name']}\n - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

                        elif Permission_Detail['emailAddress'] and any(substring not in Permission_Detail['emailAddress'] for substring in self.kwargs['permitted_domains']) and Current_File_ID == Item['id']:
                            Current_Prints.append(f" - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

            elif "non_permitted_domains" in self.kwargs:

                for Permission_Detail in Permission_Details:

                    if 'emailAddress' in Permission_Detail:

                        if Permission_Detail['emailAddress'] and any(substring in Permission_Detail['emailAddress'] for substring in self.kwargs['non_permitted_domains']) and Current_File_ID != Item['id']:
                            Print_Red("\n".join(Current_Prints))
                            Current_File_ID = Item['id']
                            Current_Prints = []
                            Current_Prints.append(f"File ID: {Item['id']} - File Name: {Item['name']}\n - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

                        elif Permission_Detail['emailAddress'] and any(substring in Permission_Detail['emailAddress'] for substring in self.kwargs['non_permitted_domains']) and Current_File_ID == Item['id']:
                            Current_Prints.append(f" - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

            elif "permitted_emails" in self.kwargs:

                for Permission_Detail in Permission_Details:

                    if 'emailAddress' in Permission_Detail:

                        if Permission_Detail['emailAddress'] and Permission_Detail['emailAddress'] not in self.kwargs['permitted_emails'] and Current_File_ID != Item['id']:
                            Print_Red("\n".join(Current_Prints))
                            Current_File_ID = Item['id']
                            Current_Prints = []
                            Current_Prints.append(f"File ID: {Item['id']} - File Name: {Item['name']}\n - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

                        elif Permission_Detail['emailAddress'] and Permission_Detail['emailAddress'] not in self.kwargs['permitted_emails'] and Current_File_ID == Item['id']:
                            Current_Prints.append(f" - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

            elif "non_permitted_emails" in self.kwargs:

                for Permission_Detail in Permission_Details:

                    if 'emailAddress' in Permission_Detail:

                        if Permission_Detail['emailAddress'] and Permission_Detail['emailAddress'] in self.kwargs['non_permitted_emails'] and Current_File_ID != Item['id']:
                            Print_Red("\n".join(Current_Prints))
                            Current_File_ID = Item['id']
                            Current_Prints = []
                            Current_Prints.append(f"File ID: {Item['id']} - File Name: {Item['name']}\n - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

                        elif Permission_Detail['emailAddress'] and Permission_Detail['emailAddress'] in self.kwargs['non_permitted_emails'] and Current_File_ID == Item['id']:
                            Current_Prints.append(f" - Accessible by {Permission_Detail['displayName']} - Email: {Permission_Detail['emailAddress']}")

            else:
                sys.exit('[-] No valid keyword arguments supplied.')

            if Current_Prints != []:
                Print_Red("\n".join(Current_Prints))
                Current_Prints = []

        except:
            print("[i] Non fatal exception.")

    def Governance_Check(self, Page_Size, **kwargs):
        self.kwargs = kwargs

        if Exclude_Directories:
            Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
            Page_Start = 0
            Page = 1
                
            while 'nextPageToken' in Response:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print(f'[i] No files found.')

                else:

                    for Parent in Result_Items:

                        if 'id' in Parent and 'name' in Parent:

                            if Parent['name'] not in Exclude_Directories:
                                print(f"[+] Searching under parent {Parent['name']}")
                                Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
                                Cur_Page_Start = 0
                                Cur_Page = 1

                                while 'nextPageToken' in Current_Response:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f"[+] Pages broken down into {str(Page_Size)} results at a time. Searching for potential access violations on page {str(Cur_Page)}. Searching through results {str(Cur_Page_Start + 1)} to {str(Cur_Page_Start + Page_Size)}")
                                        print(f"{Parent['name']} : {Current_Result_Items}.")

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

                                    Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, pageToken=Current_Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()
                                    Cur_Page += 1
                                    Cur_Page_Start += Page_Size

                                else:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f'[+] Searching for Potential Access Violations.')

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

                Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)", ).execute()
                Page += 1
                Page_Start += Page_Size

            else:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print(f'[i] No files found.')

                else:

                    for Parent in Result_Items:

                        if 'id' in Parent and 'name' in Parent:

                            if Parent['name'] not in Exclude_Directories:
                                print(f"[+] Searching under parent {Parent['name']}")
                                Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
                                Cur_Page_Start = 0
                                Cur_Page = 1
                                    
                                while 'nextPageToken' in Current_Response:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f"[+] Pages broken down into {str(Page_Size)} results at a time. Searching for potential access violations on page {str(Cur_Page)}. Searching through results {str(Cur_Page_Start + 1)} to {str(Cur_Page_Start + Page_Size)}")
                                        print(f"{Parent['name']} : {Current_Result_Items}.")

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

                                    Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, pageToken=Current_Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()
                                    Cur_Page += 1
                                    Cur_Page_Start += Page_Size

                                else:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f'[+] Searching for Potential Access Violations.')

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

        elif Include_Directories:
            Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
            Page_Start = 0
            Page = 1

            while 'nextPageToken' in Response:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print(f'[i] No files found.')

                else:

                    for Parent in Result_Items:

                        if 'id' in Parent and 'name' in Parent:

                            if Parent['name'] in Include_Directories:
                                print(f"[+] Searching under parent {Parent['name']}")
                                Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
                                Cur_Page_Start = 0
                                Cur_Page = 1

                                while 'nextPageToken' in Current_Response:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f"[+] Pages broken down into {str(Page_Size)} results at a time. Searching for potential access violations on page {str(Cur_Page)}. Searching through results {str(Cur_Page_Start + 1)} to {str(Cur_Page_Start + Page_Size)}")
                                        print(f"{Parent['name']} : {Current_Result_Items}.")

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

                                    Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, pageToken=Current_Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()
                                    Cur_Page += 1
                                    Cur_Page_Start += Page_Size

                                else:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f'[+] Searching for Potential Access Violations.')

                                        with Pool(cpu_count()) as p:
                                            p.map(self.Iteration, Current_Result_Items)

                Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)", ).execute()
                Page += 1
                Page_Start += Page_Size

            else:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print(f'[i] No files found.')

                else:

                    for Parent in Result_Items:

                        if 'id' in Parent and 'name' in Parent:

                            if Parent['name'] in Include_Directories:
                                print(f"[+] Searching under parent {Parent['name']}")
                                Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
                                Cur_Page_Start = 0
                                Cur_Page = 1
                                    
                                while 'nextPageToken' in Current_Response:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f"[+] Pages broken down into {str(Page_Size)} results at a time. Searching for potential access violations on page {str(Cur_Page)}. Searching through results {str(Cur_Page_Start + 1)} to {str(Cur_Page_Start + Page_Size)}")
                                        print(f"{Parent['name']} : {Current_Result_Items}.")

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

                                    Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, pageToken=Current_Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()
                                    Cur_Page += 1
                                    Cur_Page_Start += Page_Size

                                else:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f'[+] Searching for Potential Access Violations.')

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Result_Items)

        else:
            Response = self.Service.files().list(pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
            Page_Start = 0
            Page = 1
                
            while 'nextPageToken' in Response:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print(f'[i] No files found.')

                else:
                    print(f"[+] Pages broken down into {str(Page_Size)} results at a time. Searching for potential access violations on page {str(Page)}. Searching through results {str(Page_Start + 1)} to {str(Page_Start + Page_Size)}")

                    with Pool(processes=2) as p:
                        p.map(self.Iteration, Result_Items)

                Response = self.Service.files().list(pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)",).execute()
                Page += 1
                Page_Start += Page_Size

            else:
                Result_Items = Response.get('files', [])

                if not Result_Items:
                    print(f'[i] No files found.')

                else:
                    print(f'[+] Searching for Potential Access Violations.')

                    with Pool(processes=2) as p:
                        p.map(self.Iteration, Result_Items)

if __name__ == '__main__':
    Page_Size_Int = 1000

    try:
        Parser = argparse.ArgumentParser(description='Tool that provdes a list of files that potentially untrusted persons have access to.')
        Parser.add_argument('-pd', '--permitteddomain', help='This option is used to specify a file with permitted domains to check for users that do not belong to those domains. To run: ./Google_Drive_Governance -pd domains.txt')
        Parser.add_argument('-pe', '--permittedemail', help='This option is used to specify a file with permitted email addresses to check for users whose emails are not in that list. To run: ./Google_Drive_Governance -pe emails.txt')
        Parser.add_argument('-nd', '--nonpermitteddomain', help='This option is used to specify a file with non-permitted domains to check for users that do belong to those domains. To run: ./Google_Drive_Governance -nd domains.txt')
        Parser.add_argument('-ne', '--nonpermittedemail', help='This option is used to specify a file with non-permitted email addresses to check for users whose emails are in that list. To run: ./Google_Drive_Governance -ne emails.txt./Google_Drive_Governance -ne emails.txt -ps 1000')
        Parser.add_argument('-id', '--includingdirectories', help='This optional, additional parameter can be used to specify a file with directories you want to search within. This can be useful when searching a large Google Drive, or when you know the breaching of a certain directory\'s files are of higher risk than other directories. To run: ./Google_Drive_Governance -pd domains.txt -id directories.txt')
        Parser.add_argument('-ed', '--excludingdirectories', help='This optional, additional parameter can be used to specify a file with directories you want to skip searching. To run: ./Google_Drive_Governance -pd domains.txt -ed directories.txt')
        Parser.add_argument('-ps', '--pagesize', type=int, help='This optional argument specifies the how many results are returned in each request. The largest number available is 1000 and this is also the default length. ./Google_Drive_Governance -ne emails.txt -ps 1000')
        Parser.add_argument('-o', '--outputfile', help='Name of file you want to save terminal output to. ./Google_Drive_Governance -ne emails.txt -o file.txt')
        Arguments = Parser.parse_args()

        if Arguments.includingdirectories and Arguments.excludingdirectories:
            sys.exit("[-] Please specify either --includingdirectories or --excludingdirectories. Not both.")

        elif Arguments.includingdirectories and not Arguments.excludingdirectories:
            Include_Directories = Read_File(str(Arguments.includingdirectories))

        elif Arguments.excludingdirectories and not Arguments.includingdirectories:
            Exclude_Directories = Read_File(str(Arguments.excludingdirectories))

        if Arguments.pagesize:

            try:

                if int(Arguments.pagesize) > 0 and int(Arguments.pagesize) <= 1000:
                    Page_Size_Int = int(Arguments.pagesize)

                elif int(Arguments.pagesize) > 1000:
                    sys.exit('[-] Invalid page size provided. The value must be less than 1000.')

                elif int(Arguments.pagesize) < 0:
                    sys.exit('[-] Invalid page size provided. The value must be greater than 0.')

            except Exception as e:
                sys.exit(f'[-] {str(e)}')

        if Arguments.outputfile:
            Write_Out(Arguments.outputfile)

        Google_Drive = Main('credentials.json')

        if Arguments.permitteddomain:
            File = Read_File(str(Arguments.permitteddomain))
            Google_Drive.Governance_Check(Page_Size_Int, permitted_domains=File)

        elif Arguments.permittedemail:
            File = Read_File(str(Arguments.permittedemail))
            Google_Drive.Governance_Check(Page_Size_Int, permitted_emails=File)

        elif Arguments.nonpermitteddomain:
            File = Read_File(str(Arguments.nonpermitteddomain))
            Google_Drive.Governance_Check(Page_Size_Int, non_permitted_domains=File)

        elif Arguments.nonpermittedemail:
            File = Read_File(str(Arguments.nonpermittedemail))
            Google_Drive.Governance_Check(Page_Size_Int, non_permitted_emails=File)

        else:
            sys.exit("[-] No argument supplied.")

        print("[+] Finished. Execution time = {0:.5f}.".format(time.time() - start))

    except Exception as e:
        sys.exit(f'[-] {str(e)}')