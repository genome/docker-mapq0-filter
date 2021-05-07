FROM griffithlab/vatools:4.1.0

LABEL \
    description="tools needed for mapq0 filter"

RUN apt-get update -y && apt-get install -y \
    apt-utils \
    bzip2 \
    libbz2-dev \
    liblzma-dev \
    zlib1g-dev

COPY mapq0_vcf_filter.sh /usr/bin/mapq0_vcf_filter.sh
COPY add_mq0_and_filter.py /usr/bin/add_mq0_and_filter.py
RUN chmod +x /usr/bin/mapq0_vcf_filter.sh /usr/bin/add_mq0_and_filter.py
RUN pip3 install cython==0.29.19
RUN pip3 install pysam==0.15.4
RUN pip3 install pysamstats==1.1.2
