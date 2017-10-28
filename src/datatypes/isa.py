"""
ISA datatype

See http://isa-tools.org


Notes.
======

Apparently this class is marginally used during the upload process;
indeed it is the uploader tool that takes care of uploading and placing the raw data of the dataset
to the final destination on the Galaxy data folders.
The only method which is called is the `set_meta(...)` which contains the reference to the filname
of the already uploaded dataset (property `filename` of the `dataset` parameter).

At the moment, a reasonable strategy to support ISA datatypes might be the following:

    * define a composite datatype:
        this allows us to associate all the ISA files of a dataset
        to a dedicated subdirectory which Galaxy composite datatypes use to host their files;

    * update the existing Galaxy uploader (or create a new uploader tool) to properly handle
        the initialization of the new datatype during its upload,
        i.e., given a zip ISA dataset, the uploader should extract all its files to the subfolder mentioned above

With this kind of implementation it becomes very simple to pass a dataset constituted by more than one file
to a Galaxy tool: it can be done using the `extra_files_path` property of the input parameter.

    Example of tool command:
    -----------------------
    ```<command interpreter="python">isa-test.py ${input} ${input.extra_files_path} $output</command>```
    -----------------------------------------------------------------------------------------------------

"""

from __future__ import print_function

import os
import sys
import glob
# import zipfile
import logging
import tarfile
import tempfile
import shutil

from isatools import isatab  # depends on https://github.com/ISA-tools/isa-api/tree/py2_isatools-lite 62fb5f0

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


class Isa(data.Data):
    """Tab delimited data in foo format"""
    file_ext = "isa"
    composite_type = 'basic'  # 'auto_primary_file'
    allow_datatype_change = False
    is_binary = True

    # metadata.MetadataElement(name="base_name", desc="base name isa tab dataset",
    #                          default='Text',
    #                          readonly=True, set_in_upload=True)

    def __init__(self, **kwd):
        data.Data.__init__(self, **kwd)

    def get_primary_filename(self, files_path):
        """ Use the `investigation` file as primary"""
        investigation_file_pattern = "i_*.txt"  # TODO: check pattern to identify the investigation file
        res = glob.glob(os.path.join(files_path, investigation_file_pattern))
        if len(res) > 0:
            if len(res) == 1:
                return res[0]
            print("More than one file match the pattern '%s' "
                  "to identify the investigation file" % investigation_file_pattern)
        return None

    def write_from_stream(self, dataset, stream):
        # TODO: check if the actual file is really a TAR archive
        # extract the archive to a temp folder
        tmp_folder = tempfile.mkdtemp()
        print("Using the custom uploader")
        with tarfile.open(fileobj=stream) as tar:
            for tarinfo in tar:
                print("File name: %s " % tarinfo.name)
            tar.extractall(path=tmp_folder)

        # FIXME: update this logic with a better implementation
        tmp_files = os.listdir(tmp_folder)
        if len(tmp_files) > 0:
            first_path = os.path.join(tmp_folder, tmp_files[0])
            if os.path.isdir(first_path):
                shutil.move(os.path.join(tmp_folder, tmp_files[0]), dataset.files_path)
            else:
                shutil.move(tmp_folder, dataset.files_path)
        else:
            print("No files found within the temp folder!!!!")

        primary_filename = self.get_primary_filename(dataset.files_path)
        if primary_filename is None:
            raise Exception("Unable to find the investigation file!!!")

        print("Primary (investigation) filename: %s" % primary_filename)
        shutil.copy(os.path.join(dataset.files_path, primary_filename), dataset.file_name)

        print("All files saved!!!")

    def generate_primary_file(self, dataset=None):
        print("Dataset type: %s, keys=%s, values=%s", type(dataset), dataset.keys(), dataset.values())

        rval = ['<html><head><title>Wiff Composite Dataset </title></head><p/>']
        rval.append('<div>This composite dataset is composed of the following files:<p/><ul>')

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
        logger.info("Checking if it is an ISA: %s" % filename)
        return True

    def validate(self, dataset):
        print("Validating dataset....")
        return super(Isa, self).validate(dataset)

    def set_meta(self, dataset, **kwd):
        print("Setting metadata of ISA type: %s" % dataset.file_name)
        # raise Error("Setting metadata of ISA type")
        super(Isa, self).set_meta(dataset, **kwd)

    def split(cls, input_datasets, subdir_generator_function, split_params):
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

    def make_html_table( self, dataset, **kwargs ):
        """Create HTML table, used for displaying summary"""
        investigation_filename = self.get_primary_filename(dataset.files_path)
        # need to make sure other ISA files s_*.txt and a_*.txt are accessible
        parser = isatab.Parser()
        parser.parse(investigation_filename)
        isa = parser.isa
        # just an example how to pull data out
        inv_report = {
            'inv_title': isa.title,
            'inv_description': isa.description,
            'inv_submission_date': isa.submission_date,
            'inv_public_release_date': isa.public_release_date
        }
        study_reports = []
        for study in isa.studies:
            study_reports.append(
                {
                    'study_filename': study.filename,
                    'study_factors': ', '.join([x.name for x in study.factors]),
                    'study_num_sources': len(study.sources),
                    'study_num_samples': len(study.samples)
                }
            )
        out = ['<table cellspacing="0" cellpadding="3">']
        for k, v in inv_report.items():
            out.append( '<tr><td colspan="100%%">{k}: {v}</td></tr>'.format(k=k, v=v) )
        for study_report in study_reports:
            for k, v in study_report.items():
                out.append( '<tr><td colspan="100%%">{k}: {v}</td></tr>'.format(k=k, v=v) )
        out.append( '</table>' )
        out = "".join( out )
        return out
