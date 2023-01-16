from __future__ import print_function

import os.path, requests, time, json, sys, pathlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable TLS warnings - to allow for self-signed certificates
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# If modifying these scopes, delete the file token.json.
Scopes = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """

    try:

        try: 
            GDAG_Working_Directory = pathlib.Path(__file__).parent.absolute()

            if str(GDAG_Working_Directory) != str(os.getcwd()):
                print(f"[i] Google Drive AG Appliance has been called from outside of its directory, changing the working directory to {str(GDAG_Working_Directory)}.")
                os.chdir(GDAG_Working_Directory)

                if str(GDAG_Working_Directory) != str(os.getcwd()):
                    print("[-] Error setting the working directory.")
                    sys.exit(1)

        except:
            print(f"[!] Error setting the working directory.")
            sys.exit(1)

        # TO_DO MAKE CODE POLL FOR CREDENTIALS, INTEGRATE WITH NEW GDAG ENDPOINTS
        creds = None
        Cred_File = os.path.join(GDAG_Working_Directory, 'config/credentials.json')
        Token_File = os.path.join(GDAG_Working_Directory, 'config/token.json')

        if not os.path.exists(Cred_File):
            # Delay start to ensure GDAG Appliance has time to start
            time.sleep(5)
            print("[i] Please upload your credentials.json file to https://localhost. You will not be able to run Google Drive API-driven tasks until then.")
            resp = requests.get("https://10.0.0.6/api/auth/download", verify=False)

            while resp.status_code != 200:
                time.sleep(10)
                resp = requests.get("https://10.0.0.6/api/auth/download", verify=False)

            else:
                with open(Cred_File, 'w') as cred_file:
                    cred_file.write(json.dumps(resp.json(), indent=True, sort_keys=True))

        if os.path.exists(Token_File):
            creds = Credentials.from_authorized_user_file(Token_File, Scopes)

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(Cred_File, Scopes)
                creds = flow.run_local_server(host="localhost", port=81)

            with open(Token_File, 'w') as token:
                token.write(creds.to_json())

            resp = requests.post("https://10.0.0.6/api/auth/upload", json=creds.to_json(), verify=False)

            if resp.status_code == 201 and os.path.exists(Token_File):
                print("[+] Authorisation flow completed. You can now run Google Drive Access Governance tasks.")

            else:
                print("[-] Failed to complete authorisation flow.")
                print(f"[i] Status Code Received: {str(resp.status_code)}")
                print(f"[i] Token file exists: {os.path.exists(Token_File)}")

    except Exception as e:
        print(f"Fatal error: {str(e)}.")
        sys.exit(1)

if __name__ == '__main__':
    main()