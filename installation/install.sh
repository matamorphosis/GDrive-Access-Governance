#!/bin/bash
if [[ $EUID -ne 0 ]]; then
    echo "[-] This script must be run as root." 
    exit 0
else
    apt update
    apt install python3 python3-pip -y

    pip3 install -r requirements.txt
    mkdir ../certs
    PRIVATE_KEY="../certs/privateKey.key"
    CERTIFICATE_CRT="../certs/certificate.crt"
    #Change to your company details
    country=AU
    state=NSW
    locality=Sydney
    commonname=`domainname`
    organization=Scrummage
    organizationalunit=Scrummage
    email=Scrummage@Scrummage.com

    if [ -z $commonname ]
    then
        commonname=Scrummage
    fi

    openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout $PRIVATE_KEY -out $CERTIFICATE_CRT -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"
    chown -R $SUDO_USER:$SUDO_USER ../certs
fi