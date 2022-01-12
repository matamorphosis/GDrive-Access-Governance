#----------------------------------------------------------------------------------------------------
# Pull latest stable Ubuntu
#----------------------------------------------------------------------------------------------------
FROM ubuntu:20.04
LABEL org.opencontainers.image.source="https://github.com/matamorphosis/GDAG"
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Update repos and install required packages
#----------------------------------------------------------------------------------------------------
RUN apt update
ARG DEBIAN_FRONTEND=noninteractive
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Change region as required and install packages
#----------------------------------------------------------------------------------------------------
ENV TZ=Australia/Sydney
RUN apt install -y tzdata python3 python3-pip build-essential git openssl curl sudo
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Clone repository and create necessary directories
#----------------------------------------------------------------------------------------------------
WORKDIR /
RUN git clone https://github.com/matamorphosis/GDrive-Access-Governance
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Install online packages from requirements.txt file
#----------------------------------------------------------------------------------------------------
RUN pip3 install -r /GDrive-Access-Governance/installation/requirements.txt
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Change below to production for production environment
#----------------------------------------------------------------------------------------------------
ENV FLASK_ENVIRONMENT="development"
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Set up certificates
#----------------------------------------------------------------------------------------------------
RUN mkdir /GDrive-Access-Governance/certs
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# To provide your own, uncomment the following lines, and provide .key and .crt file pair in the same directory as this dockerfile before running.
#----------------------------------------------------------------------------------------------------
# ADD ./privateKey.key /GDrive-Access-Governance/certs/privateKey.key
# ADD ./certificate.crt /GDrive-Access-Governance/certs/certificate.crt
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# If using the above conditions to add custom a certificate pair, please ensure the names are correctly reflected below:
#----------------------------------------------------------------------------------------------------
ENV PRIVATE_KEY="/GDrive-Access-Governance/certs/privateKey.key"
ENV CERTIFICATE_CRT="/GDrive-Access-Governance/certs/certificate.crt"
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# If using the above conditions to add custom a certificate pair, please comment out the below lines
#----------------------------------------------------------------------------------------------------
ENV country=AU
ENV state=NSW
ENV locality=Sydney
ENV commonname=GDAG
ENV organization=GDAG
ENV organizationalunit=GDAG
ENV email=GDAG@GDAG.com
#----------------------------------------------------------------------------------------------------

RUN openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout $PRIVATE_KEY -out $CERTIFICATE_CRT -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"

#----------------------------------------------------------------------------------------------------
# Expose TCP port 8000 from container to host, and ensure postgresql is started and start GDAG.
#----------------------------------------------------------------------------------------------------
EXPOSE 8000
RUN chmod +x /GDrive-Access-Governance/installation/docker/start.sh
CMD /GDrive-Access-Governance/installation/docker/start.sh
#----------------------------------------------------------------------------------------------------