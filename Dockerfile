FROM griffithlab/vatools:3.0.1

LABEL \
    description="tools needed for mapq0 filter"

##########
#GATK 3.6#
##########
RUN apt-get update -y && apt-get install -y \
    apt-utils \
    bzip2 \
    default-jre \
    libbz2-dev \
    liblzma-dev \
    wget \
    zlib1g-dev

RUN cd /tmp/ \
    && wget -O /tmp/gatk3.6.tar.bz2 'https://storage.googleapis.com/gatk-software/package-archive/gatk/GenomeAnalysisTK-3.6-0-g89b7209.tar.bz2' \
    && tar xf gatk3.6.tar.bz2 \
    && cp GenomeAnalysisTK.jar /opt/GenomeAnalysisTK.jar \
    && rm -rf /tmp/*

##############
#mapq0 filter
##############
COPY mapq0_vcf_filter.sh /usr/bin/mapq0_vcf_filter.sh
RUN chmod +x /usr/bin/mapq0_vcf_filter.sh
RUN pip3 install pysam==0.15.4
RUN pip3 install pysamstats==1.1.2
