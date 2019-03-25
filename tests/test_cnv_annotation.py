"""Test the annotation of CNVs"""
import unittest

from lib.tad import Tad
from lib.gene import Gene
from lib.enhancer import Enhancer
import lib.utils as utils

class TadAnnotationTest(unittest.TestCase):
    """Test class for the annotation of CNVs"""

    def test_annotation(self):
        tad_beds = utils.objects_from_file('tests/test_data/test_tads.bed', 'TAD')
        enhancer_beds = utils.objects_from_file('tests/test_data/test_enhancer.bed', 'Enhancer',['ID'])
        gene_beds = utils.objects_from_file('tests/test_data/test_genes.bed', 'Gene',['name'])

        # create dict with chromsomes as keys
        gene_dict = utils.create_chr_dictionary_from_beds(gene_beds)
        enhancer_dict = utils.create_chr_dictionary_from_beds(enhancer_beds)
        tad_dict = utils.create_chr_dictionary_from_beds(tad_beds)

        # Annotate TADs with overlapping enhancer and genes
        annotated_tads = utils.create_annotated_tad_dict(tad_dict, gene_dict, enhancer_dict)

        #load cnvs
        cnv_beds = utils.objects_from_file("tests/test_data/test_cnv.bed", 'cnv')

        #create cnv dict
        cnv_dict = utils.create_chr_dictionary_from_beds(cnv_beds)

        #annotate cnvs
        annotated_cnvs = utils.annotate_cnvs(annotated_tads,cnv_dict)

        self.assertEqual(len(annotated_cnvs['chr2'][0].tads),1,'Annotation of TADs does not work!')
        self.assertEqual(annotated_cnvs['chr1'][0].tads[0].count_genes(),2,'Genes are not transferred to the CNV object!')