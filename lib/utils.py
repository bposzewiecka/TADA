"""Helper functions to parse BED files."""
# standart libraries
import pathlib
import json

# own libraries
from .bed import Bed
from .bed_class import BedClass


def objects_from_file(path, cls_string, column_names=[]):
    """Load a BED file and return a list of Bed objects""
    Args:
        path: Path to the BED file.
        cls_string: A string that matches one of the bed classes (e.g. Gene).
    """
    path = validate_file(path)
    bed_class = BedClass.from_str(cls_string).get_class()
    return [bed_class(line, column_names) for line in path.open()]


def validate_file(path):
    "Check if the path is a valid BED file and return a pathlib.Path object."
    path = pathlib.Path(path)

    # check if path is a valid file
    if not path.is_file():
        raise Exception(f'{path} is not a valid path')

    # check if path is a bed or txt file
    # TODO this is just prelimenary check
    if not (path.suffix == '.bed' or path.suffix == '.txt'):
        raise Exception(f'{path} is not a BED or tab-delimeted TXT file')

    return path


def create_chr_dictionary_from_beds(beds: [Bed]):
    """Create a dictionary based on bed objects with the chromsomes as keys."""
    bed_dict = {}
    for bed in beds:
        if not bed.chr in bed_dict:
            bed_dict[bed.chr] = [bed]
            continue
        bed_dict[bed.chr].append(bed)
    bed_dict = {key: sorted(bed_dict[key]) for key in bed_dict}
    return bed_dict


def is_in(bed_list, reference_bed):
    """Returns True if the first element of the list of bed objects is in the reference_bed"""
    # return False if the list of bed objects contains no element
    if not bed_list:
        return False

    # check if the first element is in the reference bed object
    if bed_list[0].start < reference_bed.end:
        return True
    else:
        return False


def reduce_dict(dictionary, keys):
    """Returns a dictionary containing only the input keys"""
    return {key: (dictionary[key] if key in dictionary else []) for key in keys}


def create_annotated_dict(tad_dict, gene_dict, enhancer_dict):
    """Annotates every TAD with the overlapping genes and enhancers.
    For each TAD in a chromosome the function iterates through the sorted gene and enhancer lists as long as the
    start position of either the first gene or first enhancer is less than the end position of the TAD.
    If one of the elements satisfies this condition there are three options:
        1. The element starts in or before the TAD and ends in the TAD -> Add to TADs elements and remove element from the list.
        2. The element starts in or before the TAD and does not in the TAD -> Add to TAD elements but keep it for other TADs.
        3. The element does not start before or in the TAD -> Leave the list as it is.
    """
    # reduce genes and enhancers to chromsomes were tads are available
    gene_dict, enhancer_dict = [reduce_dict(
        dictionary, tad_dict.keys()) for dictionary in [gene_dict, enhancer_dict]]

    # iterate through chromsomes
    for chrom in tad_dict:
        for tad in tad_dict[chrom]:
            gene_queue = []
            enhancer_queue = []
            while is_in(gene_dict[chrom], tad) or is_in(enhancer_dict[chrom], tad):
                if is_in(gene_dict[chrom], tad):
                    if gene_dict[chrom][0].end <= tad.end:
                        tad.genes.append(gene_dict[chrom].pop(0))
                    elif gene_dict[chrom][0].end > tad.end:
                        tad.genes.append(gene_dict[chrom][0])
                        gene_queue.append(gene_dict[chrom].pop(0))

                if is_in(enhancer_dict[chrom], tad):
                    if enhancer_dict[chrom][0].end <= tad.end:
                        tad.enhancer.append(enhancer_dict[chrom].pop(0))
                    elif enhancer_dict[chrom][0].end > tad.end:
                        tad.enhancer.append(enhancer_dict[chrom][0])
                        enhancer_queue.append(enhancer_dict[chrom].pop(0))

            enhancer_dict[chrom] = enhancer_queue + enhancer_dict[chrom]
            gene_dict[chrom] = gene_queue + gene_dict[chrom]
    return tad_dict
