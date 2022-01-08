#!/usr/bin/python3
# Google Drive External User Governance Tool Version 2.2.
import pickle, os.path, sys, sqlite3, datetime, os
from multiprocessing import Pool
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
Scope = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']

def Database_Output(DB_Filename, Output_Data, **kwargs):
    File_ID = Output_Data["File_ID"]
    File_Name = Output_Data["File_Name"]
    Updated = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    DB_Conn = sqlite3.connect(DB_Filename)
    DB_Cur = DB_Conn.cursor()
    DB_Cur.execute(f"""SELECT emails FROM open_results WHERE id = '{File_ID}' and file_name = '{File_Name}';""")
    Open_Results = DB_Cur.fetchone()
    DB_Cur.execute(f"""SELECT emails FROM certified_results WHERE id = '{File_ID}' and file_name = '{File_Name}';""")
    Cert_Results = DB_Cur.fetchone()

    if not kwargs.get("Certify"):

        if not Open_Results and not Cert_Results:
            Emails = ", ".join(Output_Data["Emails"])
            DB_Conn.executescript(f"""INSERT INTO open_results (id, file_name, trashed, emails, created_at, updated_at) values ('{Output_Data["File_ID"]}', '{Output_Data["File_Name"]}', '{Output_Data["Trashed"]}', '{Emails}', '{Updated}', '{Updated}');""")

        elif not Open_Results and Cert_Results:
            Emails_to_Output = []
            Cert_Emails = Cert_Results[0].split(", ")

            for Email in Output_Data["Emails"]:

                if Email not in Cert_Emails:
                    Emails_to_Output.append(Email)     

            if Emails_to_Output != []:
                Emails_to_Output = ", ".join(Emails_to_Output)
                DB_Conn.executescript(f"""INSERT INTO open_results (id, file_name, trashed, emails, created_at, updated_at) values ('{Output_Data["File_ID"]}', '{Output_Data["File_Name"]}', '{Output_Data["Trashed"]}', '{Emails_to_Output}', '{Updated}', '{Updated});""")

        elif Open_Results and not Cert_Results:
            Original_Emails = Open_Results[0].split(", ")
            Open_Emails = Original_Emails

            for Email in Output_Data["Emails"]:

                if Email not in Open_Emails:
                    Open_Emails.append(Email)

            if Open_Emails != Original_Emails:
                Open_Emails = ", ".join(Open_Emails)
                DB_Conn.executescript(f"""UPDATE open_results SET emails = "{Open_Emails}", updated_at = "{Updated}" WHERE id = "{File_ID}";""")

        elif Open_Results and Cert_Results:
            Original_Open_Emails = Open_Results[0].split(", ")
            Open_Emails = Original_Open_Emails
            Cert_Emails = Cert_Results[0].split(", ")

            for Email in Output_Data["Emails"]:

                if Email not in Open_Emails and Email not in Cert_Emails:
                    Open_Emails.append(Email)

            if Open_Emails != Original_Open_Emails:
                Open_Emails = ", ".join(Open_Emails)
                DB_Conn.executescript(f"""UPDATE open_results SET emails = "{Open_Emails}", updated_at = "{Updated}" WHERE id = "{File_ID}";""")

        else:
            DB_Conn.close()
            return

    else:
        Updated = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        if Open_Results and Cert_Results:
            Original_Cert_Emails = Cert_Results[0].split(", ")
            Open_Emails = Open_Results[0].split(", ")
            Cert_Emails = Original_Cert_Emails

            for Email in Output_Data["Emails"]:

                if Email in Open_Emails:
                    Open_Emails.remove(Email)

                if Email not in Cert_Emails:
                    Cert_Emails.append(Email)

            if Open_Emails != []:
                DB_Conn.executescript(f"""UPDATE open_results SET emails = "{Open_Emails}", updated_at = "{Updated}" WHERE id = "{File_ID}";""")

            elif Open_Emails == []:
                DB_Conn.executescript(f"""DELETE from open_results where id = "{File_ID}";""")

            if Cert_Emails != Original_Cert_Emails:
                DB_Conn.executescript(f"""UPDATE certified_results SET emails = "{Cert_Emails}", updated_at = "{Updated}" WHERE id = "{File_ID}";""")

        elif Open_Results and not Cert_Results:
            Open_Emails = Open_Results[0].split(", ")

            for Email in Output_Data["Emails"]:

                if Email in Open_Emails:
                    Open_Emails.remove(Email)

            if Open_Emails != []:
                DB_Conn.executescript(f"""UPDATE open_results SET emails = "{Open_Emails}", updated_at = "{Updated}" WHERE id = "{File_ID}";""")

            elif Open_Emails == []:
                DB_Conn.executescript(f"""DELETE from open_results where id = "{File_ID}";""")

            Emails_to_Output = ", ".join(Output_Data["Emails"])
            DB_Conn.executescript(f"""INSERT INTO certified_results (id, file_name, trashed, emails, created_at, updated_at) values ('{Output_Data["File_ID"]}', '{Output_Data["File_Name"]}', '{Output_Data["Trashed"]}', '{Emails_to_Output}', '{Updated}', '{Updated}');""")

        elif not Open_Results and not Cert_Results:
            Emails_to_Output = ", ".join(Output_Data["Emails"])
            DB_Conn.executescript(f"""INSERT INTO certified_results (id, file_name, trashed, emails, created_at, updated_at) values ('{Output_Data["File_ID"]}', '{Output_Data["File_Name"]}', '{Output_Data["Trashed"]}', '{Emails_to_Output}', '{Updated}', '{Updated}');""")

        else:
            DB_Conn.close()
            return

    DB_Conn.commit()
    DB_Conn.close()

class Main:

    def __init__(self, DB_Filename):

        try:
            Credentials = None

            if os.path.exists('token.pickle'):

                with open('token.pickle', 'rb') as token:
                    Credentials = pickle.load(token)

            if not Credentials or not Credentials.valid:

                if Credentials and Credentials.expired and Credentials.refresh_token:
                    Credentials.refresh(Request())

                else:
                    File_Dir = os.path.dirname(os.path.realpath('__file__'))
                    Configuration_File = os.path.join(File_Dir, 'config/credentials.json')
                    flow = InstalledAppFlow.from_client_secrets_file(Configuration_File, Scope)
                    Credentials = flow.run_local_server(port=0)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(Credentials, token)

            self.Service = build('drive', 'v3', credentials=Credentials, cache_discovery=False)
            self.DB_File = DB_Filename

        except Exception as e:
            sys.exit(f'[-] {str(e)}.')

    def Iteration(self, Item):

        try:

            if Item.get("mimeType") and Item.get("mimeType") != 'application/vnd.google-apps.folder' and Item.get("trashed"):
                File_Permissions = self.Service.permissions().list(fileId=Item["id"], fields="*").execute()
                Permission_Details = File_Permissions.get('permissions', [])
                self.Current_File_ID = ""
                self.Current_Prints = {}

                def Outputter(self, Permission_Detail, Item, Match):

                    try:
                        
                        if not Match:
                            self.Current_File_ID = Item['id']
                            self.Current_Prints = {"File_ID": str(Item['id']), "File_Name": str(Item['name']), "Emails": [str(Permission_Detail['emailAddress'])]}

                            if "trashed" in Item:
                                self.Current_Prints["Trashed"] = Item["trashed"]

                            else:
                                self.Current_Prints["Trashed"] = False

                        else:
                            self.Current_Prints["Emails"].append(str(Permission_Detail['emailAddress']))
                            
                        if self.kwargs["Auto Function"] == "Revoke":
                            self.Auto_Function(Item['id'], Permission_Detail['id'], Permission_Detail['emailAddress'])
                                
                    except Exception as e:
                        sys.exit(f'[-] {str(e)}.')

                for Permission_Detail in Permission_Details:

                    if 'emailAddress' in Permission_Detail:

                        if "permitted_domains" in self.kwargs:

                            if Permission_Detail['emailAddress'] and any(substring not in Permission_Detail['emailAddress'] for substring in self.kwargs['permitted_domains']):
                                Outputter(self, Permission_Detail, Item, self.Current_File_ID == Item['id'])

                        elif "non_permitted_domains" in self.kwargs:

                            if Permission_Detail['emailAddress'] and any(substring in Permission_Detail['emailAddress'] for substring in self.kwargs['non_permitted_domains']):
                                Outputter(self, Permission_Detail, Item, self.Current_File_ID == Item['id'])

                        elif "permitted_emails" in self.kwargs:

                            if Permission_Detail['emailAddress'] and Permission_Detail['emailAddress'] not in self.kwargs['permitted_emails']:
                                Outputter(self, Permission_Detail, Item, self.Current_File_ID == Item['id'])

                        elif "non_permitted_emails" in self.kwargs:

                            if Permission_Detail['emailAddress'] and Permission_Detail['emailAddress'] in self.kwargs['non_permitted_emails']:
                                Outputter(self, Permission_Detail, Item, self.Current_File_ID == Item['id'])

                        else:
                            sys.exit('[-] No valid keyword arguments supplied.')

                if self.Current_Prints != {}:

                    if self.kwargs.get("Auto Function") == "Certify":
                        Database_Output(self.DB_File, self.Current_Prints, Certify=True)

                    elif self.kwargs.get("Auto Function") == "Revoke":
                        pass

                    else:
                        Database_Output(self.DB_File, self.Current_Prints)

                    self.Current_Prints = {}

        except HttpError as err:
            pass

        except Exception as e:
            print(f"[i] {e}.")

    def Governance_Check(self, Page_Size, **kwargs):

        try:
            self.kwargs = kwargs

            if "Excluded_Directories" in kwargs:
                Exclude_Directories = kwargs["Excluded_Directories"]

                def Excluded_Parent_Search(self, Parent_Result_Items):

                    for Parent in Parent_Result_Items:

                        if 'id' in Parent and 'name' in Parent:

                            if Parent['name'] not in Exclude_Directories:
                                print(f"[+] Searching under parent {Parent['name']}")
                                Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, fields="nextPageToken, files(id, name, mimeType, trashed)",).execute()
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
                                            p.map(self.Iteration, Current_Result_Items)

                                    Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, pageToken=Current_Response['nextPageToken'], fields="nextPageToken, files(id, name, mimeType, trashed)",).execute()
                                    Cur_Page += 1
                                    Cur_Page_Start += Page_Size

                                else:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f'[+] Searching for Potential Access Violations.')

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Current_Result_Items)

                Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
                Page_Start = 0
                Page = 1
                    
                while 'nextPageToken' in Response:
                    Result_Items = Response.get('files', [])

                    if not Result_Items:
                        print(f'[i] No files found.')

                    else:
                        Excluded_Parent_Search(self, Result_Items)
                        
                    Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)", ).execute()
                    Page += 1
                    Page_Start += Page_Size

                else:
                    Result_Items = Response.get('files', [])

                    if not Result_Items:
                        print(f'[i] No files found.')

                    else:
                        Excluded_Parent_Search(self, Result_Items)

            elif "Included_Directories" in kwargs:
                Include_Directories = kwargs["Included_Directories"]

                def Included_Parent_Search(self, Parent_Result_Items):

                    for Parent in Parent_Result_Items:

                        if 'id' in Parent and 'name' in Parent:

                            if Parent['name'] in Include_Directories:
                                print(f"[+] Searching under parent {Parent['name']}")
                                Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, fields="nextPageToken, files(id, name, mimeType, trashed)",).execute()
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
                                            p.map(self.Iteration, Current_Result_Items)

                                    Current_Response = self.Service.files().list(q=f"'{Parent['id']}' in parents", pageSize=Page_Size, pageToken=Current_Response['nextPageToken'], fields="nextPageToken, files(id, name, mimeType, trashed)",).execute()
                                    Cur_Page += 1
                                    Cur_Page_Start += Page_Size

                                else:
                                    Current_Result_Items = Current_Response.get('files', [])

                                    if not Current_Result_Items:
                                        print(f'[i] No files found.')

                                    else:
                                        print(f'[+] Searching for Potential Access Violations.')

                                        with Pool(processes=2) as p:
                                            p.map(self.Iteration, Current_Result_Items)

                Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, fields="nextPageToken, files(id, name)",).execute()
                Page_Start = 0
                Page = 1

                while 'nextPageToken' in Response:
                    Result_Items = Response.get('files', [])

                    if not Result_Items:
                        print(f'[i] No files found.')

                    else:
                        Included_Parent_Search(self, Result_Items)

                    Response = self.Service.files().list(q="mimeType='application/vnd.google-apps.folder'", pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name)", ).execute()
                    Page += 1
                    Page_Start += Page_Size

                else:
                    Result_Items = Response.get('files', [])

                    if not Result_Items:
                        print(f'[i] No files found.')

                    else:
                        Included_Parent_Search(self, Result_Items)

            else:
                Response = self.Service.files().list(pageSize=Page_Size, fields="nextPageToken, files(id, name, mimeType, trashed)",).execute()
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

                    Response = self.Service.files().list(pageSize=Page_Size, pageToken=Response['nextPageToken'], fields="nextPageToken, files(id, name, mimeType)",).execute()
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

        except HttpError as err:
            pass

        except Exception as e:
            print(f"[-] {str(e)}.")

    def Auto_Function(self, File_ID, Permission_ID, Permission_Email):

        try:

            if self.kwargs["Auto Function"] == "Revoke":
                DB_Conn = sqlite3.connect(self.DB_File)
                DB_Cur = DB_Conn.cursor()
                DB_Cur.execute(f"""SELECT emails FROM open_results WHERE id = '{File_ID}';""")
                Open_Results = DB_Cur.fetchone()
                DB_Cur.execute(f"""SELECT emails FROM certified_results WHERE id = '{File_ID}';""")
                Cert_Results = DB_Cur.fetchone()
                Certified_Result = False

                if Cert_Results:
                    Cert_Emails = Cert_Results[0].split(", ")

                    if Permission_Email in Cert_Emails:
                        Certified_Result = True

                if not Certified_Result:

                    if Open_Results:
                        Open_Emails = Open_Results[0].split(", ")

                        if Permission_Email in Open_Emails:
                            Open_Emails.remove(Permission_Email)

                        if Open_Emails != []:
                            Updated = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            DB_Conn.executescript(f"""UPDATE open_results SET emails = "{Open_Emails}", updated_at = "{Updated}" WHERE id = "{File_ID}";""")

                        elif Open_Emails == []:
                            DB_Conn.executescript(f"""DELETE from open_results where id = "{File_ID}";""")

                        DB_Conn.commit()
                        DB_Conn.close()

                    if File_ID and Permission_ID:
                        self.Service.permissions().delete(fileId=File_ID, permissionId=Permission_ID).execute()

        except Exception as e:
            print(f"[-] {str(e)}.")

    def Revoke_Access(self, File_ID, Email_Address):

        try:
            Permission_ID = ""
            File_Permissions = self.Service.permissions().list(fileId=File_ID, fields="*").execute()
            Permission_Details = File_Permissions.get('permissions', [])

            for Permission_Detail in Permission_Details:

                if 'emailAddress' in Permission_Detail:

                    if Email_Address == Permission_Detail['emailAddress']:
                        Permission_ID = Permission_Detail['id']

            if Permission_ID != "":
                self.Service.permissions().delete(fileId=File_ID, permissionId=Permission_ID).execute()

            return True

        except Exception as e:
            print(f"[-] {str(e)}.")

    def Provision_Access(self, File_ID, Transfer_Ownership, Permission):

        try:
            self.Service.permissions().create(fileId=File_ID, transferOwnership=Transfer_Ownership, body=Permission).execute()
            return True

        except Exception as e:
            print(f"[-] {str(e)}.")