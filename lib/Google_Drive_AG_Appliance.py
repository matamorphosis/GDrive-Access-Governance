#!/usr/bin/python3
import os, re, pathlib, sys, colorama, logging, datetime, json, sqlite3, threading, time, dateutil.parser
from flask import Flask, render_template, flash, request, redirect, url_for, session, send_from_directory, jsonify
from flask_compress import Compress
from signal import signal, SIGINT
from logging.handlers import RotatingFileHandler
Bad_Characters = ["|", "&", "?", "\\", "\"", "\'", "[", "]", ">", "<", "~", "`", ";", "{", "}", "%", "^", "--", "++",
                  "+", "'", "(", ")", "*", "="]

if __name__ == "__main__":

    try:

        def Date():
            return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        try:
            GDAG_Working_Directory = pathlib.Path(__file__).parent.absolute()

            if str(GDAG_Working_Directory) != str(os.getcwd()):
                print(f"[i] Google Drive AG Appliance has been called from outside of its directory, changing the working directory to {str(GDAG_Working_Directory)}.")
                os.chdir(GDAG_Working_Directory)

                if str(GDAG_Working_Directory) != str(os.getcwd()):
                    sys.exit(f'{Date()} Error setting the working directory.')

        except:
            sys.exit(f'{Date()} Error setting the working directory.')

        try:
            File_Path = os.path.dirname(os.path.realpath('__file__'))
            app = Flask(__name__, instance_path=os.path.join(File_Path, 'static/protected'))
            Compress(app)
            app.config.update(
                SESSION_COOKIE_SECURE=True,
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE='Strict',
            )
            app.permanent_session_lifetime = datetime.timedelta(minutes=5)

        except:
            app.logger.fatal(f'{Date()} Startup error, ensure all necessary libraries are imported and installed.')
            sys.exit()

        def Load_Web_App_Configuration():

            try:
                File_Dir = os.path.dirname(os.path.realpath('__file__'))
                Configuration_File = os.path.join(File_Dir, 'config/config.json')
                logging.info(f"{Date()} Loading web application's configuration data.")

                with open(Configuration_File) as JSON_File:
                    Configuration_Data = json.load(JSON_File)

                WA_Debug = Configuration_Data['web-app']['debug']
                WA_Host = Configuration_Data['web-app']['host']
                WA_Port = Configuration_Data['web-app']['port']

                if WA_Host and WA_Port:
                    return [WA_Debug, WA_Host, WA_Port]

                else:
                    return None

            except Exception as e:
                logging.warning(f"{Date()} {str(e)}.")
                sys.exit()

        def handler(signal_received, frame):
            print('[i] CTRL-C detected. Shutting program down.')
            DB_Conn.close()
            sys.exit()

        class API_Caller:

            def __init__(self, task_id, task_type):
                self.task_id = task_id
                self.task_type = task_type

            def Controller(self, control):

                if control in ["Running", "Stopped"]:
                    DB_Conn = sqlite3.connect(DB_Filename)
                    DB_Cursor = DB_Conn.cursor()

                    if self.task_type == "Domains":
                        DB_Cursor.execute(f"""UPDATE domain_tasks SET run_status = "{control}" WHERE id = {self.task_id}""")

                    elif self.task_type == "Emails":
                        DB_Cursor.execute(f"""UPDATE email_tasks SET run_status = "{control}" WHERE id = {self.task_id}""")

                    DB_Conn.commit()
                    DB_Conn.close()

            def Call_API(self):
                import GDAG_Lib
                Google_Drive = GDAG_Lib.Main(DB_Filename)
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()

                if self.task_type == "Domains":
                    DB_Cursor.execute(f"""SELECT * FROM domain_tasks WHERE id = {self.task_id};""")
                    Result = DB_Cursor.fetchone()
                    DB_Conn.close()

                elif self.task_type == "Emails":
                    DB_Cursor.execute(f"""SELECT * FROM email_tasks WHERE id = {self.task_id};""")
                    Result = DB_Cursor.fetchone()
                    DB_Conn.close()

                Page_Size = 1000
                Thread_0 = threading.Thread(target=self.Controller, args=("Running",))
                Thread_0.start()
                Thread_0.join()

                Permitted = Result[4]
                Directories = Result[6]
                Included = Result[7]

                if Directories and str(Included) == "True" and str(Permitted) == "True":
                    Thread_1 = threading.Thread(target=Google_Drive.Governance_Check, args=(Page_Size,), kwargs={f"permitted_{self.task_type.lower()}": Result[3].split(", "), "Auto Function": Result[5],"Included_Directories": Directories.split(", "),})

                elif Directories and str(Included) == "False" and str(Permitted) == "True":
                    Thread_1 = threading.Thread(target=Google_Drive.Governance_Check, args=(Page_Size,), kwargs={f"permitted_{self.task_type.lower()}": Result[3].split(", "), "Auto Function": Result[5], "Excluded_Directories": Directories.split(", "),})

                elif Directories and str(Included) == "True" and str(Permitted) == "False":
                    Thread_1 = threading.Thread(target=Google_Drive.Governance_Check, args=(Page_Size,), kwargs={f"non_permitted_{self.task_type.lower()}": Result[3].split(", "), "Auto Function": Result[5], "Included_Directories": Directories.split(", "),})

                elif Directories and str(Included) == "False" and str(Permitted) == "False":
                    Thread_1 = threading.Thread(target=Google_Drive.Governance_Check, args=(Page_Size,), kwargs={f"non_permitted_{self.task_type.lower()}": Result[3].split(", "), "Auto Function": Result[5], "Excluded_Directories": Directories.split(", "),})

                elif not Directories and str(Permitted) == "True":
                    Thread_1 = threading.Thread(target=Google_Drive.Governance_Check, args=(Page_Size,), kwargs={f"permitted_{self.task_type.lower()}": Result[3].split(", "), "Auto Function": Result[5],})

                elif not Directories and str(Permitted) == "False":
                    Thread_1 = threading.Thread(target=Google_Drive.Governance_Check, args=(Page_Size,), kwargs={f"non_permitted_{self.task_type.lower()}": Result[3].split(", "), "Auto Function": Result[5],})

                Thread_1.start()
                Thread_1.join()
                Thread_2 = threading.Thread(target=self.Controller, args=("Stopped",))
                Thread_2.start()
                Thread_2.join()

        DB_Filename = 'GDriveAGApp.db'
        Schema_Filename = 'Schema.sql'
        Token_File = "token.pickle"
        DB_Is_New = not os.path.exists(DB_Filename)
        DB_Conn = sqlite3.connect(DB_Filename)

        if DB_Is_New:

            with open(Schema_Filename, 'rt') as f:
                Schema = f.read()

            DB_Conn.executescript(Schema)
            DB_Conn.close()

        else:
            DB_Conn.executescript(f"""UPDATE domain_tasks SET run_status = "Stopped";""")
            DB_Conn.executescript(f"""UPDATE email_tasks SET run_status = "Stopped";""")
            DB_Conn.commit()
            DB_Conn.close()

        if os.path.exists(Token_File):
            File_Epoch_time = os.path.getctime(Token_File)
            File_DateTime = datetime.datetime.utcfromtimestamp(File_Epoch_time).strftime("%Y-%m-%d %H:%M:%S")
            File_DateTime = dateutil.parser.parse(File_DateTime)
            Right_Now_10_Days_Ago = datetime.datetime.today() - datetime.timedelta(days=10)

            if File_DateTime < Right_Now_10_Days_Ago:
                os.remove(Token_File)

        Application_Details = Load_Web_App_Configuration()
        signal(SIGINT, handler)
        formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        handler = RotatingFileHandler('GDAG_Appliance.log', maxBytes=10000, backupCount=5)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.secret_key = os.urandom(24)

        @app.after_request
        def apply_caching(response):

            try:
                response.headers["X-Frame-Options"] = "SAMEORIGIN"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                response.headers["X-Content-Type"] = "nosniff"
                response.headers["Server"] = ""
                response.headers["Pragma"] = "no-cache"
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, pre-check=0, post-check=0, max-age=0, s-maxage=0"
                return response

            except Exception as e:
                app.logger.error(e)

        @app.errorhandler(404)
        def page_not_found(e):

            try:
                return render_template('404.html'), 404

            except Exception as e:
                app.logger.error(e)


        @app.errorhandler(405)
        def method_not_allowed(e):

            try:
                return render_template('no_method.html'), 405

            except Exception as e:
                app.logger.error(e)

        app.register_error_handler(404, page_not_found)
        app.register_error_handler(405, method_not_allowed)

        @app.route('/')
        def index():

            try:
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute("""SELECT * FROM open_results;""")
                Open_Results = DB_Cursor.fetchall()
                DB_Cursor.execute("""SELECT * FROM certified_results;""")
                Cert_Results = DB_Cursor.fetchall()
                DB_Cursor.execute("""SELECT COUNT(*) FROM email_tasks;""")
                Email_Tasks = DB_Cursor.fetchone()
                DB_Cursor.execute("""SELECT COUNT(*) FROM domain_tasks;""")
                Domain_Tasks = DB_Cursor.fetchone()
                Total_Open_Emails = []
                Total_Cert_Emails = []
                Result_Labels = ["Open Results", "Certified Results"]
                Task_Labels = ["Email Tasks", "Domain Tasks"]
                Result_Colors = ["#ff0000", "#008000"]
                Task_Colors = ["#0000ff", "#800080"]

                if Open_Results:

                    for Open_Result in Open_Results:
                        Current_Emails = Open_Result[2].split(", ")
                        Total_Open_Emails += Current_Emails

                if Cert_Results:

                    for Cert_Result in Cert_Results:
                        Current_Emails = Cert_Result[2].split(", ")
                        Total_Cert_Emails += Current_Emails

                if not Total_Cert_Emails and not Total_Cert_Emails and Email_Tasks[0] == 0 and Domain_Tasks[0] == 0:
                    return render_template('index.html', Result_Values=None, Task_Values=None)

                elif not Total_Cert_Emails and not Total_Cert_Emails:
                    Task_Values = [Email_Tasks[0], Domain_Tasks[0]]
                    return render_template('index.html', Result_Values=None, Task_Values=[Task_Values, Task_Labels, Task_Colors])

                elif Email_Tasks[0] == 0 and Domain_Tasks[0] == 0:
                    Result_Values = [len(Total_Open_Emails), len(Total_Cert_Emails)]
                    return render_template('index.html', Result_Values=[Result_Values, Result_Labels, Result_Colors], Task_Values=None)

                else:
                    Result_Values = [len(Total_Open_Emails), len(Total_Cert_Emails)]
                    Task_Values = [Email_Tasks[0], Domain_Tasks[0]]
                    return render_template('index.html', Result_Values=[Result_Values, Result_Labels, Result_Colors], Task_Values=[Task_Values, Task_Labels, Task_Colors])

            except Exception as e:
                app.logger.error(e)

        @app.route('/tasks/email', methods=['GET'])
        def email_tasks():

            try:
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute("""SELECT * FROM email_tasks;""")
                DB_Results = DB_Cursor.fetchall()
                DB_Conn.close()
                return render_template('email_tasks.html', newtask=False, Tasks=DB_Results)

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('index'))

        @app.route('/tasks/domain', methods=['GET'])
        def domain_tasks():

            try:
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute("""SELECT * FROM domain_tasks;""")
                DB_Results = DB_Cursor.fetchall()
                DB_Conn.close()
                return render_template('domain_tasks.html', newtask=False, Tasks=DB_Results)

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('index'))

        @app.route('/tasks/email/new', methods=['GET', 'POST'])
        def new_email_task():

            try:

                if 'task_name' in request.form and 'finishtask' in request.form:

                    if any(Bad_Char in form_data for Bad_Char in Bad_Characters for form_data in [request.form['task_name'], request.form['task_emails']]):
                        return render_template('email_tasks.html', newtask=True, error="Please ensure fields do not have any bad special characters.")

                    if 'emailoptions' in request.form and 'task_emails' in request.form:
                        DB_Conn = sqlite3.connect(DB_Filename)

                        try:
                            if request.form['emailoptions'] not in ["True", "False"]:
                                return render_template('email_tasks.html', newtask=True, error="Invalid request, please try again.")

                            else:
                                Option = request.form['emailoptions']
                                task_emails = request.form['task_emails'].replace("\r", "")
                                task_emails = task_emails.replace("\n", ", ")
                                auto_function = "None"

                                if 'revoke' in request.form and 'certify' in request.form:
                                    return render_template('email_tasks.html', newtask=True, error="Invalid request, please only select one auto function. Either certify or revoke.")

                                if 'revoke' in request.form:

                                    if request.form['revoke'] == "on":
                                        auto_function = "Revoke"

                                elif 'certify' in request.form:

                                    if request.form['certify'] == "on":
                                        auto_function = "Certify"

                                if 'diroptions' in request.form and 'task_directories' in request.form:

                                    if request.form['diroptions'] and request.form['task_directories']:

                                        if any(Bad_Char in request.form['task_directories'] for Bad_Char in Bad_Characters):
                                            return render_template('email_tasks.html', newtask=True, error="Please ensure fields do not have any bad special characters.")

                                        if request.form['diroptions'] not in ["True", "False"]:
                                            return render_template('email_tasks.html', newtask=True, error="Invalid request, please try again.")

                                        else:
                                            Dir_Option = request.form['diroptions']
                                            task_directories = request.form['task_directories'].replace("\r", "")
                                            task_directories = task_directories.replace("\n", ", ")
                                            DB_Conn.executescript(f"""INSERT INTO email_tasks (name, run_status, emails, permitted, autofunc, directories, included) values ('{request.form['task_name']}', 'Stopped', '{task_emails}', '{Option}', '{auto_function}', '{task_directories}', '{Dir_Option}');""")

                                    else:
                                        DB_Conn.executescript(f"""INSERT INTO email_tasks (name, run_status, emails, permitted, autofunc) values ('{request.form['task_name']}', 'Stopped', '{task_emails}', '{Option}', '{auto_function}');""")

                                else:
                                    DB_Conn.executescript(f"""INSERT INTO email_tasks (name, run_status, emails, permitted, autofunc) values ('{request.form['task_name']}', 'Stopped', '{task_emails}', '{Option}', '{auto_function}');""")

                        except:
                            return render_template('email_tasks.html', newtask=True, error="Invalid request, please try again.")

                        DB_Conn.commit()
                        DB_Conn.close()

                    return redirect(url_for('email_tasks'))

                else:
                    return render_template('email_tasks.html', newtask=True)

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('email_tasks'))

        @app.route('/tasks/domain/new', methods=['GET', 'POST'])
        def new_domain_task():

            try:

                if 'task_name' in request.form and 'finishtask' in request.form:

                    if any(Bad_Char in form_data for Bad_Char in Bad_Characters for form_data in [request.form['task_name'], request.form['task_domains']]):
                        return render_template('domain_tasks.html', newtask=True, error="Please ensure fields do not have any bad special characters.")

                    if 'domainoptions' in request.form:
                        DB_Conn = sqlite3.connect(DB_Filename)

                        if request.form['domainoptions'] not in ["True", "False"]:
                            return render_template('domain_tasks.html', newtask=True, error="Invalid request, please try again.")

                        else:
                            Option = request.form['domainoptions']
                            task_domains = request.form['task_domains'].replace("\r", "")
                            task_domains = task_domains.replace("\n", ", ")
                            revoke = "False"
                            auto_function = "None"

                            if 'revoke' in request.form:

                                if request.form['revoke'] == "on":
                                    auto_function = "Revoke"

                            elif 'certify' in request.form:

                                if request.form['certify'] == "on":
                                    auto_function = "Certify"

                            if 'diroptions' in request.form and 'task_directories' in request.form:

                                if request.form['diroptions'] and request.form['task_directories']:

                                    if any(Bad_Char in request.form['task_directories'] for Bad_Char in Bad_Characters):
                                        return render_template('domain_tasks.html', newtask=True, error="Please ensure fields do not have any bad special characters.")

                                    if request.form['diroptions'] not in ["True", "False"]:
                                        return render_template('domain_tasks.html', newtask=True, error="Invalid request, please try again.")

                                    else:
                                        Dir_Option = request.form['diroptions']
                                        task_directories = request.form['task_directories'].replace("\r", "")
                                        task_directories = task_directories.replace("\n", ", ")
                                        DB_Conn.executescript(f"""INSERT INTO domain_tasks (name, run_status, domains, permitted, autofunc, directories, included) values ('{request.form['task_name']}', 'Stopped', '{task_domains}', '{Option}', '{auto_function}', '{task_directories}', '{Dir_Option}');""")

                                else:
                                    DB_Conn.executescript(f"""INSERT INTO domain_tasks (name, run_status, domains, permitted, autofunc) values ('{request.form['task_name']}', 'Stopped', '{task_domains}', '{Option}', '{auto_function}');""")

                            else:
                                DB_Conn.executescript(f"""INSERT INTO domain_tasks (name, run_status, domains, permitted, autofunc) values ('{request.form['task_name']}', 'Stopped', '{task_domains}', '{Option}', '{auto_function}');""")

                        DB_Conn.commit()
                        DB_Conn.close()

                    return redirect(url_for('domain_tasks'))

                else:
                    return render_template('domain_tasks.html', newtask=True)

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('domain_tasks'))

        @app.route('/tasks/email/delete/<taskid>', methods=['POST'])
        def email_task_delete(taskid):

            try:
                taskid = str(int(taskid))
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute(f"""DELETE from email_tasks where id = {taskid}""")
                DB_Conn.commit()
                DB_Conn.close()
                return redirect(url_for('email_tasks'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('email_tasks'))

        @app.route('/tasks/domain/delete/<taskid>', methods=['POST'])
        def domain_task_delete(taskid):

            try:
                taskid = str(int(taskid))
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute(f"""DELETE from domain_tasks where id = {taskid}""")
                DB_Conn.commit()
                DB_Conn.close()
                return redirect(url_for('domain_tasks'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('domain_tasks'))

        @app.route('/tasks/email/run/<taskid>', methods=['POST'])
        def email_task_run(taskid):

            try:
                taskid = str(int(taskid))
                New_Task = API_Caller(taskid, "Emails")
                New_Thread = threading.Thread(target=New_Task.Call_API)
                New_Thread.start()
                return redirect(url_for('email_tasks'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('email_tasks'))

        @app.route('/tasks/domain/run/<taskid>', methods=['POST'])
        def domain_task_run(taskid):

            try:
                taskid = str(int(taskid))
                New_Task = API_Caller(taskid, "Domains")
                New_Thread = threading.Thread(target=New_Task.Call_API)
                New_Thread.start()
                return redirect(url_for('domain_tasks'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('domain_tasks'))

        @app.route('/results/open', methods=['GET'])
        def results():

            try:
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute("""SELECT * FROM open_results;""")
                DB_Results = DB_Cursor.fetchall()
                DB_Conn.close()
                return render_template('results.html', revoke_page=False, Results=DB_Results)

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('index'))

        @app.route('/results/certified', methods=['GET'])
        def results_certified():

            try:
                DB_Conn = sqlite3.connect(DB_Filename)
                DB_Cursor = DB_Conn.cursor()
                DB_Cursor.execute("""SELECT * FROM certified_results;""")
                DB_Results = DB_Cursor.fetchall()
                DB_Conn.close()
                return render_template('certified_results.html', revoke_page=False, Results=DB_Results)

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('results'))

        @app.route('/results/review/<resultid>', methods=['GET', 'POST'])
        def result_review_page(resultid):

            try:

                if not any(char in resultid for char in ["(", ")", ";", "--", "++", "\"", "\'"]):
                    resultid = (resultid)
                    DB_Conn = sqlite3.connect(DB_Filename)
                    DB_Cursor = DB_Conn.cursor()
                    DB_Cursor.execute(f"""SELECT emails FROM open_results WHERE id = '{resultid}';""")
                    DB_Results = DB_Cursor.fetchone()
                    Email_List = DB_Results[0].split(", ")
                    DB_Conn.close()
                    return render_template('results.html', review_page=True, Result_ID=resultid, Results=Email_List)

                else:
                    return redirect(url_for('results'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('results'))

        @app.route('/results/revoke/<resultid>', methods=['POST'])
        def result_revoke(resultid):

            try:

                if 'email' in request.form:

                    if not any(char in resultid for char in ["(", ")", ";", "--", "++", "\"", "\'"]):

                        def nested_result_revocation_function(Result_ID, Request_Form):
                            DB_Conn = sqlite3.connect(DB_Filename)
                            DB_Cursor = DB_Conn.cursor()
                            DB_Cursor.execute(f"""SELECT emails FROM certified_results WHERE id = '{Result_ID}';""")
                            Cert_Results = DB_Cursor.fetchone()

                            if not Cert_Results:
                                DB_Cursor.execute(f"""SELECT emails FROM open_results WHERE id = '{Result_ID}';""")
                                DB_Results = DB_Cursor.fetchone()
                                Email_List = DB_Results[0].split(", ")

                                if Request_Form["email"] in Email_List:
                                    import GDAG_Lib
                                    Google_Drive = GDAG_Lib.Main(DB_Filename)
                                    Revoked = Google_Drive.Revoke_Access(Result_ID, Request_Form["email"])

                                    if Revoked:
                                        Email_List.remove(Request_Form["email"])

                                        if Email_List == []:
                                            DB_Cursor.execute(f"""DELETE from open_results where id = "{Result_ID}";""")
                                            DB_Conn.commit()

                                        else:
                                            Emails = ", ".join(Email_List)
                                            DB_Cursor.execute(f"""UPDATE open_results SET emails = "{Emails}" WHERE id = "{Result_ID}";""")
                                            DB_Conn.commit()

                                DB_Conn.close()

                        Thread_1 = threading.Thread(target=nested_result_revocation_function, args=(resultid, request.form))
                        Thread_1.start()
                        return redirect(url_for('results'))

                    else:
                        return redirect(url_for('results'))

                else:
                    return redirect(url_for('results'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('results'))

        @app.route('/results/certify/<resultid>', methods=['POST'])
        def result_certify(resultid):

            try:

                if 'email' in request.form:

                    if not any(char in resultid for char in ["(", ")", ";", "--", "++", "\"", "\'"]):
                        DB_Conn = sqlite3.connect(DB_Filename)
                        DB_Cursor = DB_Conn.cursor()
                        DB_Cursor.execute(f"""SELECT * FROM open_results WHERE id = '{resultid}';""")
                        Open_Results = DB_Cursor.fetchone()
                        DB_Cursor.execute(f"""SELECT * FROM certified_results WHERE id = '{resultid}';""")
                        Cert_Results = DB_Cursor.fetchone()
                        Open_Results_Email_List = Open_Results[3].split(", ")
                        Cert_Results_Email_List = []

                        if Cert_Results:
                            Cert_Results_Email_List = Cert_Results[3].split(", ")

                        if request.form["email"] in Open_Results_Email_List:
                            Open_Results_Email_List.remove(request.form["email"])

                            if Cert_Results:
                                Cert_Results_Email_List.append(request.form["email"])

                                if Open_Results_Email_List == []:
                                    Emails = ", ".join(Cert_Results_Email_List)
                                    DB_Cursor.execute(f"""DELETE from open_results where id = "{resultid}";""")
                                    DB_Cursor.execute(f"""UPDATE certified_results SET emails = "{Emails}" WHERE id = "{resultid}";""")
                                    DB_Conn.commit()

                                else:
                                    Open_Emails = ", ".join(Open_Results_Email_List)
                                    Cert_Emails = ", ".join(Cert_Results_Email_List)
                                    DB_Cursor.execute(f"""UPDATE open_results SET emails = "{Open_Emails}" WHERE id = "{resultid}";""")
                                    DB_Cursor.execute(f"""UPDATE certified_results SET emails = "{Cert_Emails}" WHERE id = "{resultid}";""")
                                    DB_Conn.commit()

                            else:
                                Cert_Results_Email_List = [request.form["email"]]

                                if Open_Results_Email_List == []:
                                    Emails = ", ".join(Cert_Results_Email_List)
                                    DB_Cursor.execute(f"""DELETE from open_results where id = "{resultid}";""")
                                    DB_Cursor.execute(f"""INSERT INTO certified_results (id, file_name, trashed, emails, created_at) values ('{Open_Results[0]}', '{Open_Results[1]}', '{Open_Results[2]}', '{Emails}', '{Open_Results[4]}');""")
                                    DB_Conn.commit()

                                else:
                                    Open_Emails = ", ".join(Open_Results_Email_List)
                                    Cert_Emails = ", ".join(Cert_Results_Email_List)
                                    DB_Cursor.execute(f"""UPDATE open_results SET emails = "{Open_Emails}" WHERE id = "{resultid}";""")
                                    DB_Cursor.execute(f"""INSERT INTO certified_results (id, file_name, trashed, emails, created_at) values ('{Open_Results[0]}', '{Open_Results[1]}', '{Open_Results[2]}', '{Cert_Emails}', '{Open_Results[4]}');""")
                                    DB_Conn.commit()

                        else:
                            return redirect(url_for('results'))

                        DB_Conn.close()
                        return redirect(url_for('results'))

                    else:
                        return redirect(url_for('results'))

                else:
                    return redirect(url_for('results'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('results'))

        @app.route('/results/create/<resultid>', methods=['POST'])
        def result_create(resultid):

            try:

                if all(item in request.form for item in ['email', 'role', 'grantee']):

                    if re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", request.form['email']) and any(role == request.form['role'] for role in ['owner', 'organizer', 'fileOrganizer', 'reader', 'writer', 'commenter']) and any(grantee == request.form['grantee'] for grantee in ['user', 'group', 'domain', 'anyone']):

                        if not any(char in resultid for char in ["(", ")", ";", "--", "++", "\"", "\'"]):

                            def nested_result_create_function(Result_ID, Request_Form):

                                if Request_Form['role'] == 'owner':
                                    Transfer_Ownership = True

                                else:
                                    Transfer_Ownership = False

                                DB_Conn = sqlite3.connect(DB_Filename)
                                DB_Cursor = DB_Conn.cursor()
                                DB_Cursor.execute(f"""SELECT * FROM open_results WHERE id = '{Result_ID}';""")
                                Open_Results = DB_Cursor.fetchone()
                                DB_Cursor.execute(f"""SELECT * FROM certified_results WHERE id = '{Result_ID}';""")
                                Cert_Results = DB_Cursor.fetchone()
                                Open_Results_Email_List = Open_Results[3].split(", ")
                                Cert_Results_Email_List = []

                                if Cert_Results:
                                    Cert_Results_Email_List = Cert_Results[3].split(", ")

                                if Request_Form["email"] not in Open_Results_Email_List and Request_Form["email"] not in Cert_Results_Email_List:
                                    import GDAG_Lib
                                    Google_Drive = GDAG_Lib.Main(DB_Filename)
                                    Provisioned = Google_Drive.Provision_Access(Result_ID, Transfer_Ownership, {"role": Request_Form['role'], "type": Request_Form['grantee'], "emailAddress": Request_Form["email"]})

                                    if Provisioned:

                                        if Cert_Results:
                                            Cert_Results_Email_List.append(Request_Form["email"])
                                            Emails = ", ".join(Cert_Results_Email_List)
                                            DB_Cursor.execute(f"""UPDATE certified_results SET emails = "{Emails}" WHERE id = "{Result_ID}";""")
                                            DB_Conn.commit()

                                        else:
                                            Cert_Results_Email_List = [Request_Form["email"]]
                                            Emails = ", ".join(Cert_Results_Email_List)
                                            DB_Cursor.execute(f"""INSERT INTO certified_results (id, file_name, trashed, emails, created_at) values ('{Open_Results[0]}', '{Open_Results[1]}', '{Open_Results[2]}', '{Emails}', '{Open_Results[4]}');""")
                                            DB_Conn.commit()

                                DB_Conn.close()

                            Thread_1 = threading.Thread(target=nested_result_create_function, args=(resultid, request.form))
                            Thread_1.start()
                            return redirect(url_for('results'))

                        else:
                            return redirect(url_for('results'))

                    else:
                        return redirect(url_for('results'))

                else:
                    return redirect(url_for('results'))

            except Exception as e:
                app.logger.error(e)
                return redirect(url_for('results'))

        app.run(debug=Application_Details[0], host=Application_Details[1], port=Application_Details[2], threaded=True)

    except Exception as e:
        sys.exit(f"[-] {str(e)}.")