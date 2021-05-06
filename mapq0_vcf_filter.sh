#!/bin/bash
set -e

outvcf=$1
vcf=$2
bam=$3
mapq0perc=$4
sample_name=$5
outdir=$(dirname "$outvcf")

count=0;
zgrep -v "^#" "$vcf" | cut -f 1,2 | while read chr pos;do
    pysamstats --type mapq --chromosome $chr --start $pos --end $((pos+1)) "$bam"  | grep $pos | cut -f 1,2,5 >>$outdir/mapq0counts
    count=$((count+1))
done


if [[ $count -eq 0 ]];then
    #no sites to process, just make a copy of the (empty) vcf.
    #handle both gzipped and unzipped vcfs
    if [[ ${vcf: -3} == ".gz" ]];then 
        gunzip -c $vcf > $outdir/mapq_filtered.vcf.gz
    else
        cp $vcf $outdir/mapq_filtered.vcf.gz
    fi
else 
    #process each line, add MQ0 and MQ0PERC values to the right sample, and add MAPQ0 filter when needed
    python3 /usr/bin/add_mq0_and_filter.py $vcf mapq0counts $sample_name mapq0perc $outdir/mapq_filtered.vcf.gz
fi
