DNS over HTTPS (DoH) encrypts DNS queries, which traditionally are sent in plain text, making them unreadable to anyone except the client and the server. This ensures greater privacy for users. To set up a DoH server on Ubuntu using Nginx and OpenSSL, follow the steps below:

Update Your System:
Before beginning any major installation, it's a good idea to update your system's default applications.

$ sudo apt update && sudo apt upgrade -y

Install and Configure Unbound (DNS Resolver):
Unbound is a lightweight, secure DNS resolver. Install it and set up a basic configuration.

$ sudo apt install unbound

Configure Unbound by editing the configuration file located at /etc/unbound/unbound.conf. You can use a text editor like nano.

$ sudo nano /etc/unbound/unbound.conf

Here's a basic configuration to get you started:

server:
  interface: 127.0.0.1
  access-control: 127.0.0.0/8 allow
  hide-identity: yes
  hide-version: yes
  
Restart Unbound to apply the changes.

$ sudo systemctl restart unbound

Install Nginx:
Nginx will serve as the HTTPS proxy for your DoH server.

$ sudo apt install nginx

Generate a Self-Signed SSL Certificate using OpenSSL.
OpenSSL is a robust, full-featured open-source toolkit that implements the Secure Sockets Layer (SSL) and Transport Layer Security (TLS) protocols.

$ sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt

Fill in the prompts appropriately. The most important line is the one that requests the Common Name (e.g. server FQDN or YOUR name). You need to enter the domain name associated with your server or, in this case, you can simply type localhost.

Install DoH Proxy:

You'll need a software to translate between HTTP and DNS. You can use doh-proxy, a fast and secure DoH proxy written in Rust.

First, install Rust:

$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
$ source $HOME/.cargo/env

Then, install doh-proxy:
$ cargo install doh-proxy

Configure Nginx:

Edit the Nginx configuration file for your site (found in /etc/nginx/sites-available/) to include a section for the DoH proxy. This might look something like this:


server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;

    ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
    ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;

    server_name localhost;

    location /dns-query {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

Save and exit the text editor, then test the configuration and restart Nginx.

$ sudo nginx -t
$ sudo systemctl restart nginx

Start DoH Proxy:

Run doh-proxy, specifying the address of your DNS resolver:

$ doh-proxy --upstream '127.0.0.1:53'

Your DoH server should now be up and running. It is set up to use the self-signed SSL certificate, so if you navigate to https://localhost/dns-query in your browser, you'll get a security warning. This is because your browser does not trust the self-signed certificate. However, the communication will be encrypted.





