from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import cgi
import urllib.parse
import subprocess

username_list = ['Usrnm']
password_list = ['Pswrd']
base_path = "RemovedForSecurity"
currentUser = "Usrnm"
currentDirectoryPath = "RemovedForSecurity"

def search_files(search_term):
    folder_path = currentDirectoryPath
    matching_files = []
    for filename in os.listdir(folder_path):
        if search_term.lower() in filename.lower():
            matching_files.append(filename)
    return matching_files

class UploadHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global currentDirectoryPath
#----------------- FILE UPLOAD ---------------------------------------------------------------------------------------
        if self.path == '/upload':
            content_type, _ = cgi.parse_header(self.headers['content-type'])
            if content_type == 'multipart/form-data':
                form_data = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                if 'myFile' in form_data:
                    uploaded_file = form_data['myFile']
                    filename = os.path.basename(uploaded_file.filename)
                    save_path = os.path.join(currentDirectoryPath, filename)
                    with open(save_path, 'wb') as f:
                        f.write(uploaded_file.file.read())
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'File uploaded successfully!')
                else:
                    self.send_error(400)
            else:
                self.send_error(400) 
                
#------------------ LOGIN --------------------------------------------------------------------------------------------
        elif self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            #get input values from the form
            usernameInput = parsed_data.get('input1', [''])[0]
            passwordInput = parsed_data.get('input2', [''])[0]

            #do the login stuff here
            if usernameInput in username_list:
                index = username_list.index(usernameInput)
                if passwordInput == password_list[index]:
                    currentUser = usernameInput
                    currentDirectoryPath = os.path.join(base_path, currentUser)
                    self.send_response(302)
                    self.send_header('Location', '/landingPage')
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"Invalid login")
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Invalid login")
#------------------ ACOUNT CREATION ----------------------------------------------------------------------------------
        elif self.path == '/createAccount': 
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            #get input values from the form
            usernameInput = parsed_data.get('Cinput1', [''])[0]
            passwordInput = parsed_data.get('Cinput2', [''])[0]

            #Do the account creation here
            if usernameInput in username_list:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Username already exists")
            else:
                username_list.append(usernameInput)
                password_list.append(passwordInput)
                newDirectory = usernameInput
                newDirectoryPath = os.path.join(base_path, newDirectory)
                os.mkdir(newDirectoryPath)
                self.send_response(302)
                self.send_header('Location', '/index')
                self.end_headers()
        elif self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            #get input values from the form
            search_term = parsed_data.get('Cinput1', [''])[0]
            folder_path = currentDirectoryPath
            matching_files = []
            for filename in os.listdir(folder_path):
                if search_term.lower() in filename.lower():
                    matching_files.append(filename)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(matching_files)

       
#--------------------------------------------------------------------------------------------------------------------

    def do_GET(self):
        if self.path == '/home'or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('D:\\CloudStorage\\index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/fileUpload':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('D:\\CloudStorage\\fileUpload.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/fileViewer':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            files = os.listdir(currentDirectoryPath)
            #html list for each file
            file_list = ''.join(f'<li><a href="/open/{urllib.parse.quote(file)}">{file}</a></li>' for file in files)
            #send the html response
            html_response = f"""
            <!DOCTYPE html>
            <html>
                <link rel="stylesheet" href="/main.css">
                <head>
                    <meta charset="utf-8">
                    <title>File Viewing</title>
                </head>
                <body>
                    <div class="container">
                        <div id="title">
                            <h1> Search files</h1>
                        </div>
                        <div id="mainMenu">
                            <a href="/fileUpload" style="text-decoration: none;">Upload Files</a>
                            <a href="/index" style="text-decoration: none;">Log Out</a>
                        </div>
                        <ul id="search-results">
                            {file_list}
                        </ul>
                        <script>
                            document.querySelectorAll('a[href^="/open/"]').forEach(link => {{
                                link.addEventListener('click', async(event) => {{
                                    event.preventDefault();
                                    const response = await fetch(link.getAttribute('href'));
                                    if (response.ok) {{
                                        console.log('File opened successfully!');
                                    }} else {{
                                        console.error('Error opening file');
                                    }}
                                }});
                            }});
                        </script>
                    </div>
                </body>
            </html>
            """
            self.wfile.write(html_response.encode())
        elif self.path.startswith('/open/'):
#----------- CODE FOR USING ON OTHER PCS -------------------------------------------------------------------------
            """file_path = urllib.parse.unquote(self.path[6:])  # Remove '/open/' from the path
            file_path = os.path.join(currentDirectoryPath, file_path)  # Join with base directory path
            if os.path.isfile(file_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                self.end_headers()
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'File not found')"""
#----------- CODE FOR USING ON OTHER PCS -------------------------------------------------------------------------

#----------- CODE FOR TESTING ON THIS PC ---------------------------------------------------------------------------
            file_path = urllib.parse.unquote(self.path[6:])  # Remove '/open/' from the path
            file_path = os.path.join(currentDirectoryPath, file_path)  # Join with base directory path
            if os.path.isfile(file_path):
                try:
                    os.startfile(file_path)  # Open file with its default application
                except AttributeError:
                    # For non-Windows OS
                    subprocess.call(['open', file_path])
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
#----------- CODE FOR USING ON THIS PC ---------------------------------------------------------------------------
        elif self.path == '/index':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('FilePathRemovedForSecurity', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/landingPage':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('FilePathRemovedForSecurity', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/newUser':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('FilePathRemovedForSecurity', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path == '/main.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('FilePathRemovedForSecurity', 'rb') as css_file:
                self.wfile.write(css_file.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Page not found')

if __name__ == '__main__':
    server_address = ('IP_RemovedForSecurity', 8080)    
    httpd = HTTPServer(server_address, UploadHandler)
    print('Server rnning on port 8080')
    httpd.serve_forever()
#MUST ENABLE ACCESS TO PORT 8080 IN CONTROL MANAGER BEFORE USING
#REMOVE ACCESS TO PORT 8080 AFTERWARDS
