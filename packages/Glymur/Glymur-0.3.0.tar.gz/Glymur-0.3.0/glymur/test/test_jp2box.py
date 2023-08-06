#pylint:  disable-all
import doctest
import os
import sys
import tempfile
import xml.etree.cElementTree as ET

if sys.hexversion < 0x02070000:
    import unittest2 as unittest
else:
    import unittest

import numpy as np
import pkg_resources

import glymur
from glymur import Jp2k
from glymur.jp2box import *
from glymur.core import COLOR, OPACITY
from glymur.core import RED, GREEN, BLUE, GREY, WHOLE_IMAGE

from .fixtures import OPENJP2_IS_V2_OFFICIAL

try:
    format_corpus_data_root = os.environ['FORMAT_CORPUS_DATA_ROOT']
except KeyError:
    format_corpus_data_root = None


# Doc tests should be run as well.
def load_tests(loader, tests, ignore):
    if os.name == "nt":
        # Can't do it on windows, temporary file issue.
        return tests
    tests.addTests(doctest.DocTestSuite('glymur.jp2box'))
    return tests


@unittest.skipIf(OPENJP2_IS_V2_OFFICIAL,
                 "Requires v2.0.0+ in order to run.")
@unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
@unittest.skipIf(glymur.lib.openjp2.OPENJP2 is None,
                 "Missing openjp2 library.")
class TestChannelDefinition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Need a one_plane plane image for greyscale testing."""
        j2k = Jp2k(glymur.data.goodstuff())
        data = j2k.read()
        # Write the first component back out to file.
        with tempfile.NamedTemporaryFile(suffix=".j2k", delete=False) as tfile:
            grey_j2k = Jp2k(tfile.name, 'wb')
            grey_j2k.write(data[:, :, 0])
            cls.one_plane = tfile.name
        # Write the first two components back out to file.
        with tempfile.NamedTemporaryFile(suffix=".j2k", delete=False) as tfile:
            grey_j2k = Jp2k(tfile.name, 'wb')
            grey_j2k.write(data[:, :, 0:1])
            cls.two_planes = tfile.name
        # Write four components back out to file.
        with tempfile.NamedTemporaryFile(suffix=".j2k", delete=False) as tfile:
            rgba_jp2 = Jp2k(tfile.name, 'wb')
            shape = (data.shape[0], data.shape[1], 1)
            alpha = np.zeros((shape), dtype=data.dtype)
            data4 = np.concatenate((data, alpha), axis=2)
            rgba_jp2.write(data4)
            cls.four_planes = tfile.name

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.one_plane)
        os.unlink(cls.two_planes)
        os.unlink(cls.four_planes)

    def setUp(self):
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

        j2k = Jp2k(self.j2kfile)
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)

        self.jP = JPEG2000SignatureBox()
        self.ftyp = FileTypeBox()
        self.jp2h = JP2HeaderBox()
        self.jp2c = ContiguousCodestreamBox()
        self.ihdr = ImageHeaderBox(height=height, width=width,
                                   num_components=num_components)
        self.colr_rgb = ColourSpecificationBox(colorspace=glymur.core.SRGB)
        self.colr_gr = ColourSpecificationBox(colorspace=glymur.core.GREYSCALE)

    def tearDown(self):
        pass

    def test_cdef_no_inputs(self):
        """channel_type and association are required inputs."""
        with self.assertRaises(IOError):
            glymur.jp2box.ChannelDefinitionBox()

    def test_rgb_with_index(self):
        """Just regular RGB."""
        j2k = Jp2k(self.j2kfile)
        channel_type = [COLOR, COLOR, COLOR]
        association = [RED, GREEN, BLUE]
        cdef = glymur.jp2box.ChannelDefinitionBox(index=[0, 1, 2],
                                                  channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_rgb, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)

            jp2 = Jp2k(tfile.name)
            jp2h = jp2.box[2]
            boxes = [box.box_id for box in jp2h.box]
            self.assertEqual(boxes, ['ihdr', 'colr', 'cdef'])
            self.assertEqual(jp2h.box[2].index, (0, 1, 2))
            self.assertEqual(jp2h.box[2].channel_type,
                             (COLOR, COLOR, COLOR))
            self.assertEqual(jp2h.box[2].association,
                             (RED, GREEN, BLUE))

    def test_rgb(self):
        """Just regular RGB, but don't supply the optional index."""
        j2k = Jp2k(self.j2kfile)
        channel_type = [COLOR, COLOR, COLOR]
        association = [RED, GREEN, BLUE]
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_rgb, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)

            jp2 = Jp2k(tfile.name)
            jp2h = jp2.box[2]
            boxes = [box.box_id for box in jp2h.box]
            self.assertEqual(boxes, ['ihdr', 'colr', 'cdef'])
            self.assertEqual(jp2h.box[2].index, (0, 1, 2))
            self.assertEqual(jp2h.box[2].channel_type,
                             (COLOR, COLOR, COLOR))
            self.assertEqual(jp2h.box[2].association,
                             (RED, GREEN, BLUE))

    def test_rgba(self):
        """Just regular RGBA."""
        j2k = Jp2k(self.four_planes)
        channel_type = (COLOR, COLOR, COLOR, OPACITY)
        association = (RED, GREEN, BLUE, WHOLE_IMAGE)
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_rgb, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)

            jp2 = Jp2k(tfile.name)
            jp2h = jp2.box[2]
            boxes = [box.box_id for box in jp2h.box]
            self.assertEqual(boxes, ['ihdr', 'colr', 'cdef'])
            self.assertEqual(jp2h.box[2].index, (0, 1, 2, 3))
            self.assertEqual(jp2h.box[2].channel_type, channel_type)
            self.assertEqual(jp2h.box[2].association, association)

    def test_bad_rgba(self):
        """R, G, and B must be specified."""
        j2k = Jp2k(self.four_planes)
        channel_type = (COLOR, COLOR, OPACITY, OPACITY)
        association = (RED, GREEN, BLUE, WHOLE_IMAGE)
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_rgb, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError) as ce:
                j2k.wrap(tfile.name, boxes=boxes)

    def test_grey(self):
        """Just regular greyscale."""
        j2k = Jp2k(self.one_plane)
        channel_type = (COLOR,)
        association = (GREY,)
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_gr, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)

            jp2 = Jp2k(tfile.name)
            jp2h = jp2.box[2]
            boxes = [box.box_id for box in jp2h.box]
            self.assertEqual(boxes, ['ihdr', 'colr', 'cdef'])
            self.assertEqual(jp2h.box[2].index, (0,))
            self.assertEqual(jp2h.box[2].channel_type, channel_type)
            self.assertEqual(jp2h.box[2].association, association)

    def test_grey_alpha(self):
        """Just regular greyscale plus alpha."""
        j2k = Jp2k(self.two_planes)
        channel_type = (COLOR, OPACITY)
        association = (GREY, WHOLE_IMAGE)
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_gr, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)

            jp2 = Jp2k(tfile.name)
            jp2h = jp2.box[2]
            boxes = [box.box_id for box in jp2h.box]
            self.assertEqual(boxes, ['ihdr', 'colr', 'cdef'])
            self.assertEqual(jp2h.box[2].index, (0, 1))
            self.assertEqual(jp2h.box[2].channel_type, channel_type)
            self.assertEqual(jp2h.box[2].association, association)

    def test_bad_grey_alpha(self):
        """A greyscale image with alpha layer must specify a color channel"""
        j2k = Jp2k(self.two_planes)

        channel_type = (OPACITY, OPACITY)
        association = (GREY, WHOLE_IMAGE)

        # This cdef box
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)
        boxes = [self.ihdr, self.colr_gr, cdef]
        self.jp2h.box = boxes
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises((OSError, IOError)) as ce:
                j2k.wrap(tfile.name, boxes=boxes)

    def test_only_one_cdef_in_jp2_header(self):
        """There can only be one channel definition box in the jp2 header."""
        j2k = Jp2k(self.j2kfile)

        channel_type = (COLOR, COLOR, COLOR)
        association = (RED, GREEN, BLUE)
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)

        boxes = [self.ihdr, cdef, self.colr_rgb, cdef]
        self.jp2h.box = boxes

        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]

        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)

    def test_not_in_jp2_header(self):
        j2k = Jp2k(self.j2kfile)
        boxes = [self.ihdr, self.colr_rgb]
        self.jp2h.box = boxes

        channel_type = (COLOR, COLOR, COLOR)
        association = (RED, GREEN, BLUE)
        cdef = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                  association=association)

        boxes = [self.jP, self.ftyp, self.jp2h, cdef, self.jp2c]

        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)

    def test_bad_type(self):
        # Channel types are limited to 0, 1, 2, 65535
        # Should reject if not all of index, channel_type, association the
        # same length.
        channel_type = (COLOR, COLOR, 3)
        association = (RED, GREEN, BLUE)
        with self.assertRaises(IOError):
            box = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                     association=association)

    def test_wrong_lengths(self):
        # Should reject if not all of index, channel_type, association the
        # same length.
        channel_type = (COLOR, COLOR)
        association = (RED, GREEN, BLUE)
        with self.assertRaises(IOError):
            box = glymur.jp2box.ChannelDefinitionBox(channel_type=channel_type,
                                                     association=association)


@unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
class TestXML(unittest.TestCase):

    def setUp(self):
        self.jp2file = glymur.data.nemo()
        self.j2kfile = glymur.data.goodstuff()

        raw_xml = b"""<?xml version="1.0"?>
        <data>
            <country name="Liechtenstein">
                <rank>1</rank>
                <year>2008</year>
                <gdppc>141100</gdppc>
                <neighbor name="Austria" direction="E"/>
                <neighbor name="Switzerland" direction="W"/>
            </country>
            <country name="Singapore">
                <rank>4</rank>
                <year>2011</year>
                <gdppc>59900</gdppc>
                <neighbor name="Malaysia" direction="N"/>
            </country>
            <country name="Panama">
                <rank>68</rank>
                <year>2011</year>
                <gdppc>13600</gdppc>
                <neighbor name="Costa Rica" direction="W"/>
                <neighbor name="Colombia" direction="E"/>
            </country>
        </data>"""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tfile:
            tfile.write(raw_xml)
            tfile.flush()
        self.xmlfile = tfile.name

        j2k = Jp2k(self.j2kfile)
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)

        self.jP = JPEG2000SignatureBox()
        self.ftyp = FileTypeBox()
        self.jp2h = JP2HeaderBox()
        self.jp2c = ContiguousCodestreamBox()
        self.ihdr = ImageHeaderBox(height=height, width=width,
                                   num_components=num_components)
        self.colr = ColourSpecificationBox(colorspace=glymur.core.SRGB)

    def tearDown(self):
        os.unlink(self.xmlfile)
        pass

    def test_negative_both_file_and_xml_provided(self):
        """The XML should come from only one source."""
        j2k = Jp2k(self.j2kfile)
        xml_object = ET.parse(self.xmlfile)
        with self.assertRaises((IOError, OSError)) as ce:
            xmlb = glymur.jp2box.XMLBox(filename=self.xmlfile, xml=xml_object)

    @unittest.skipIf(os.name == "nt",
                     "Problems using NamedTemporaryFile on windows.")
    def test_basic_xml(self):
        # Should be able to write an XMLBox.
        j2k = Jp2k(self.j2kfile)

        self.jp2h.box = [self.ihdr, self.colr]

        the_xml = ET.fromstring('<?xml version="1.0"?><data>0</data>')
        xmlb = glymur.jp2box.XMLBox(xml=the_xml)
        self.assertEqual(ET.tostring(xmlb.xml),
                         b'<data>0</data>')

        boxes = [self.jP, self.ftyp, self.jp2h, xmlb, self.jp2c]

        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)
            jp2 = Jp2k(tfile.name)
            self.assertEqual(jp2.box[3].box_id, 'xml ')
            self.assertEqual(ET.tostring(jp2.box[3].xml.getroot()),
                             b'<data>0</data>')

    @unittest.skipIf(os.name == "nt",
                     "Problems using NamedTemporaryFile on windows.")
    def test_xml_from_file(self):
        j2k = Jp2k(self.j2kfile)

        self.jp2h.box = [self.ihdr, self.colr]

        xmlb = glymur.jp2box.XMLBox(filename=self.xmlfile)
        boxes = [self.jP, self.ftyp, self.jp2h, xmlb, self.jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)
            jp2 = Jp2k(tfile.name)

            output_boxes = [box.box_id for box in jp2.box]
            self.assertEqual(output_boxes, ['jP  ', 'ftyp', 'jp2h', 'xml ',
                                            'jp2c'])

            elts = jp2.box[3].xml.findall('country')
            self.assertEqual(len(elts), 3)

            neighbor = elts[1].find('neighbor')
            self.assertEqual(neighbor.attrib['name'], 'Malaysia')
            self.assertEqual(neighbor.attrib['direction'], 'N')


class TestColourSpecificationBox(unittest.TestCase):

    def setUp(self):
        self.j2kfile = glymur.data.goodstuff()

        j2k = Jp2k(self.j2kfile)
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)

        self.jP = JPEG2000SignatureBox()
        self.ftyp = FileTypeBox()
        self.jp2h = JP2HeaderBox()
        self.jp2c = ContiguousCodestreamBox()
        self.ihdr = ImageHeaderBox(height=height, width=width,
                                   num_components=num_components)

    def tearDown(self):
        pass

    @unittest.skipIf(os.name == "nt",
                     "Problems using NamedTemporaryFile on windows.")
    def test_color_specification_box_with_out_enumerated_colorspace(self):
        j2k = Jp2k(self.j2kfile)

        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        boxes[2].box = [self.ihdr, ColourSpecificationBox(colorspace=None)]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(NotImplementedError):
                j2k.wrap(tfile.name, boxes=boxes)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_missing_colr_box(self):
        j2k = Jp2k(self.j2kfile)
        boxes = [self.jP, self.ftyp, self.jp2h, self.jp2c]
        boxes[2].box = [self.ihdr]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)

    def test_default_ColourSpecificationBox(self):
        b = glymur.jp2box.ColourSpecificationBox(colorspace=glymur.core.SRGB)
        self.assertEqual(b.method,  glymur.core.ENUMERATED_COLORSPACE)
        self.assertEqual(b.precedence, 0)
        self.assertEqual(b.approximation, 0)
        self.assertEqual(b.colorspace, glymur.core.SRGB)
        self.assertIsNone(b.icc_profile)

    def test_ColourSpecificationBox_with_colorspace_and_icc(self):
        # Colour specification boxes can't have both.
        with self.assertRaises((OSError, IOError)):
            colorspace = glymur.core.SRGB
            icc_profile = b'\x01\x02\x03\x04'
            b = glymur.jp2box.ColourSpecificationBox(colorspace=colorspace,
                                                     icc_profile=icc_profile)

    def test_ColourSpecificationBox_with_bad_method(self):
        colorspace = glymur.core.SRGB
        method = -1
        with self.assertRaises(IOError):
            b = glymur.jp2box.ColourSpecificationBox(colorspace=colorspace,
                                                     method=method)

    def test_ColourSpecificationBox_with_bad_approximation(self):
        colorspace = glymur.core.SRGB
        approx = -1
        with self.assertRaises(IOError):
            b = glymur.jp2box.ColourSpecificationBox(colorspace=colorspace,
                                                     approximation=approx)


@unittest.skipIf(glymur.lib.openjp2.OPENJP2 is None,
                 "Missing openjp2 library.")
class TestWrap(unittest.TestCase):

    def setUp(self):
        self.j2kfile = glymur.data.goodstuff()
        self.jp2file = glymur.data.nemo()

    def tearDown(self):
        pass

    def verify_wrapped_raw(self, jp2file):
        # Shared method by at least two tests.
        jp2 = Jp2k(jp2file)
        self.assertEqual(len(jp2.box), 4)

        self.assertEqual(jp2.box[0].box_id, 'jP  ')
        self.assertEqual(jp2.box[0].offset, 0)
        self.assertEqual(jp2.box[0].length, 12)
        self.assertEqual(jp2.box[0].longname, 'JPEG 2000 Signature')

        self.assertEqual(jp2.box[1].box_id, 'ftyp')
        self.assertEqual(jp2.box[1].offset, 12)
        self.assertEqual(jp2.box[1].length, 20)
        self.assertEqual(jp2.box[1].longname, 'File Type')

        self.assertEqual(jp2.box[2].box_id, 'jp2h')
        self.assertEqual(jp2.box[2].offset, 32)
        self.assertEqual(jp2.box[2].length, 45)
        self.assertEqual(jp2.box[2].longname, 'JP2 Header')

        self.assertEqual(jp2.box[3].box_id, 'jp2c')
        self.assertEqual(jp2.box[3].offset, 77)
        self.assertEqual(jp2.box[3].length, 115228)

        # jp2h super box
        self.assertEqual(len(jp2.box[2].box), 2)

        self.assertEqual(jp2.box[2].box[0].box_id, 'ihdr')
        self.assertEqual(jp2.box[2].box[0].offset, 40)
        self.assertEqual(jp2.box[2].box[0].length, 22)
        self.assertEqual(jp2.box[2].box[0].longname, 'Image Header')
        self.assertEqual(jp2.box[2].box[0].height, 800)
        self.assertEqual(jp2.box[2].box[0].width, 480)
        self.assertEqual(jp2.box[2].box[0].num_components, 3)
        self.assertEqual(jp2.box[2].box[0].bits_per_component, 8)
        self.assertEqual(jp2.box[2].box[0].signed, False)
        self.assertEqual(jp2.box[2].box[0].compression, 7)
        self.assertEqual(jp2.box[2].box[0].colorspace_unknown, False)
        self.assertEqual(jp2.box[2].box[0].ip_provided, False)

        self.assertEqual(jp2.box[2].box[1].box_id, 'colr')
        self.assertEqual(jp2.box[2].box[1].offset, 62)
        self.assertEqual(jp2.box[2].box[1].length, 15)
        self.assertEqual(jp2.box[2].box[1].longname, 'Colour Specification')
        self.assertEqual(jp2.box[2].box[1].precedence, 0)
        self.assertEqual(jp2.box[2].box[1].approximation, 0)
        self.assertEqual(jp2.box[2].box[1].colorspace, glymur.core.SRGB)
        self.assertIsNone(jp2.box[2].box[1].icc_profile)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_wrap(self):
        j2k = Jp2k(self.j2kfile)
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name)
            self.verify_wrapped_raw(tfile.name)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_wrap_jp2(self):
        j2k = Jp2k(self.jp2file)
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            jp2 = j2k.wrap(tfile.name)
        boxes = [box.box_id for box in jp2.box]
        self.assertEqual(boxes, ['jP  ', 'ftyp', 'jp2h', 'jp2c'])

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_default_layout_but_with_specified_boxes(self):
        j2k = Jp2k(self.j2kfile)
        boxes = [JPEG2000SignatureBox(),
                 FileTypeBox(),
                 JP2HeaderBox(),
                 ContiguousCodestreamBox()]
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)
        boxes[2].box = [ImageHeaderBox(height=height,
                                       width=width,
                                       num_components=num_components),
                        ColourSpecificationBox(colorspace=glymur.core.SRGB)]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            j2k.wrap(tfile.name, boxes=boxes)
            self.verify_wrapped_raw(tfile.name)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_image_header_box_not_first_in_jp2_header(self):
        # The specification says that ihdr must be the first box in jp2h.
        j2k = Jp2k(self.j2kfile)
        boxes = [JPEG2000SignatureBox(),
                 FileTypeBox(),
                 JP2HeaderBox(),
                 ContiguousCodestreamBox()]
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)
        boxes[2].box = [ColourSpecificationBox(colorspace=glymur.core.SRGB),
                        ImageHeaderBox(height=height,
                                       width=width,
                                       num_components=num_components)]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_first_2_boxes_not_jP_and_ftyp(self):
        j2k = Jp2k(self.j2kfile)
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)

        jP = JPEG2000SignatureBox()
        ftyp = FileTypeBox()
        jp2h = JP2HeaderBox()
        jp2c = ContiguousCodestreamBox()
        colr = ColourSpecificationBox(colorspace=glymur.core.SRGB)
        ihdr = ImageHeaderBox(height=height, width=width,
                              num_components=num_components)
        jp2h.box = [ihdr, colr]
        boxes = [ftyp, jP, jp2h, jp2c]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_jp2h_not_preceeding_jp2c(self):
        j2k = Jp2k(self.j2kfile)
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)

        jP = JPEG2000SignatureBox()
        ftyp = FileTypeBox()
        jp2h = JP2HeaderBox()
        jp2c = ContiguousCodestreamBox()
        colr = ColourSpecificationBox(colorspace=glymur.core.SRGB)
        ihdr = ImageHeaderBox(height=height, width=width,
                              num_components=num_components)
        jp2h.box = [ihdr, colr]
        boxes = [jP, ftyp, jp2c, jp2h]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)

    @unittest.skipIf(os.name == "nt", "Temporary file issue on window.")
    def test_missing_codestream(self):
        j2k = Jp2k(self.j2kfile)
        c = j2k.get_codestream()
        height = c.segment[1].ysiz
        width = c.segment[1].xsiz
        num_components = len(c.segment[1].xrsiz)

        jP = JPEG2000SignatureBox()
        ftyp = FileTypeBox()
        jp2h = JP2HeaderBox()
        ihdr = ImageHeaderBox(height=height, width=width,
                              num_components=num_components)
        jp2h.box = [ihdr]
        boxes = [jP, ftyp, jp2h]
        with tempfile.NamedTemporaryFile(suffix=".jp2") as tfile:
            with self.assertRaises(IOError):
                j2k.wrap(tfile.name, boxes=boxes)


class TestJp2Boxes(unittest.TestCase):

    def test_default_JPEG2000SignatureBox(self):
        # Should be able to instantiate a JPEG2000SignatureBox
        b = glymur.jp2box.JPEG2000SignatureBox()
        self.assertEqual(b.signature, (13, 10, 135, 10))

    def test_default_FileTypeBox(self):
        # Should be able to instantiate a FileTypeBox
        b = glymur.jp2box.FileTypeBox()
        self.assertEqual(b.brand, 'jp2 ')
        self.assertEqual(b.minor_version, 0)
        self.assertEqual(b.compatibility_list, ['jp2 '])

    def test_default_ImageHeaderBox(self):
        # Should be able to instantiate an image header box.
        b = glymur.jp2box.ImageHeaderBox(height=512, width=256,
                                         num_components=3)
        self.assertEqual(b.height,  512)
        self.assertEqual(b.width,  256)
        self.assertEqual(b.num_components,  3)
        self.assertEqual(b.bits_per_component, 8)
        self.assertFalse(b.signed)
        self.assertFalse(b.colorspace_unknown)

    def test_default_JP2HeaderBox(self):
        b1 = JP2HeaderBox()
        b1.box = [ImageHeaderBox(height=512, width=256),
                  ColourSpecificationBox(colorspace=glymur.core.GREYSCALE)]

    def test_default_ContiguousCodestreamBox(self):
        b = ContiguousCodestreamBox()
        self.assertEqual(b.box_id, 'jp2c')
        self.assertIsNone(b.main_header)


class TestJpxBoxes(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(format_corpus_data_root is None,
                     "FORMAT_CORPUS_DATA_ROOT environment variable not set")
    def test_codestream_header(self):
        # Should recognize codestream header box.
        jfile = os.path.join(format_corpus_data_root,
                             'jp2k-formats/balloon.jpf')
        jpx = Jp2k(jfile)

        # This superbox just happens to be empty.
        self.assertEqual(jpx.box[4].box_id, 'jpch')
        self.assertEqual(len(jpx.box[4].box), 0)

    @unittest.skipIf(format_corpus_data_root is None,
                     "FORMAT_CORPUS_DATA_ROOT environment variable not set")
    def test_compositing_layer_header(self):
        # Should recognize compositing layer header box.
        jfile = os.path.join(format_corpus_data_root,
                             'jp2k-formats/balloon.jpf')
        jpx = Jp2k(jfile)

        # This superbox just happens to be empty.
        self.assertEqual(jpx.box[5].box_id, 'jplh')
        self.assertEqual(len(jpx.box[5].box), 0)


if __name__ == "__main__":
    unittest.main()
