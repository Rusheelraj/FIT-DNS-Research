# Implementing DNSSEC using bind9. 

## Installation:

### Install Bind9 Server:

``` 
$ sudo apt update 
$ sudo apt install bind9 bind9utils bind9-doc dnsutils
```

## Configure the DNS Zone:

### Edit the named configuration file (named.conf.local) to configure the DNS zone:

``` $ sudo nano /etc/bind/named.conf.local ```

Here, I am creating a sample zone called "adam". You are free to give the name you wish.  

Add the following configuration:

```
    zone "adam" {
    type master;
    file "/etc/bind/zones/db.adam";  # zone file path
    allow-transfer { none; };  # disable zone transfers
};

```

Save and exit the editor.

## Creating the Zone File:

### Create a directory for your zone files (if it doesn't already exist), and create the zone file:

``` $ sudo mkdir /etc/bind/zones ```

``` $ sudo nano /etc/bind/zones/db.adam ```

Add your DNS records:

```
$TTL 604800
@ IN SOA ns.adam. admin.adam. (
  2023062001 ; serial number
  604800     ; refresh
  86400      ; retry
  2419200    ; expire
  604800 )   ; negative cache TTL

; name servers
adam. IN NS ns.adam.

; A records for name servers
ns IN A 192.0.2.1  ; replace with your server's IP

; additional records
www IN A 192.0.2.1  ; replace with your server's IP

```

Save and exit the editor.

## Generate the Keys:

### Generate the Key Signing Key (KSK) and Zone Signing Key (ZSK) for your domain:

``` $ cd /etc/bind/zones ```

Note: The Zone name much match zone name specified in /etc/bind/named.conf.local

``` $ dnssec-keygen -a RSASHA256 -b 2048 -n ZONE -K . adam  # KSK ```

``` $ dnssec-keygen -a RSASHA256 -b 1024 -n ZONE adam  # ZSK ```

If there isn't any output, that means the keys were generated successfully. It should generate 4 files, 2 files with .private and 2 files with .key. Each belongs to KSK and ZSK respectively. 

The generated keys should be like:

```
Kadam.+008+17088.key  Kadam.+008+17088.private
Kadam.+008+48016.key  Kadam.+008+48016.private

```
Before signing the zone, include the keys in db.adam file present in /etc/bind/zones.

``` $ sudo db.adam ```

Once you generate the keys, you should be including the keys in the db.adam file.

```
$TTL 604800
@ IN SOA ns.adam. admin.adam. (
  2023062001 ; serial number
  604800     ; refresh
  86400      ; retry
  2419200    ; expire
  604800 )   ; negative cache TTL

; name servers
adam. IN NS ns.adam.

; A records for name servers
ns IN A 192.0.2.1  ; replace with your server's IP

; additional records
www IN A 192.0.2.1  ; replace with your server's IP

; The below are additional records where I am including the generated keys

$INCLUDE Kadam.+008+17088.key ;
$INCLUDE Kadam.+008+48016.key ; 

```

## Sign the Zone:
### Sign the zone using these keys:

``` $ dnssec-signzone -A -3 $(head -c 1000 /dev/random | sha1sum | cut -b 1-16) -N INCREMENT -o adam -t db.adam ```

## Update Zone Configuration:

### Edit the named.conf.local file again to use the signed zone file:

``` $ sudo nano /etc/bind/named.conf.local ```

### Update the file path in the zone block:

```
    zone "adam" {
    type master;
    file "/etc/bind/zones/db.adam.signed";  # updated file path
    allow-transfer { none; };
};

```
Save and exit the editor.

## Configure DNSSEC Validation:
### Edit the named.conf.options file:

``` $ sudo nano /etc/bind/named.conf.options ```

Set dnssec-validation line to auto, and auth-nxdomain line to no:

```
    options {
    directory "/var/cache/bind";

    dnssec-validation auto;

    auth-nxdomain no;
};

```
Save and exit the editor.

Restart the Bind9 service:

``` $ sudo service bind9 restart ```

## Testing:
Once you have set up DNSSEC, you can test it using dig. Here's how you can use dig to check your DNSSEC configuration for the domain "adam":

``` $ dig @localhost adam. SOA +dnssec ```

Expected output should be like:

```
; <<>> DiG 9.16.1-Ubuntu <<>> @localhost adam. SOA +dnssec
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 22372
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags: do; udp: 4096
; COOKIE: 9fa35794b38e6d2f0100000064a19f9ae328a2b937039f63 (good)
;; QUESTION SECTION:
;adam.				IN	SOA

;; ANSWER SECTION:
adam.			604800	IN	SOA	ns.adam. admin.adam. 2023062002 604800 86400 2419200 604800
adam.			604800	IN	RRSIG	SOA 8 1 604800 20230721180115 20230621180115 17088 adam. Qcix2dMig1ea4MLLDVeCrIBhYzdGnY+hyy/RZx2sGi7z5eyOQ+iwbnwm utZcVsEEyBJDas9fTAiqszbw61yD95YMgx4ve7/B4eXOaVKMNPQM8Yry 1DbOx02MOK48K9C6HQhxp3XicLsyQgdtcRJWLrpV17fwuL91vuWL1GGb DKQ=

;; Query time: 0 msec
;; SERVER: 127.0.0.1#53(127.0.0.1)
;; WHEN: Sun Jul 02 12:02:34 EDT 2023
;; MSG SIZE  rcvd: 270


```
Using kdig by querying fit.edu:

Install kdig by using the below command: 

``` $ sudo apt install knot-dnsutils ```

Once installed, we can use kdig/dig to query a website using our newly created DNSSEC.

``` $ kdig @localhost +dnssec fit.edu ```

Expected output should be like:

```
;; ->>HEADER<<- opcode: QUERY; status: NOERROR; id: 1643
;; Flags: qr rd ra; QUERY: 1; ANSWER: 1; AUTHORITY: 0; ADDITIONAL: 1

;; EDNS PSEUDOSECTION:
;; Version: 0; flags: do; UDP size: 4096 B; ext-rcode: NOERROR

;; QUESTION SECTION:
;; fit.edu.            		IN	A

;; ANSWER SECTION:
fit.edu.            	3207	IN	A	18.215.123.220

;; Received 52 B
;; Time 2023-07-02 12:08:52 EDT
;; From 127.0.0.1@53(UDP) in 0.2 ms

```
In the output, we can observe the 'do' flag is set, meaning that it has used DNSSEC while quering. 

We can also analyse the packet using Wireshark:

Install Wireshark:

``` $ sudo apt install wireshark -y ```

![image](https://github.com/Rusheelraj/FIT-DNS-Research/assets/30828807/866a8d3c-eebf-46b6-9dce-8e209ad509cc)


Capture the traffic and analyse it. Once you see the packet, we can observe in 'Additional Records', that the

In the output, you're looking for the ad flag, which indicates that DNSSEC validation was successful. You should see it in the flags section of the output, like this: ;; flags: qr aa rd ra ad; QUERY: 1, ANSWER: 2, AUTHORITY: 1, ADDITIONAL: 1.

Also, check for the RRSIG records in the answer section of the output, which indicate that the record has been signed using DNSSEC.

Note: Replace localhost with the IP address of your DNS server if you are testing from a different machine. Also replace "adam" with your actual domain name if it's different.
