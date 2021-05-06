import argparse
import sys
import vcfpy
import csv
from collections import OrderedDict

def to_array(dictionary):
    array = []
    for key, value in dictionary.items():
        array.append("{}|{}".format(key, value))
    return sorted(array)

def parse_tsv_file(args):
    values={}
    with open(args.values_file,'r') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        for row in tsvin:
            if any(x.strip() for x in row): #skip blank lines
                values[(row[0] + ":" + row[1])] = row[2]
    return values


def create_vcf_reader(args):
    vcf_reader = vcfpy.Reader.from_path(args.input_vcf)
    if 'MQ0' in vcf_reader.header.format_ids():
        print("FORMAT already contains a MQ0 field. It's value will be overwritten when matches are found")
    if 'MQ0FRAC' in vcf_reader.header.format_ids() :
        print("FORMAT already contains a MQ0FRAC field. It's value will be overwritten when matches are found")
    return vcf_reader

def create_vcf_writer(args, vcf_reader):
    if args.output_vcf:
        output_file = args.output_vcf
    else:
        (head, sep, tail) = args.input_vcf.rpartition('.vcf')
        output_file = ('').join([head, '.info.vcf', tail])

    new_header = vcf_reader.header.copy()

    if not 'MQ0' in vcf_reader.header.format_ids():
        od = OrderedDict([('ID', 'MQ0'), ('Number', '1'), ('Type', 'Float'), ('Description', 'Number of MAPQ == 0 reads covering this site in the tumor')])
        new_header.add_format_line(od)
    if not 'MQ0FRAC' in vcf_reader.header.format_ids():    
        od2 = OrderedDict([('ID', 'MQ0FRAC'), ('Number', '1'), ('Type', 'Float'), ('Description', 'Fraction of MAPQ == 0 reads covering this site in the tumor')])
        new_header.add_format_line(od2)
    if not 'MQ0FRAC' in vcf_reader.header.filter_ids():    
        od3 = OrderedDict([('ID', 'MAPQ0'), ('Description', 'Site exceeds {} fraction of reads with mapping quality zero'.format(args.mq0frac_threshold))])
        new_header.add_filter_line(od3)

    return vcfpy.Writer.from_path(output_file, new_header)

def define_parser():
    parser = argparse.ArgumentParser(
        "vcf-mapq-filter",
        description = "A tool that will add mapping quality data from a tab-delimited file to a MQ0 field" +
                      "field in VCF INFO column, then apply a filter to sites with greater than a" +
                      "specified fraction of reads with MAPQ0 in the tumor sample."
    )

    parser.add_argument(
        "input_vcf",
        help="A VCF file"
    )
    parser.add_argument(
        "values_file",
        help="A TSV file containing three columns: chromosome, position, value"
    )
    parser.add_argument(
        "sample_name",
        help="The sample name from which the MQ0 values were extracted. Expected to have a DP value"
    )
    parser.add_argument(
        "mq0frac_threshold",
        help="lines with MQ0FRAC above this value will be labeled MAPQ0 in the FILTER field"
    )
    parser.add_argument(
        "output_vcf",
        help="Path to write the output VCF file"
    )
    return parser

def main(args_input = sys.argv[1:]):
    parser = define_parser()
    args = parser.parse_args(args_input)

    vcf_reader  = create_vcf_reader(args)
    vcf_writer = create_vcf_writer(args, vcf_reader)

    values = parse_tsv_file(args)

    for entry in vcf_reader:
        if "MQ0" not in entry.FORMAT:
            if isinstance(entry.FORMAT, tuple):
                entry.FORMAT = ["MQ0"]
            else:
                entry.FORMAT.append('MQ0')
        if "MQ0FRAC" not in entry.FORMAT:
            if isinstance(entry.FORMAT, tuple):
                entry.FORMAT = ["MQ0FRAC"]
            else:
                entry.FORMAT.append('MQ0FRAC')

        if entry.CHROM + ":" + str(entry.POS) in values:
            mq0frac = float(values[entry.CHROM + ":" + str(entry.POS)])/float(entry.call_for_sample[args.sample_name].data['DP'])
            entry.call_for_sample[args.sample_name].data['MQ0'] = values[entry.CHROM + ":" + str(entry.POS)]
            entry.call_for_sample[args.sample_name].data['MQ0FRAC'] = round(mq0frac,4)
            if mq0frac > float(args.mq0frac_threshold):
                entry.add_filter('MAPQ0')
                
        vcf_writer.write_record(entry)

    vcf_reader.close()
    vcf_writer.close()

if __name__ == '__main__':
    main()
