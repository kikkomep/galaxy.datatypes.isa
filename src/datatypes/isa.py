"""
ISA datatype

See http://isa-tools.org

"""

from __future__ import print_function

import os
import sys
import logging
import tarfile

from galaxy.datatypes import data
from galaxy.datatypes import metadata

# logger
logger = logging.getLogger("galaxy.jobs.runners.local")

# create a file handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


class Isa(data.Text):
    """Tab delimited data in foo format"""
    file_ext = "isa"
    # edam_format = "format_2331"
    # composite_type = 'auto_primary_file'
    composite_type = 'basic'
    allow_datatype_change = False
    is_binary = False

    # metadata.MetadataElement(name="base_name", desc="base name isa tab dataset",
    #                          default='Text',
    #                          readonly=True, set_in_upload=True)

    def __init__(self, **kwd):
        data.Text.__init__(self, **kwd)
        # logger.info("The current dataset: ", self.__dict__.keys())
        # print(self)
        # print(kwd, file=sys.stderr)
        # logger.info("Dataset ISA options: %s", kwd)
        # self.add_composite_file("*.txt", description="Investigation file")
        # self.add_composite_file("archive.tar.gz", description="Investigation file")

        # self.add_composite_file('i_investigation.txt', mimetype='text/plain')
        # self.add_composite_file('archive',
        #                         description='ISA Archive',
        #                         # substitute_name_with_metadata='base_name',
        #                         is_binary=True)
        # self.add_composite_file('%s.map',
        #                         description='Map File',
        #                         substitute_name_with_metadata='base_name',
        #                         is_binary=False)

        # for k, n in self.composite_files.items():
        #     print("%s --> %s" % (k, n))
        # self.add_composite_file("%s.txt", description="Investigation file", substitute_name_with_metadata='base_name',
        #                         is_binary=False)
        # self.add_composite_file("prova.txt", description="Prova file")

    def generate_primary_file(self, dataset=None):
        logger.info("Dataset type: %s, keys=%s, values=%s", type(dataset), dataset.keys(), dataset.values())

        rval = ['<html><head><title>Wiff Composite Dataset </title></head><p/>']
        rval.append('<div>This composite dataset is composed of the following files:<p/><ul>')

        # with tarfile.open(dataset.get("datatype").primary_file_name, "r") as tar:
        #     for tarinfo in tar:
        #         logger.info(tarinfo.name, tarinfo.size)

        for composite_name, composite_file in self.get_composite_files(dataset=dataset).items():
            fn = composite_name
            opt_text = ''
            if composite_file.optional:
                opt_text = ' (optional)'
            if composite_file.get('description'):
                rval.append('<li><a href="%s" type="text/plain">%s (%s)</a>%s</li>' % (
                    fn, fn, composite_file.get('description'), opt_text))
            else:
                rval.append('<li><a href="%s" type="text/plain">%s</a>%s</li>' % (fn, fn, opt_text))
        rval.append('</ul></div></html>')
        return "\n".join(rval)

    def sniff(self, filename):
        print("Checking if it is an ISA: %s" % filename)
        return True

    def validate(self, dataset):
        print("Validating dataset....")
        return super(Isa, self).validate(dataset)

    def set_meta(self, dataset, **kwd):
        #logger.info("Setting metadata of ISA type: %s", dataset.file_name)
        print("Setting metadata of ISA type: %s" % dataset.file_name)
        # raise Error("Setting metadata of ISA type")
        super(Isa, self).set_meta(dataset, **kwd)

#        with tarfile.open(dataset.file_name, "r:gz") as tar:
#            for tarinfo in tar:
#                print("file: %s (%s)" % (tarinfo.name, tarinfo.size))

    def write_from_stream(self, dataset, stream):
        print("Writing Dataset type: %s, keys=%s, values=%s, type_stream=%s", type(dataset), dataset.keys(),
              dataset.values(), type(stream))
        # tar = tarfile.TarFile(fileobj=stream, mode="r:gz")
        # # with tarfile.open(fileobj=stream, mode="r:gz") as tar:
        # for tarinfo in tar:
        #     logger.info(tarinfo.name, tarinfo.size)
        #
        # tar.close()
        # logger.info(type(self.get_raw_data(dataset)))
        super(Isa, self).write_from_stream(dataset, stream)

    def split(cls, input_datasets, subdir_generator_function, split_params):
        print("Splitting")
	super(Isa, cls).split(input_datasets, subdir_generator_function, split_params)

    def set_raw_data(self, dataset, data):
        print("Setting raw data")
        super(Isa, self).set_raw_data(dataset, data)

    def _archive_main_file(self, archive, display_name, data_filename):
        print("Archiving the main file: %s" % data_filename)
        return super(Isa, self)._archive_main_file(archive, display_name, data_filename)

    def _archive_composite_dataset(self, trans, data=None, **kwd):
        print("Archiving the composite dataset")
        return super(Isa, self)._archive_composite_dataset(trans, data, **kwd)
