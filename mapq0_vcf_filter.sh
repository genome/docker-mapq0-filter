#!/bin/bash
set -e

# arguments
outdir=$1
vcf=$2
bam=$3
mapq0perc=$4
sample_name=$5

# for each variant
# define number of reads with MAPQ=0 
zgrep -v "^#" "$vcf" | cut -f 1,2 | while read chr pos;do
    pysamstats --type mapq --chromosome $chr --start $pos --end $((pos+1)) "$bam"  | grep $pos | cut -f 1,2,5 >>$outdir/mapq0counts
done


if [[ ! -z $outdir/mapq0counts ]];then
    #process each line, add MQ0 and MQ0PERC values to the right sample, and add MAPQ0 filter when needed
    python3 /usr/bin/add_mq0_and_filter.py $vcf $outdir/mapq0counts $sample_name $mapq0perc $outdir/mapq_filtered.vcf.gz
else
    #no sites to process, just make a copy of the (empty) vcf.
    #handle both gzipped and unzipped vcfs
    echo "There is no variant to process. The input VCF file will be copied."
    if [[ ${vcf: -3} == ".gz" ]];then 
        cp $vcf $outdir/mapq_filtered.vcf.gz
    else
        gzip -c $vcf > $outdir/mapq_filtered.vcf.gz
    fi
fi
