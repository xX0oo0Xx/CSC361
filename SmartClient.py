import ssl
import socket
import sys
import re
REDIRECT_LIMIT = 0

class SmartClient:
    def __init__(self,url,port=80):
        """
        Constructor for SmartClient.

        Args:
            url (_type_): Input from argv[1].
            port (int, optional): Port to connect. Defaults to 443.

        Raises:
            ValueError: Raise if input port invalid.
        """
        self.url = url
        if port != 80 and port != 443:
            raise ValueError("Invalid web port# [Hint: 80(HTTP), 443(HTTPS)]")
        
        self.port = 80 if (port == 80) else 443
        scheme = re.search(r"(https?://).*",url,re.IGNORECASE)
        self.scheme = scheme.group(1) if scheme else ""
        
        if scheme:
            self.port = 80 if self.scheme=="http://" else 443
            print(f"Scheme detected: '{self.scheme}'\r\nUsing port :{self.port} for connection.")
        
        #Formatting input.
        if url.startswith(('http://', 'https://')):
            self.host = re.search(r'https?://([^/]+)/?', url).group(1)
            self.path = "/" + "/".join(url.split("/")[3:])
        else:
            parts = url.split("/", 1)
            self.host = parts[0]
            if len(parts) ==1:
                self.path = "/"
            else:
                self.path = "/" + parts[1]

    def generate_defalt_connecton(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect((self.host, self.port))
        except Exception as e:
            print(f"Generation defalt socket connection failed: {e}.")
            s.close()
            self.port = 443
            return self.generate_connection()
        
        return s
                         
    def generate_connection(self):
        """
        Generate socket and ssl socket and do connect.
        Returns:
            _type_: A wrapped ssl socket.
        """
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error as e:
            print(f"socket creatiion error: {e}")
        except NameError as e:
            print(f"Raise {e}, socket moduel does not imported")
        except Exception as e:
            print(f"Serious error occurs: {e}")
        
        context = ssl.create_default_context()
        try:
            ssl_soc = context.wrap_socket(s,server_hostname=self.host)
        except (ssl.SSLError, OSError) as e:
            print(f"Network connection failed: {e}")
            
        try:
            ssl_soc.connect((self.host,self.port))
        except ssl.SSLError as e:
            print(f"Negotiation failure : {e}, with Host: {self.host} Port: {self.port}: \r\n Try another port...")
            self.port = 80 if self.port == 443 else 443
            return self.generate_connection()
        except socket.gaierror as e:
            print(f"Invalid IP address or Hostname: {e}")
        except (OSError,socket.error) as e:
            print(f"Failed to establish connection: {e}")
        except Exception as e:
            print(f"Serious error occurs: {e}")
        
        
        return ssl_soc
    
    def handle_redirect(self, response : str) -> bool:
        """
        Handler of redirection.
        Args:
            response (str): HTTP response from server.

        Raises:
            RuntimeError: Raise if input response invalid.
            socket.timeout: Raise if redirect too many times(defaults to 5).

        Returns:
            bool: If there is a redirection, return True.
            Else return False.
        """
        global REDIRECT_LIMIT
        
        if type(response) != str:
            raise RuntimeError("RuntimeError: the input response is not a valid type")
        if REDIRECT_LIMIT >= 5:
            raise socket.timeout("TimeOutError: Too many redirect")
        
        status_code = response.split()[1]
        if status_code in ('301','302'):
            dest = re.search(r'Location: (.+)',response).group(1).strip()
            
            scheme = re.search(r"(https?://).*",dest,re.IGNORECASE)
            self.scheme = scheme.group(1) if scheme else ""
            
            if scheme:
                self.port = 80 if self.scheme=="http://" else 443
                print(f"Scheme detected: '{self.scheme}' \r\n Changing port to -----> {self.port}")
            
            if dest.startswith(('http://', 'https://')):
                self.host = re.search(r'https?://([^/]+)/?', dest).group(1)
                self.path = "/" + "/".join(dest.split("/")[3:])
            else:
                parts = dest.split("/", 1)
                self.host = parts[0]
                if len(parts) ==1:
                    self.path = "/"
                else:
                    self.path = "/" + parts[1]
            print(f"Redirecting to new destination: {dest}")
            REDIRECT_LIMIT +=1
            return True
        else:
            return False
        
    def handle_cookies(self,response : str) -> list:
        """
        Handler of Set-Cookies.
        Args:
            response (str): HTTP response from server.

        Raises:
            RuntimeError: Raise if input response invalid.

        Returns:
            list: A list which contains formatted cookie informations.
        references:\n
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie\n
        https://en.wikipedia.org/wiki/HTTP_cookie
        """
        if type(response) != str:
            raise RuntimeError("RuntimeError: the input response is not a valid type")
        
        cookie_pool = []
        cookies = re.findall(r'Set-Cookie: (.*)',response)
        if cookies:
            for cookie in cookies:
                parts = cookie.split(";",1)
                fp = parts[0]
                sp = parts[1]
                
                name = fp.split("=")[0]
                expires = re.search(r'expires=([^;]+)',sp, re.IGNORECASE)
                domain = re.search(r'domain=([^;]+)',sp, re.IGNORECASE)
                expire_time = expires.group(1) if expires else "Not Specified"
                domain_name = domain.group(1) if domain else "Not Specified"
                cookie_pool.append(f"Cookie: {name} (Expires: {expire_time}, Domain: {domain_name})")
                
        return cookie_pool
    
    def is_password_portect(self,response : str) -> bool:
        """
        Check if the target site is password-protected.
        Args:
            response (str): HTTP response from server.

        Raises:
            RuntimeError: Raise if input response invalid.

        Returns:
            bool: Return True if target site is password-protected. 
            Else return False.
        """
        if type(response) != str:
            raise RuntimeError("RuntimeError: the input response is not a valid type")

        status_code = response.split()[1]
        if status_code in ('401') or 'WWW-Authenticate' in response:
            return True
        else:
            return False
    
    def is_support_h2(self) -> bool:
        """
        Check if the target site is support Http2.
        Returns:
            bool: Return True if it does.
            Else return False.
        """
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2', 'http/1.1'])
        ssl_soc = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),server_hostname=self.host)
        ssl_soc.connect((self.host, self.port))
        if ssl_soc.selected_alpn_protocol() != None:
            if 'h2' in ssl_soc.selected_alpn_protocol():
                ssl_soc.close()
                return True
            else:
                ssl_soc.close()
                return False
        ssl_soc.close()
        return False
                
    def connect(self):
        """
        Main connect and control of SmartClient.
        """
        request = f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n"
        if self.port == 443:
            ssl_soc = self.generate_connection()
            
            try:
                ssl_soc.sendall(request.encode(encoding="UTF-8", errors="ignore"))
            except (ssl.SSLError,socket.error,OSError) as e:
                print(f"Faild to send: {e}")
            except Exception as e:
                print(f"Unexpected Error: {e}")
            
            response = ssl_soc.recv(4096).decode()               
            ssl_soc.close
        else:
            soc = self.generate_defalt_connecton()
            soc.send(request.encode())
            response = soc.recv(4096).decode()
            soc.close()
            
            
        
        if self.handle_redirect(response):
            return self.connect()
        
        cookie_pool = self.handle_cookies(response)
        
        self.print_all(response,request,cookie_pool)
        
    def print_all(self,response:str,request:str,cookie_pool):
        print("---Request begin---")
        print(request)
        print("---Request end---")
        print("HTTP request sent, awaiting response...")
        print("\n")
        print("---Response header ---")
        start_at = response.find("\r\n\r\n")
        print(response[:start_at])
        print("\n")
        print("--- Response body ---")
        print(response[start_at+4:])
        print("\n")
        print("--- Final output ---")
        print(f"website: {self.host}")
        print(f"1. Supports http2: {'yes' if self.is_support_h2() else 'no'}")
        print(f"2. List of Cookies:")
        if cookie_pool:
            for cookie in cookie_pool:
                print(cookie)
        else:
            print("No cookie exist")
        print(f"3. Password-protected: {'yes' if self.is_password_portect(response) else 'no'}")
        
        
        
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        client = SmartClient("https://docs.engr.uvic.ca/docs/", 80)
        client.connect()
    else:
        client = SmartClient(sys.argv[1])
        client.connect()
    