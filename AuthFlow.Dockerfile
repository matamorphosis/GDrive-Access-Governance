#----------------------------------------------------------------------------------------------------
# Pull latest stable Ubuntu
#----------------------------------------------------------------------------------------------------
FROM ubuntu:20.04
LABEL org.opencontainers.image.source="https://github.com/matamorphosis/GDAG-Auth-Flow"
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
RUN apt update
RUN apt install -y tzdata python3 python3-pip curl ncat
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Clone repository and create necessary directories
#----------------------------------------------------------------------------------------------------
WORKDIR /
COPY ./ /
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Install online packages from requirements.txt file
#----------------------------------------------------------------------------------------------------
RUN pip3 install -r /installation/requirements.txt
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------
# Start GDAG Auth Flow Server
#----------------------------------------------------------------------------------------------------
RUN chmod +x /installation/docker/*start.sh
WORKDIR /app
CMD ["bash", "/installation/docker/auth-flow-start.sh"]
#----------------------------------------------------------------------------------------------------