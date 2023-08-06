"""
Tests for general glymur functionality.
"""
# E1101:  assertWarns introduced in python 3.2
# pylint: disable=E1101

# R0904:  Not too many methods in unittest.
# pylint: disable=R0904

# E0611:  unittest.mock is unknown to python2.7/pylint
# pylint: disable=E0611,F0401

import doctest
import os
import re
import shutil
import struct
import sys
import tempfile
import uuid
from xml.etree import cElementTree as ET

if sys.hexversion < 0x02070000:
    import unittest2 as unittest
else:
    import unittest

if sys.hexversion <= 0x03030000:
    from mock import patch
else:
    from unittest.mock import patch
import warnings

import numpy as np
import pkg_resources

import glymur
from glymur import Jp2k

from .fixtures import OPENJP2_IS_V2_OFFICIAL

try:
    DATA_ROOT = os.environ['OPJ_DATA_ROOT']
except KeyError:
    DATA_ROOT = None
except:
    raise


# Doc tests should be run as well.
def load_tests(loader, tests, ignore):
    # W0613:  "loader" and "ignore" are necessary for the protocol
    # They are unused here, however.
    # pylint: disable=W0613

    """Should run doc tests as well"""
    if os.name == "nt":
        # Can't do it on windows, temporary file issue.
        return tests
    if sys.hexversion < 0x02070000:
        # Don't bother with doctests on 2.6 for the time being.
        return tests
    if glymur.lib.openjp2.OPENJP2 is not None:
        tests.addTests(doctest.DocTestSuite('glymur.jp2k'))
    return tests


@unittest.skipIf(glymur.lib.openjp2.OPENJP2 is None and
                 glymur.lib.openjpeg.OPENJPEG is None,
                 "Missing openjp2 library.")
class TestConfig(unittest.TestCase):
    """Test suite for reading without proper library in place."""

    def setUp(self):
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

    def tearDown(self):
        pass

    def test_read_without_library(self):
        """Don't have either openjp2 or openjpeg libraries?  Must error out.
        """
        with patch('glymur.lib.openjp2.OPENJP2', new=None):
            with patch('glymur.lib.openjpeg.OPENJPEG', new=None):
                with self.assertRaises(glymur.jp2k.LibraryNotFoundError):
                    glymur.Jp2k(self.jp2file).read()

    def test_read_bands_without_library(self):
        """Don't have openjp2 library?  Must error out.
        """
        with patch('glymur.lib.openjp2.OPENJP2', new=None):
            with patch('glymur.lib.openjpeg.OPENJPEG', new=None):
                with self.assertRaises(glymur.jp2k.LibraryNotFoundError):
                    glymur.Jp2k(self.jp2file).read_bands()

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_write_without_library(self):
        """Don't have openjp2 library?  Must error out.
        """
        data = glymur.Jp2k(self.j2kfile).read()
        with patch('glymur.lib.openjp2.OPENJP2', new=None):
            with patch('glymur.lib.openjpeg.OPENJPEG', new=None):
                with self.assertRaises(glymur.jp2k.LibraryNotFoundError):
                    with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
                        ofile = Jp2k(tfile.name, 'wb')
                        ofile.write(data)


@unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
@unittest.skipIf(glymur.lib.openjp2.OPENJP2 is None,
                 "Missing openjp2 library.")
class TestJp2kBadXmlFile(unittest.TestCase):
    """Test suite for bad XML box situations"""

    @classmethod
    def setUpClass(cls):
        """Setup a JP2 file with a bad XML box.  We only need to do this once
        per class rather than once per test.
        """
        jp2file = pkg_resources.resource_filename(glymur.__name__,
                                                  "data/nemo.jp2")
        with tempfile.NamedTemporaryFile(suffix='.jp2', delete=False) as tfile:
            cls._bad_xml_file = tfile.name
            with open(jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                write_buffer = ifile.read(77)
                tfile.write(write_buffer)

                # Write the xml box with bad xml
                # Length = 28, id is 'xml '.
                write_buffer = struct.pack('>I4s', int(28), b'xml ')
                tfile.write(write_buffer)

                write_buffer = '<test>this is a test'
                write_buffer = write_buffer.encode()
                tfile.write(write_buffer)

                # Get the rest of the input file.
                write_buffer = ifile.read()
                tfile.write(write_buffer)
                tfile.flush()

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls._bad_xml_file)

    def setUp(self):
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

    def tearDown(self):
        pass

    @unittest.skipIf(sys.hexversion < 0x03020000,
                     "Uses features introduced in 3.2.")
    def test_invalid_xml_box_warning(self):
        """Should warn in case of bad XML"""
        with self.assertWarns(UserWarning):
            Jp2k(self._bad_xml_file)

    def test_invalid_xml_box(self):
        """Should be able to recover info from xml box with bad xml."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            jp2k = Jp2k(self._bad_xml_file)

        self.assertEqual(jp2k.box[3].box_id, 'xml ')
        self.assertEqual(jp2k.box[3].offset, 77)
        self.assertEqual(jp2k.box[3].length, 28)
        self.assertIsNone(jp2k.box[3].xml)


@unittest.skipIf(glymur.lib.openjp2.OPENJP2 is None,
                 "Missing openjp2 library.")
class TestJp2k(unittest.TestCase):
    """Test suite for version 2.0/2.0+ of openjpeg"""

    def setUp(self):
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

    def tearDown(self):
        pass

    def test_rlevel_max(self):
        """Verify that rlevel=-1 gets us the lowest resolution image"""
        j = Jp2k(self.j2kfile)
        thumbnail1 = j.read(rlevel=-1)
        thumbnail2 = j.read(rlevel=5)
        np.testing.assert_array_equal(thumbnail1, thumbnail2)
        self.assertEqual(thumbnail1.shape, (25, 15, 3))

    def test_bad_area_parameter(self):
        """Should error out appropriately if given a bad area parameter."""
        j = Jp2k(self.jp2file)
        with self.assertRaises(IOError):
            # Start corner must be >= 0
            j.read(area=(-1, -1, 1, 1))
        with self.assertRaises(IOError):
            # End corner must be > 0
            j.read(area=(10, 10, 0, 0))
        with self.assertRaises(IOError):
            # End corner must be >= start corner
            j.read(area=(10, 10, 8, 8))

    def test_rlevel_too_high(self):
        """Should error out appropriately if reduce level too high"""
        j = Jp2k(self.jp2file)
        with self.assertRaises(IOError):
            j.read(rlevel=6)

    def test_not_jpeg2000(self):
        """Should error out appropriately if not given a JPEG 2000 file."""
        filename = pkg_resources.resource_filename(glymur.__name__, "jp2k.py")
        with self.assertRaises(IOError):
            Jp2k(filename)

    def test_file_not_present(self):
        """Should error out if reading from a file that does not exist"""
        # Verify that we error out appropriately if not given an existing file
        # at all.
        with self.assertRaises(OSError):
            filename = 'this file does not actually exist on the file system.'
            Jp2k(filename)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_write_with_jp2_in_caps(self):
        """should be able to write with JP2 suffix."""
        j2k = Jp2k(self.j2kfile)
        expdata = j2k.read()
        with tempfile.NamedTemporaryFile(suffix='.JP2') as tfile:
            ofile = Jp2k(tfile.name, 'wb')
            ofile.write(expdata)
            actdata = ofile.read()
            np.testing.assert_array_equal(actdata, expdata)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_write_srgb_without_mct(self):
        """should be able to write RGB without specifying mct"""
        j2k = Jp2k(self.j2kfile)
        expdata = j2k.read()
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            ofile = Jp2k(tfile.name, 'wb')
            ofile.write(expdata, mct=False)
            actdata = ofile.read()
            np.testing.assert_array_equal(actdata, expdata)

            codestream = ofile.get_codestream()
            self.assertEqual(codestream.segment[2].spcod[3], 0)  # no mct

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_write_grayscale_with_mct(self):
        """MCT usage makes no sense for grayscale images."""
        j2k = Jp2k(self.j2kfile)
        expdata = j2k.read()
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            ofile = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError):
                ofile.write(expdata[:, :, 0], mct=True)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_write_cprl(self):
        """Must be able to write a CPRL progression order file"""
        # Issue 17
        j = Jp2k(self.jp2file)
        expdata = j.read(rlevel=1)
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            ofile = Jp2k(tfile.name, 'wb')
            ofile.write(expdata, prog='CPRL')
            actdata = ofile.read()
            np.testing.assert_array_equal(actdata, expdata)

            codestream = ofile.get_codestream()
            self.assertEqual(codestream.segment[2].spcod[0], glymur.core.CPRL)

    def test_jp2_boxes(self):
        """Verify the boxes of a JP2 file.  Basic jp2 test."""
        jp2k = Jp2k(self.jp2file)

        # top-level boxes
        self.assertEqual(len(jp2k.box), 6)

        self.assertEqual(jp2k.box[0].box_id, 'jP  ')
        self.assertEqual(jp2k.box[0].offset, 0)
        self.assertEqual(jp2k.box[0].length, 12)
        self.assertEqual(jp2k.box[0].longname, 'JPEG 2000 Signature')

        self.assertEqual(jp2k.box[1].box_id, 'ftyp')
        self.assertEqual(jp2k.box[1].offset, 12)
        self.assertEqual(jp2k.box[1].length, 20)
        self.assertEqual(jp2k.box[1].longname, 'File Type')

        self.assertEqual(jp2k.box[2].box_id, 'jp2h')
        self.assertEqual(jp2k.box[2].offset, 32)
        self.assertEqual(jp2k.box[2].length, 45)
        self.assertEqual(jp2k.box[2].longname, 'JP2 Header')

        self.assertEqual(jp2k.box[3].box_id, 'uuid')
        self.assertEqual(jp2k.box[3].offset, 77)
        self.assertEqual(jp2k.box[3].length, 638)

        self.assertEqual(jp2k.box[4].box_id, 'uuid')
        self.assertEqual(jp2k.box[4].offset, 715)
        self.assertEqual(jp2k.box[4].length, 2412)

        self.assertEqual(jp2k.box[5].box_id, 'jp2c')
        self.assertEqual(jp2k.box[5].offset, 3127)
        self.assertEqual(jp2k.box[5].length, 1132296)

        # jp2h super box
        self.assertEqual(len(jp2k.box[2].box), 2)

        self.assertEqual(jp2k.box[2].box[0].box_id, 'ihdr')
        self.assertEqual(jp2k.box[2].box[0].offset, 40)
        self.assertEqual(jp2k.box[2].box[0].length, 22)
        self.assertEqual(jp2k.box[2].box[0].longname, 'Image Header')
        self.assertEqual(jp2k.box[2].box[0].height, 1456)
        self.assertEqual(jp2k.box[2].box[0].width, 2592)
        self.assertEqual(jp2k.box[2].box[0].num_components, 3)
        self.assertEqual(jp2k.box[2].box[0].bits_per_component, 8)
        self.assertEqual(jp2k.box[2].box[0].signed, False)
        self.assertEqual(jp2k.box[2].box[0].compression, 7)
        self.assertEqual(jp2k.box[2].box[0].colorspace_unknown, False)
        self.assertEqual(jp2k.box[2].box[0].ip_provided, False)

        self.assertEqual(jp2k.box[2].box[1].box_id, 'colr')
        self.assertEqual(jp2k.box[2].box[1].offset, 62)
        self.assertEqual(jp2k.box[2].box[1].length, 15)
        self.assertEqual(jp2k.box[2].box[1].longname, 'Colour Specification')
        self.assertEqual(jp2k.box[2].box[1].precedence, 0)
        self.assertEqual(jp2k.box[2].box[1].approximation, 0)
        self.assertEqual(jp2k.box[2].box[1].colorspace, glymur.core.SRGB)
        self.assertIsNone(jp2k.box[2].box[1].icc_profile)

    @unittest.skipIf(DATA_ROOT is None,
                     "OPJ_DATA_ROOT environment variable not set")
    def test_j2k_box(self):
        """A J2K/J2C file must not have any boxes."""
        # Verify that a J2K file has no boxes.
        filename = os.path.join(DATA_ROOT, 'input/conformance/p0_01.j2k')
        jp2k = Jp2k(filename)
        self.assertEqual(len(jp2k.box), 0)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_64bit_xl_field(self):
        """XL field should be supported"""
        # Verify that boxes with the XL field are properly read.
        # Don't have such a file on hand, so we create one.  Copy our example
        # file, but making the codestream have a 64-bit XL field.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                write_buffer = ifile.read(3127)
                tfile.write(write_buffer)

                # The L field must be 1 in order to signal the presence of the
                # XL field.  The actual length of the jp2c box increased by 8
                # (8 bytes for the XL field).
                length = 1
                typ = b'jp2c'
                xlen = 1133427 + 8
                write_buffer = struct.pack('>I4sQ', int(length), typ, xlen)
                tfile.write(write_buffer)

                # Get the rest of the input file (minus the 8 bytes for L and
                # T.
                ifile.seek(8, 1)
                write_buffer = ifile.read()
                tfile.write(write_buffer)
                tfile.flush()

            jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[5].box_id, 'jp2c')
            self.assertEqual(jp2k.box[5].offset, 3127)
            self.assertEqual(jp2k.box[5].length, 1133427 + 8)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_length_field_is_zero(self):
        """L=0 (length field in box header) is allowed"""
        # Verify that boxes with the L field as zero are correctly read.
        # This should only happen in the last box of a JPEG 2000 file.
        # Our example image has its last box at byte 588458.
        baseline_jp2 = Jp2k(self.jp2file)
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                write_buffer = ifile.read(588458)
                tfile.write(write_buffer)

                length = 0
                typ = b'uuid'
                write_buffer = struct.pack('>I4s', int(length), typ)
                tfile.write(write_buffer)

                # Get the rest of the input file (minus the 8 bytes for L and
                # T.
                ifile.seek(8, 1)
                write_buffer = ifile.read()
                tfile.write(write_buffer)
                tfile.flush()

            new_jp2 = Jp2k(tfile.name)

            # The top level boxes in each file should match.
            for j in range(len(baseline_jp2.box)):
                self.assertEqual(new_jp2.box[j].box_id,
                                 baseline_jp2.box[j].box_id)
                self.assertEqual(new_jp2.box[j].offset,
                                 baseline_jp2.box[j].offset)
                self.assertEqual(new_jp2.box[j].length,
                                 baseline_jp2.box[j].length)

    @unittest.skipIf(DATA_ROOT is None,
                     "OPJ_DATA_ROOT environment variable not set")
    def test_read_differing_subsamples(self):
        """should error out with read used on differently subsampled images"""
        # Verify that we error out appropriately if we use the read method
        # on an image with differing subsamples
        #
        # Issue 86.
        filename = os.path.join(DATA_ROOT, 'input/conformance/p0_05.j2k')
        j = Jp2k(filename)
        with self.assertRaises(RuntimeError):
            j.read()

    @unittest.skipIf(DATA_ROOT is None,
                     "OPJ_DATA_ROOT environment variable not set")
    def test_empty_box_with_j2k(self):
        """Verify that the list of boxes in a J2C/J2K file is present, but
        empty.
        """
        filename = os.path.join(DATA_ROOT, 'input/conformance/p0_05.j2k')
        j = Jp2k(filename)
        self.assertEqual(j.box, [])

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_cblkh_different_than_width(self):
        """Verify that we can set a code block size where height does not equal
        width.
        """
        data = np.zeros((128, 128), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            j = Jp2k(tfile.name, 'wb')

            # The code block dimensions are given as rows x columns.
            j.write(data, cbsize=(16, 32))

            codestream = j.get_codestream()

            # Code block size is reported as XY in the codestream.
            self.assertEqual(tuple(codestream.segment[2].spcod[5:7]), (3, 2))

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_too_many_dimensions(self):
        """OpenJP2 only allows 2D or 3D images."""
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError):
                data = np.zeros((128, 128, 2, 2), dtype=np.uint8)
                j.write(data)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_unrecognized_jp2_clrspace(self):
        """We only allow RGB and GRAYSCALE.  Should error out with others"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError):
                data = np.zeros((128, 128, 3), dtype=np.uint8)
                j.write(data, colorspace='cmyk')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_2d_rgb(self):
        """RGB must have at least 3 components."""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError):
                data = np.zeros((128, 128, 2), dtype=np.uint8)
                j.write(data, colorspace='rgb')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_colorspace_with_j2k(self):
        """Specifying a colorspace with J2K does not make sense"""
        with tempfile.NamedTemporaryFile(suffix='.j2k') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError):
                data = np.zeros((128, 128, 3), dtype=np.uint8)
                j.write(data, colorspace='rgb')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_specify_rgb(self):
        """specify RGB explicitly"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 3), dtype=np.uint8)
            j.write(data, colorspace='rgb')
            self.assertEqual(j.box[2].box[1].colorspace, glymur.core.SRGB)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_specify_gray(self):
        """test gray explicitly specified (that's GRAY, not GREY)"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128), dtype=np.uint8)
            j.write(data, colorspace='gray')
            self.assertEqual(j.box[2].box[1].colorspace,
                             glymur.core.GREYSCALE)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_specify_grey(self):
        """test grey explicitly specified"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128), dtype=np.uint8)
            j.write(data, colorspace='grey')
            self.assertEqual(j.box[2].box[1].colorspace,
                             glymur.core.GREYSCALE)

    @unittest.skipIf(OPENJP2_IS_V2_OFFICIAL,
                     "Does not seem to work on official v2.0.0 release.")
    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_grey_with_extra_component(self):
        """version 2.0 cannot write gray + extra"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 2), dtype=np.uint8)
            j.write(data)
            self.assertEqual(j.box[2].box[0].height, 128)
            self.assertEqual(j.box[2].box[0].width, 128)
            self.assertEqual(j.box[2].box[0].num_components, 2)
            self.assertEqual(j.box[2].box[1].colorspace,
                             glymur.core.GREYSCALE)

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_grey_with_two_extra_comps(self):
        """should be able to write gray + two extra components"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 3), dtype=np.uint8)
            j.write(data, colorspace='gray')
            self.assertEqual(j.box[2].box[0].height, 128)
            self.assertEqual(j.box[2].box[0].width, 128)
            self.assertEqual(j.box[2].box[0].num_components, 3)
            self.assertEqual(j.box[2].box[1].colorspace,
                             glymur.core.GREYSCALE)

    @unittest.skipIf(OPENJP2_IS_V2_OFFICIAL,
                     "Does not seem to work on official v2.0.0 release.")
    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_rgb_with_extra_component(self):
        """v2.0+ should be able to write extra components"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            data = np.zeros((128, 128, 4), dtype=np.uint8)
            j.write(data)
            self.assertEqual(j.box[2].box[0].height, 128)
            self.assertEqual(j.box[2].box[0].width, 128)
            self.assertEqual(j.box[2].box[0].num_components, 4)
            self.assertEqual(j.box[2].box[1].colorspace, glymur.core.SRGB)

    @unittest.skipIf(OPENJP2_IS_V2_OFFICIAL is False,
                     "Test is specific for v2.0.0 release")
    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_extra_components_on_v2(self):
        """must error out in 1.x with extra components."""
        # Extra components seems to require 2.0+.  Verify that we error out.
        with self.assertRaises(IOError):
            with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
                j = Jp2k(tfile.name, 'wb')
                data = np.zeros((128, 128, 4), dtype=np.uint8)
                j.write(data)

    def test_specify_ycc(self):
        """Should reject YCC"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            with self.assertRaises(IOError):
                data = np.zeros((128, 128, 3), dtype=np.uint8)
                j.write(data, colorspace='ycc')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_uinf_ulst_url_boxes(self):
        """Verify that we can read UINF, ULST, and URL boxes"""
        # Verify that we can read UINF, ULST, and URL boxes.  I don't have
        # easy access to such a file, and there's no such file in the
        # openjpeg repository, so I'll fake one.
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                write_buffer = ifile.read(77)
                tfile.write(write_buffer)

                # Write the UINF superbox
                # Length = 50, id is uinf.
                write_buffer = struct.pack('>I4s', int(50), b'uinf')
                tfile.write(write_buffer)

                # Write the ULST box.
                # Length is 26, 1 UUID, hard code that UUID as zeros.
                write_buffer = struct.pack('>I4sHIIII', int(26), b'ulst',
                                           int(1), int(0), int(0), int(0),
                                           int(0))
                tfile.write(write_buffer)

                # Write the URL box.
                # Length is 16, version is one byte, flag is 3 bytes, url
                # is the rest.
                write_buffer = struct.pack('>I4sBBBB',
                                           int(16), b'url ',
                                           int(0), int(0), int(0), int(0))
                tfile.write(write_buffer)
                write_buffer = struct.pack('>ssss', b'a', b'b', b'c', b'd')
                tfile.write(write_buffer)

                # Get the rest of the input file.
                write_buffer = ifile.read()
                tfile.write(write_buffer)
                tfile.flush()

            jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[3].box_id, 'uinf')
            self.assertEqual(jp2k.box[3].offset, 77)
            self.assertEqual(jp2k.box[3].length, 50)

            self.assertEqual(jp2k.box[3].box[0].box_id, 'ulst')
            self.assertEqual(jp2k.box[3].box[0].offset, 85)
            self.assertEqual(jp2k.box[3].box[0].length, 26)
            ulst = []
            ulst.append(uuid.UUID('00000000-0000-0000-0000-000000000000'))
            self.assertEqual(jp2k.box[3].box[0].ulst, ulst)

            self.assertEqual(jp2k.box[3].box[1].box_id, 'url ')
            self.assertEqual(jp2k.box[3].box[1].offset, 111)
            self.assertEqual(jp2k.box[3].box[1].length, 16)
            self.assertEqual(jp2k.box[3].box[1].version, 0)
            self.assertEqual(jp2k.box[3].box[1].flag, (0, 0, 0))
            self.assertEqual(jp2k.box[3].box[1].url, 'abcd')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_xml_with_trailing_nulls(self):
        """ElementTree doesn't like trailing null chars after valid XML text"""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            with open(self.jp2file, 'rb') as ifile:
                # Everything up until the jp2c box.
                write_buffer = ifile.read(77)
                tfile.write(write_buffer)

                # Write the xml box
                # Length = 36, id is 'xml '.
                write_buffer = struct.pack('>I4s', int(36), b'xml ')
                tfile.write(write_buffer)

                write_buffer = '<test>this is a test</test>' + chr(0)
                write_buffer = write_buffer.encode()
                tfile.write(write_buffer)

                # Get the rest of the input file.
                write_buffer = ifile.read()
                tfile.write(write_buffer)
                tfile.flush()

            jp2k = Jp2k(tfile.name)

            self.assertEqual(jp2k.box[3].box_id, 'xml ')
            self.assertEqual(jp2k.box[3].offset, 77)
            self.assertEqual(jp2k.box[3].length, 36)
            self.assertEqual(ET.tostring(jp2k.box[3].xml.getroot()),
                             b'<test>this is a test</test>')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_asoc_label_box(self):
        """Test asoc and label box"""
        # Construct a fake file with an asoc and a label box, as
        # OpenJPEG doesn't have such a file.
        data = Jp2k(self.jp2file).read(rlevel=1)
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            j = Jp2k(tfile.name, 'wb')
            j.write(data)

            with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile2:

                # Offset of the codestream is where we start.
                read_buffer = tfile.read(77)
                tfile2.write(read_buffer)

                # read the rest of the file, it's the codestream.
                codestream = tfile.read()

                # Write the asoc superbox.
                # Length = 36, id is 'asoc'.
                write_buffer = struct.pack('>I4s', int(56), b'asoc')
                tfile2.write(write_buffer)

                # Write the contained label box
                write_buffer = struct.pack('>I4s', int(13), b'lbl ')
                tfile2.write(write_buffer)
                tfile2.write('label'.encode())

                # Write the xml box
                # Length = 36, id is 'xml '.
                write_buffer = struct.pack('>I4s', int(35), b'xml ')
                tfile2.write(write_buffer)

                write_buffer = '<test>this is a test</test>'
                write_buffer = write_buffer.encode()
                tfile2.write(write_buffer)

                # Now append the codestream.
                tfile2.write(codestream)
                tfile2.flush()

                jasoc = Jp2k(tfile2.name)
                self.assertEqual(jasoc.box[3].box_id, 'asoc')
                self.assertEqual(jasoc.box[3].box[0].box_id, 'lbl ')
                self.assertEqual(jasoc.box[3].box[0].label, 'label')
                self.assertEqual(jasoc.box[3].box[1].box_id, 'xml ')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    @unittest.skipIf(OPENJP2_IS_V2_OFFICIAL,
                     "Segfault on official v2.0.0 release.")
    def test_openjpeg_library_message(self):
        """Verify the error message produced by the openjpeg library"""
        # This will confirm that the error callback mechanism is working.
        with open(self.jp2file, 'rb') as fptr:
            data = fptr.read()
            with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
                # Codestream starts at byte 3127. SIZ marker at 3137.
                # COD marker at 3186.  Subsampling at 3180.
                tfile.write(data[0:3179])

                # Make the DY bytes of the SIZ segment zero.  That means that
                # a subsampling factor is zero, which is illegal.
                tfile.write(b'\x00')
                tfile.write(data[3180:3182])
                tfile.write(b'\x00')
                tfile.write(data[3184:3186])
                tfile.write(b'\x00')

                tfile.write(data[3186:])
                tfile.flush()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    j = Jp2k(tfile.name)
                regexp = re.compile(r'''OpenJPEG\slibrary\serror:\s+
                                        Invalid\svalues\sfor\scomp\s=\s0\s+
                                        :\sdx=1\sdy=0''', re.VERBOSE)
                if sys.hexversion < 0x03020000:
                    with self.assertRaisesRegexp((IOError, OSError), regexp):
                        j.read(rlevel=1)
                else:
                    with self.assertRaisesRegex((IOError, OSError), regexp):
                        j.read(rlevel=1)

    def test_xmp_attribute(self):
        """Verify the XMP packet in the shipping example file can be read."""
        j = Jp2k(self.jp2file)
        xmp = j.box[4].data
        ns0 = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
        ns1 = '{http://ns.adobe.com/xap/1.0/}'
        name = '{0}RDF/{0}Description'.format(ns0)
        elt = xmp.find(name)
        attr_value = elt.attrib['{0}CreatorTool'.format(ns1)]
        self.assertEqual(attr_value, 'glymur')

    @unittest.skipIf(os.name == "nt", "NamedTemporaryFile issue on windows")
    def test_unrecognized_exif_tag(self):
        """An unrecognized exif tag should be handled gracefully."""
        with tempfile.NamedTemporaryFile(suffix='.jp2') as tfile:
            shutil.copyfile(self.jp2file, tfile.name)

            # The Exif UUID starts at byte 77.  There are 8 bytes for the L and
            # T fields, then 16 bytes for the UUID identifier, then 6 exif
            # header bytes, then 8 bytes for the TIFF header, then 2 bytes
            # the the Image IFD number of tags, where we finally find the first
            # tag, "Make" (271).  We'll corrupt it by changing it into 171,
            # which does not correspond to any known Exif Image tag.
            with open(tfile.name, 'r+b') as fptr:
                fptr.seek(117)
                write_buffer = struct.pack('<H', int(171))
                fptr.write(write_buffer)

            # Verify that a warning is issued, but only on python3.
            # On python2, just suppress the warning.
            if sys.hexversion < 0x03030000:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    j = Jp2k(tfile.name)
            else:
                with self.assertWarns(UserWarning):
                    j = Jp2k(tfile.name)

            exif = j.box[3].data
            # Were the tag == 271, 'Make' would be in the keys instead.
            self.assertTrue(171 in exif['Image'].keys())
            self.assertFalse('Make' in exif['Image'].keys())


@unittest.skipIf(glymur.lib.openjpeg.OPENJPEG is None,
                 "Missing openjpeg library.")
class TestJp2k15(unittest.TestCase):
    """Test suite for openjpeg 1.5"""

    @classmethod
    def setUpClass(cls):
        # Monkey patch the package so as to use OPENJPEG instead of OPENJP2
        cls.openjp2 = glymur.lib.openjp2.OPENJP2
        glymur.lib.openjp2.OPENJP2 = None

    @classmethod
    def tearDownClass(cls):
        # Restore OPENJP2
        glymur.lib.openjp2.OPENJP2 = cls.openjp2

    def setUp(self):
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

    def tearDown(self):
        pass

    def test_area(self):
        """Area option not allowed for 1.5.1.
        """
        j2k = Jp2k(self.j2kfile)
        with self.assertRaises(TypeError):
            j2k.read(area=(0, 0, 100, 100))

    def test_tile(self):
        """tile option not allowed for 1.5.1.
        """
        j2k = Jp2k(self.j2kfile)
        with self.assertRaises(TypeError):
            j2k.read(tile=0)

    def test_layer(self):
        """layer option not allowed for 1.5.1.
        """
        j2k = Jp2k(self.j2kfile)
        with self.assertRaises(TypeError):
            j2k.read(layer=1)

    def test_basic_jp2(self):
        """This test is only useful when openjp2 is not available
        and OPJ_DATA_ROOT is not set.  We need at least one
        working JP2 test.
        """
        j2k = Jp2k(self.jp2file)
        j2k.read(rlevel=1)

    def test_basic_j2k(self):
        """This test is only useful when openjp2 is not available
        and OPJ_DATA_ROOT is not set.  We need at least one
        working J2K test.
        """
        j2k = Jp2k(self.j2kfile)
        j2k.read()


if __name__ == "__main__":
    unittest.main()
