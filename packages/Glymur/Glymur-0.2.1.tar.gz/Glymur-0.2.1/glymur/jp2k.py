"""Access to JPEG2000 files.

License:  MIT
"""

# pylint: disable=C0302

import sys
if sys.hexversion >= 0x03030000:
    from contextlib import ExitStack
else:
    from contextlib2 import ExitStack
import ctypes
import math
import os
import struct
import warnings

import numpy as np

from .codestream import Codestream
from .core import SRGB
from .core import GREYSCALE
from .core import PROGRESSION_ORDER
from .jp2box import Jp2kBox
from .jp2box import JPEG2000SignatureBox
from .jp2box import FileTypeBox
from .jp2box import JP2HeaderBox
from .jp2box import ContiguousCodestreamBox
from .jp2box import ImageHeaderBox
from .jp2box import ColourSpecificationBox
from .lib import _openjpeg as _opj
from .lib import _openjp2 as _opj2

_COLORSPACE_MAP = {'rgb': _opj2.CLRSPC_SRGB,
                   'gray': _opj2.CLRSPC_GRAY,
                   'grey': _opj2.CLRSPC_GRAY,
                   'ycc': _opj2.CLRSPC_YCC}

# Setup the default callback handlers.  See the callback functions subsection
# in the ctypes section of the Python documentation for a solid explanation of
# what's going on here.
_CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p)


def _default_error_handler(msg, _):
    """Default error handler callback for openjpeg library."""
    msg = "OpenJPEG library error:  {0}".format(msg.decode('utf-8').rstrip())
    _opj2.set_error_message(msg)


def _default_info_handler(msg, _):
    """Default info handler callback for openjpeg library."""
    print("[INFO] {0}".format(msg.decode('utf-8').rstrip()))


def _default_warning_handler(library_msg, _):
    """Default warning handler callback for openjpeg library."""
    library_msg = library_msg.decode('utf-8').rstrip()
    msg = "OpenJPEG library warning:  {0}".format(library_msg)
    warnings.warn(msg)

_ERROR_CALLBACK = _CMPFUNC(_default_error_handler)
_INFO_CALLBACK = _CMPFUNC(_default_info_handler)
_WARNING_CALLBACK = _CMPFUNC(_default_warning_handler)


class Jp2k(Jp2kBox):
    """JPEG 2000 file.

    Attributes
    ----------
    filename : str
        The path to the JPEG 2000 file.
    mode : str
        The mode used to open the file.
    box : sequence
        List of top-level boxes in the file.  Each box may in turn contain
        its own list of boxes.  Will be empty if the file consists only of a
        raw codestream.
    """

    def __init__(self, filename, mode='rb'):
        """
        Parameters
        ----------
        filename : str or file
            The path to JPEG 2000 file.
        mode : str, optional
            The mode used to open the file.
        """
        Jp2kBox.__init__(self)
        self.filename = filename
        self.mode = mode
        self.box = []
        self._codec_format = None
        self._file_size = 0

        # Parse the file for JP2/JPX contents only if we are reading it.
        if mode == 'rb':
            self.parse()

    def __str__(self):
        metadata = ['File:  ' + os.path.basename(self.filename)]
        if len(self.box) > 0:
            for box in self.box:
                metadata.append(str(box))
        else:
            codestream = self.get_codestream()
            metadata.append(str(codestream))
        return '\n'.join(metadata)

    def parse(self):
        """Parses the JPEG 2000 file.

        Raises
        ------
        IOError
            The file was not JPEG 2000.
        """
        stat = os.stat(self.filename)
        self.length = stat.st_size
        self._file_size = stat.st_size

        with open(self.filename, 'rb') as fptr:

            # Make sure we have a JPEG2000 file.  It could be either JP2 or
            # J2C.  Check for J2C first, single box in that case.
            read_buffer = fptr.read(2)
            signature, = struct.unpack('>H', read_buffer)
            if signature == 0xff4f:
                self._codec_format = _opj2.CODEC_J2K
                # That's it, we're done.  The codestream object is only
                # produced upon explicit request.
                return

            self._codec_format = _opj2.CODEC_JP2

            # Should be JP2.
            # First 4 bytes should be 12, the length of the 'jP  ' box.
            # 2nd 4 bytes should be the box ID ('jP  ').
            # 3rd 4 bytes should be the box signature (13, 10, 135, 10).
            fptr.seek(0)
            read_buffer = fptr.read(12)
            values = struct.unpack('>I4s4B', read_buffer)
            box_length = values[0]
            box_id = values[1]
            signature = values[2:]
            if (((box_length != 12) or (box_id != b'jP  ') or
                 (signature != (13, 10, 135, 10)))):
                msg = '{0} is not a JPEG 2000 file.'.format(self.filename)
                raise IOError(msg)

            # Back up and start again, we know we have a superbox (box of
            # boxes) here.
            fptr.seek(0)
            self.box = self.parse_superbox(fptr)

    # pylint:  disable-msg=W0221
    def write(self, img_array, cratios=None, eph=False, psnr=None, numres=None,
              cbsize=None, psizes=None, grid_offset=None, sop=False,
              subsam=None, tilesize=None, prog=None, modesw=None,
              colorspace=None, verbose=False, mct=None):
        """Write image data to a JP2/JPX/J2k file.  Intended usage of the
        various parameters follows that of OpenJPEG's opj_compress utility.

        This method can only be used to create JPEG 2000 images that can fit
        in memory.

        Parameters
        ----------
        img_array : ndarray
            Image data to be written to file.
        callbacks : bool, optional
            If true, enable default info handler such that INFO messages
            produced by the OpenJPEG library are output to the console.  By
            default, OpenJPEG warning and error messages are captured by
            Python's own warning and error mechanisms.
        cbsize : tuple, optional
            Code block size (DY, DX).
        colorspace : str, optional
            Either 'rgb' or 'gray'.
        cratios : sequence, optional
            Compression ratios for successive layers.
        eph : bool, optional
            If true, write SOP marker after each header packet.
        grid_offset : tuple, optional
            Offset (DY, DX) of the origin of the image in the reference grid.
        mct : bool, optional
            Specifies usage of the multi component transform.  If not
            specified, defaults to True if the colorspace is RGB.
        modesw : int, optional
            Mode switch.
                1 = BYPASS(LAZY)
                2 = RESET
                4 = RESTART(TERMALL)
                8 = VSC
                16 = ERTERM(SEGTERM)
                32 = SEGMARK(SEGSYM)
        numres : int, optional
            Number of resolutions.
        prog : str, optional
            Progression order, one of "LRCP" "RLCP", "RPCL", "PCRL", "CPRL".
        psnr : list, optional
            Different PSNR for successive layers.
        psizes : list, optional
            List of precinct sizes.  Each precinct size tuple is defined in
            (height x width).
        sop : bool, optional
            If true, write SOP marker before each packet.
        subsam : tuple, optional
            Subsampling factors (dy, dx).
        tilesize : tuple, optional
            Numeric tuple specifying tile size in terms of (numrows, numcols),
            not (X, Y).
        verbose : bool, optional
            Print informational messages produced by the OpenJPEG library.

        Examples
        --------
        >>> import glymur
        >>> jfile = glymur.data.nemo()
        >>> jp2 = glymur.Jp2k(jfile)
        >>> data = jp2.read(rlevel=1)
        >>> from tempfile import NamedTemporaryFile
        >>> tfile = NamedTemporaryFile(suffix='.jp2', delete=False)
        >>> j = Jp2k(tfile.name, mode='wb')
        >>> j.write(data.astype(np.uint8))
        """

        cparams = _opj2.set_default_encoder_parameters()

        outfile = self.filename.encode()
        num_pad_bytes = _opj2.PATH_LEN - len(outfile)
        outfile += b'0' * num_pad_bytes
        cparams.outfile = outfile

        if self.filename[-4:].lower() == '.jp2':
            codec_fmt = _opj2.CODEC_JP2
        else:
            codec_fmt = _opj2.CODEC_J2K

        cparams.cod_format = codec_fmt

        # Set defaults to lossless to begin.
        cparams.tcp_rates[0] = 0
        cparams.tcp_numlayers = 1
        cparams.cp_disto_alloc = 1

        if cbsize is not None:
            width = cbsize[1]
            height = cbsize[0]
            if height * width > 4096 or height < 4 or width < 4:
                msg = "Code block area cannot exceed 4096.  "
                msg += "Code block height and width must be larger than 4."
                raise RuntimeError(msg)
            if ((math.log(height, 2) != math.floor(math.log(height, 2)) or
                 math.log(width, 2) != math.floor(math.log(width, 2)))):
                msg = "Bad code block size ({0}, {1}), "
                msg += "must be powers of 2."
                raise IOError(msg.format(height, width))
            cparams.cblockw_init = width
            cparams.cblockh_init = height

        if cratios is not None:
            cparams.tcp_numlayers = len(cratios)
            for j, cratio in enumerate(cratios):
                cparams.tcp_rates[j] = cratio
            cparams.cp_disto_alloc = 1

        if eph:
            cparams.csty |= 0x04

        if grid_offset is not None:
            cparams.image_offset_x0 = grid_offset[1]
            cparams.image_offset_y0 = grid_offset[0]

        if modesw is not None:
            for shift in range(6):
                power_of_two = 1 << shift
                if modesw & power_of_two:
                    cparams.mode |= power_of_two

        if numres is not None:
            cparams.numresolution = numres

        if prog is not None:
            prog = prog.upper()
            cparams.prog_order = PROGRESSION_ORDER[prog]

        if psnr is not None:
            cparams.tcp_numlayers = len(psnr)
            for j, snr_layer in enumerate(psnr):
                cparams.tcp_distoratio[j] = snr_layer
            cparams.cp_fixed_quality = 1

        if psizes is not None:
            for j, (prch, prcw) in enumerate(psizes):
                if j == 0 and cbsize is not None:
                    cblkh, cblkw = cbsize
                    if cblkh * 2 > prch or cblkw * 2 > prcw:
                        msg = "Highest Resolution precinct size must be at "
                        msg += "least twice that of the code block dimensions."
                        raise IOError(msg)
                if ((math.log(prch, 2) != math.floor(math.log(prch, 2)) or
                     math.log(prcw, 2) != math.floor(math.log(prcw, 2)))):
                    msg = "Bad precinct sizes ({0}, {1}), "
                    msg += "must be powers of 2."
                    raise IOError(msg.format(prch, prcw))

                cparams.prcw_init[j] = prcw
                cparams.prch_init[j] = prch
            cparams.csty |= 0x01
            cparams.res_spec = len(psizes)

        if sop:
            cparams.csty |= 0x02

        if subsam is not None:
            cparams.subsampling_dy = subsam[0]
            cparams.subsampling_dx = subsam[1]

        if tilesize is not None:
            cparams.cp_tdx = tilesize[1]
            cparams.cp_tdy = tilesize[0]
            cparams.tile_size_on = _opj2.TRUE

        if cratios is not None and psnr is not None:
            msg = "Cannot specify cratios and psnr together."
            raise RuntimeError(msg)

        if img_array.ndim == 2:
            numrows, numcols = img_array.shape
            img_array = img_array.reshape(numrows, numcols, 1)
        elif img_array.ndim == 3:
            pass
        else:
            msg = "{0}D imagery is not allowed.".format(img_array.ndim)
            raise IOError(msg)

        numrows, numcols, num_comps = img_array.shape

        if colorspace is None:
            if img_array.shape[2] == 1 or img_array.shape[2] == 2:
                colorspace = _opj2.CLRSPC_GRAY
            else:
                # No YCC unless specifically told to do so.
                colorspace = _opj2.CLRSPC_SRGB
        else:
            if codec_fmt == _opj2.CODEC_J2K:
                raise IOError('Do not specify a colorspace with J2K.')
            colorspace = colorspace.lower()
            if colorspace not in ('rgb', 'grey', 'gray'):
                msg = 'Invalid colorspace "{0}"'.format(colorspace)
                raise IOError(msg)
            elif colorspace == 'rgb' and img_array.shape[2] < 3:
                msg = 'RGB colorspace requires at least 3 components.'
                raise IOError(msg)
            else:
                colorspace = _COLORSPACE_MAP[colorspace]

        if mct is None:
            if colorspace == _opj2.CLRSPC_SRGB:
                cparams.tcp_mct = 1
            else:
                cparams.tcp_mct = 0
        else:
            if mct and colorspace == _opj2.CLRSPC_GRAY:
                msg = "Cannot specify usage of the multi component transform "
                msg += "if the colorspace is gray."
                raise IOError(msg)
            cparams.tcp_mct = 1 if mct else 0

        if img_array.dtype == np.uint8:
            comp_prec = 8
        elif img_array.dtype == np.uint16:
            comp_prec = 16
        else:
            raise RuntimeError("unhandled datatype")

        comptparms = (_opj2.ImageComptParmType * num_comps)()
        for j in range(num_comps):
            comptparms[j].dx = cparams.subsampling_dx
            comptparms[j].dy = cparams.subsampling_dy
            comptparms[j].w = numcols
            comptparms[j].h = numrows
            comptparms[j].x0 = cparams.image_offset_x0
            comptparms[j].y0 = cparams.image_offset_y0
            comptparms[j].prec = comp_prec
            comptparms[j].bpp = comp_prec
            comptparms[j].sgnd = 0

        image = _opj2.image_create(comptparms, colorspace)

        # set image offset and reference grid
        image.contents.x0 = cparams.image_offset_x0
        image.contents.y0 = cparams.image_offset_y0
        image.contents.x1 = (image.contents.x0 +
                             (numcols - 1) * cparams.subsampling_dx + 1)
        image.contents.y1 = (image.contents.y0 +
                             (numrows - 1) * cparams.subsampling_dy + 1)

        # Stage the image data to the openjpeg data structure.
        for k in range(0, num_comps):
            layer = np.ascontiguousarray(img_array[:, :, k], dtype=np.int32)
            dest = image.contents.comps[k].data
            src = layer.ctypes.data
            ctypes.memmove(dest, src, layer.nbytes)

        codec = _opj2.create_compress(codec_fmt)

        if verbose:
            _opj2.set_info_handler(codec, _INFO_CALLBACK)
        else:
            _opj2.set_info_handler(codec, None)

        _opj2.set_warning_handler(codec, _WARNING_CALLBACK)
        _opj2.set_error_handler(codec, _ERROR_CALLBACK)
        _opj2.setup_encoder(codec, cparams, image)
        strm = _opj2.stream_create_default_file_stream_v3(self.filename, False)
        _opj2.start_compress(codec, image, strm)
        _opj2.encode(codec, strm)
        _opj2.end_compress(codec, strm)
        _opj2.stream_destroy_v3(strm)
        _opj2.destroy_codec(codec)
        _opj2.image_destroy(image)

        self.parse()

    def wrap(self, filename, boxes=None):
        """Write the codestream back out to file, wrapped in new JP2 jacket.

        Parameters
        ----------
        filename : str
            JP2 file to be created from a raw codestream.
        boxes : list
            JP2 box definitions to define the JP2 file format.  If not
            provided, a default ""jacket" is assumed, consisting of JP2
            signature, file type, JP2 header, and contiguous codestream boxes.

        Returns
        -------
        jp2 : Jp2k object
            Newly wrapped Jp2k object.

        Examples
        --------
        >>> import glymur, tempfile
        >>> jfile = glymur.data.goodstuff()
        >>> j2k = glymur.Jp2k(jfile)
        >>> tfile = tempfile.NamedTemporaryFile(suffix='jp2')
        >>> jp2 = j2k.wrap(tfile.name)
        """
        if boxes is None:
            # Try to create a reasonable default.
            boxes = [JPEG2000SignatureBox(),
                     FileTypeBox(),
                     JP2HeaderBox(),
                     ContiguousCodestreamBox()]
            codestream = self.get_codestream()
            height = codestream.segment[1].ysiz
            width = codestream.segment[1].xsiz
            num_components = len(codestream.segment[1].xrsiz)
            boxes[2].box = [ImageHeaderBox(height=height,
                                           width=width,
                                           num_components=num_components),
                            ColourSpecificationBox(colorspace=SRGB)]

        # Check for a bad sequence of boxes.
        # 1st two boxes must be 'jP  ' and 'ftyp'
        if boxes[0].box_id != 'jP  ' or boxes[1].box_id != 'ftyp':
            msg = "The first box must be the signature box and the second "
            msg += "must be the file type box."
            raise IOError(msg)

        # jp2c must be preceeded by jp2h
        jp2h_lst = [idx for (idx, box) in enumerate(boxes)
                    if box.box_id == 'jp2h']
        jp2h_idx = jp2h_lst[0]
        jp2c_lst = [idx for (idx, box) in enumerate(boxes)
                    if box.box_id == 'jp2c']
        if len(jp2c_lst) == 0:
            msg = "A codestream box must be defined in the outermost "
            msg += "list of boxes."
            raise IOError(msg)

        jp2c_idx = jp2c_lst[0]
        if jp2h_idx >= jp2c_idx:
            msg = "The codestream box must be preceeded by a jp2 header box."
            raise IOError(msg)

        # 1st jp2 header box must be ihdr
        jp2h = boxes[jp2h_idx]
        if jp2h.box[0].box_id != 'ihdr':
            msg = "The first box in the jp2 header box must be the image "
            msg += "header box."
            raise IOError(msg)

        # colr must be present in jp2 header box.
        colr_lst = [j for (j, box) in enumerate(jp2h.box)
                    if box.box_id == 'colr']
        if len(colr_lst) == 0:
            msg = "The jp2 header box must contain a color definition box."
            raise IOError(msg)
        colr = jp2h.box[colr_lst[0]]

        # Any cdef box must be in the jp2 header following the image header.
        cdef_lst = [j for (j, box) in enumerate(boxes) if box.box_id == 'cdef']
        if len(cdef_lst) != 0:
            msg = "Any channel defintion box must be in the JP2 header "
            msg += "following the image header."
            raise IOError(msg)

        cdef_lst = [j for (j, box) in enumerate(jp2h.box)
                    if box.box_id == 'cdef']
        if len(cdef_lst) > 1:
            msg = "Only one channel definition box is allowed in the "
            msg += "JP2 header."
            raise IOError(msg)
        elif len(cdef_lst) == 1:
            cdef = jp2h.box[cdef_lst[0]]
            assn = cdef.association
            typ = cdef.channel_type
            if colr.colorspace == SRGB:
                if any([chan + 1 not in assn or typ[chan] != 0
                        for chan in [0, 1, 2]]):
                    msg = "All color channels must be defined in the "
                    msg += "channel definition box."
                    raise IOError(msg)
            elif colr.colorspace == GREYSCALE:
                if 0 not in typ:
                    msg = "All color channels must be defined in the "
                    msg += "channel definition box."
                    raise IOError(msg)

        with open(filename, 'wb') as ofile:
            for box in boxes:
                if box.box_id != 'jp2c':
                    box.write(ofile)
                else:
                    # The codestream gets written last.
                    if len(self.box) == 0:
                        # Am I a raw codestream?  If so, then it is pretty
                        # easy, just write the codestream box header plus all
                        # of myself out to file.
                        ofile.write(struct.pack('>I', self.length + 8))
                        ofile.write('jp2c'.encode())
                        with open(self.filename, 'rb') as ifile:
                            ofile.write(ifile.read())
                    else:
                        # OK, I'm a jp2 file.  Need to find out where the
                        # raw codestream actually starts.
                        jp2c = [box for box in self.box
                                if box.box_id == 'jp2c']
                        jp2c = jp2c[0]
                        ofile.write(struct.pack('>I', jp2c.length + 8))
                        ofile.write('jp2c'.encode())
                        with open(self.filename, 'rb') as ifile:
                            # Seek 8 bytes past the L, T fields to get to the
                            # raw codestream.
                            ifile.seek(jp2c.offset + 8)
                            ofile.write(ifile.read(jp2c.length - 8))

            ofile.flush()

        jp2 = Jp2k(filename)
        return jp2

    def read(self, **kwargs):
        """Read a JPEG 2000 image.

        Parameters
        ----------
        rlevel : int, optional
            Factor by which to rlevel output resolution.  Use -1 to get the
            lowest resolution thumbnail.  This is the only keyword option
            available to use when only OpenJPEG version 1.5.1 is present.
        layer : int, optional
            Number of quality layer to decode.
        area : tuple, optional
            Specifies decoding image area,
            (first_row, first_col, last_row, last_col)
        tile : int, optional
            Number of tile to decode.
        verbose : bool, optional
            Print informational messages produced by the OpenJPEG library.

        Returns
        -------
        img_array : ndarray
            The image data.

        Raises
        ------
        IOError
            If the image has differing subsample factors.

        Examples
        --------
        >>> import glymur
        >>> jfile = glymur.data.nemo()
        >>> jp = glymur.Jp2k(jfile)
        >>> image = jp.read()
        >>> image.shape
        (1456, 2592, 3)

        Read the lowest resolution thumbnail.

        >>> thumbnail = jp.read(rlevel=-1)
        >>> thumbnail.shape
        (728, 1296, 3)
        """
        if _opj2.OPENJP2 is not None:
            img = self._read_openjp2(**kwargs)
        else:
            img = self._read_openjpeg(**kwargs)
        return img

    def _read_openjpeg(self, rlevel=0, verbose=False):
        """Read a JPEG 2000 image using libopenjpeg.

        Parameters
        ----------
        rlevel : int, optional
            Factor by which to rlevel output resolution.  Use -1 to get the
            lowest resolution thumbnail.
        verbose : bool, optional
            Print informational messages produced by the OpenJPEG library.

        Returns
        -------
        img_array : ndarray
            The image data.

        Raises
        ------
        RuntimeError
            If the image has differing subsample factors.
        """
        # Check for differing subsample factors.
        codestream = self.get_codestream(header_only=True)
        dxs = np.array(codestream.segment[1].xrsiz)
        dys = np.array(codestream.segment[1].yrsiz)
        if np.any(dxs - dxs[0]) or np.any(dys - dys[0]):
            msg = "Components must all have the same subsampling factors "
            msg += "to use this method with OpenJPEG 1.5.1.  Please consider "
            msg += "using OPENJP2 instead."
            raise RuntimeError(msg)

        with ExitStack() as stack:
            # Set decoding parameters.
            dparameters = _opj.DecompressionParametersType()
            _opj.set_default_decoder_parameters(ctypes.byref(dparameters))
            dparameters.cp_reduce = rlevel
            dparameters.decod_format = self._codec_format

            infile = self.filename.encode()
            nelts = _opj.PATH_LEN - len(infile)
            infile += b'0' * nelts
            dparameters.infile = infile

            dinfo = _opj.create_decompress(dparameters.decod_format)

            event_mgr = _opj.EventMgrType()
            info_handler = ctypes.cast(_INFO_CALLBACK, ctypes.c_void_p)
            event_mgr.info_handler = info_handler if verbose else None
            event_mgr.warning_handler = ctypes.cast(_WARNING_CALLBACK,
                                                    ctypes.c_void_p)
            event_mgr.error_handler = ctypes.cast(_ERROR_CALLBACK,
                                                  ctypes.c_void_p)
            _opj.set_event_mgr(dinfo, ctypes.byref(event_mgr))

            _opj.setup_decoder(dinfo, dparameters)

            with open(self.filename, 'rb') as fptr:
                src = fptr.read()
            cio = _opj.cio_open(dinfo, src)

            image = _opj.decode(dinfo, cio)

            stack.callback(_opj.image_destroy, image)
            stack.callback(_opj.destroy_decompress, dinfo)
            stack.callback(_opj.cio_close, cio)

            ncomps = image.contents.numcomps
            component = image.contents.comps[0]
            if component.sgnd:
                if component.prec <= 8:
                    dtype = np.int8
                elif component.prec <= 16:
                    dtype = np.int16
                else:
                    raise RuntimeError("Unhandled precision, datatype")
            else:
                if component.prec <= 8:
                    dtype = np.uint8
                elif component.prec <= 16:
                    dtype = np.uint16
                else:
                    raise RuntimeError("Unhandled precision, datatype")

            nrows = image.contents.comps[0].h
            ncols = image.contents.comps[0].w
            ncomps = image.contents.numcomps
            data = np.zeros((nrows, ncols, ncomps), dtype)

            for k in range(image.contents.numcomps):
                component = image.contents.comps[k]
                nrows = component.h
                ncols = component.w

                if nrows == 0 or ncols == 0:
                    # Letting this situation continue would segfault
                    # Python.
                    msg = "Component {0} has dimensions {1} x {2}"
                    msg = msg.format(k, nrows, ncols)
                    raise IOError(msg)

                addr = ctypes.addressof(component.data.contents)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    nelts = nrows * ncols
                    band = np.ctypeslib.as_array(
                        (ctypes.c_int32 * nelts).from_address(addr))
                    data[:, :, k] = np.reshape(band.astype(dtype),
                                               (nrows, ncols))

        if data.shape[2] == 1:
            data = data.view()
            data.shape = data.shape[0:2]

        return data

    def _read_openjp2(self, rlevel=0, layer=0, area=None, tile=None,
                      verbose=False):
        """Read a JPEG 2000 image using libopenjp2.

        Parameters
        ----------
        layer : int, optional
            Number of quality layer to decode.
        rlevel : int, optional
            Factor by which to rlevel output resolution.  Use -1 to get the
            lowest resolution thumbnail.
        area : tuple, optional
            Specifies decoding image area,
            (first_row, first_col, last_row, last_col)
        tile : int, optional
            Number of tile to decode.
        verbose : bool, optional
            Print informational messages produced by the OpenJPEG library.

        Returns
        -------
        img_array : ndarray
            The image data.

        Raises
        ------
        RuntimeError
            If the image has differing subsample factors.
        """
        # Check for differing subsample factors.
        codestream = self.get_codestream(header_only=True)
        dxs = np.array(codestream.segment[1].xrsiz)
        dys = np.array(codestream.segment[1].yrsiz)
        if np.any(dxs - dxs[0]) or np.any(dys - dys[0]):
            msg = "Components must all have the same subsampling factors."
            raise RuntimeError(msg)

        img_array = self._read_common(rlevel=rlevel,
                                      layer=layer,
                                      area=area,
                                      tile=tile,
                                      verbose=verbose,
                                      as_bands=False)

        if img_array.shape[2] == 1:
            img_array = img_array.view()
            img_array.shape = img_array.shape[0:2]

        return img_array

    def _read_common(self, rlevel=0, layer=0, area=None, tile=None,
                     verbose=False, as_bands=False):
        """Read a JPEG 2000 image.

        Parameters
        ----------
        layer : int, optional
            Number of quality layer to decode.
        rlevel : int, optional
            Factor by which to rlevel output resolution.
        area : tuple, optional
            Specifies decoding image area,
            (first_row, first_col, last_row, last_col)
        tile : int, optional
            Number of tile to decode.
        verbose : bool, optional
            Print informational messages produced by the OpenJPEG library.
        as_bands : bool, optional
            If true, return the individual 2D components in a list.

        Returns
        -------
        img_array : ndarray
            The individual image components or a single array.
        """
        dparam = _opj2.set_default_decoder_parameters()

        infile = self.filename.encode()
        nelts = _opj2.PATH_LEN - len(infile)
        infile += b'0' * nelts
        dparam.infile = infile

        dparam.decod_format = self._codec_format

        dparam.cp_layer = layer

        if rlevel == -1:
            # Get the lowest resolution thumbnail.
            codestream = self.get_codestream()
            rlevel = codestream.segment[2].spcod[4]

        dparam.cp_reduce = rlevel
        if area is not None:
            if area[0] < 0 or area[1] < 0:
                msg = "Upper left corner coordinates must be nonnegative:  {0}"
                msg = msg.format(area)
                raise IOError(msg)
            if area[2] <= 0 or area[3] <= 0:
                msg = "Lower right corner coordinates must be positive:  {0}"
                msg = msg.format(area)
                raise IOError(msg)
            dparam.DA_y0 = area[0]
            dparam.DA_x0 = area[1]
            dparam.DA_y1 = area[2]
            dparam.DA_x1 = area[3]

        if tile is not None:
            dparam.tile_index = tile
            dparam.nb_tile_to_decode = 1

        with ExitStack() as stack:
            stream = _opj2.stream_create_default_file_stream_v3(self.filename,
                                                                True)
            stack.callback(_opj2.stream_destroy_v3, stream)
            codec = _opj2.create_decompress(self._codec_format)
            stack.callback(_opj2.destroy_codec, codec)

            _opj2.set_error_handler(codec, _ERROR_CALLBACK)
            _opj2.set_warning_handler(codec, _WARNING_CALLBACK)
            if verbose:
                _opj2.set_info_handler(codec, _INFO_CALLBACK)
            else:
                _opj2.set_info_handler(codec, None)

            _opj2.setup_decoder(codec, dparam)
            image = _opj2.read_header(stream, codec)
            stack.callback(_opj2.image_destroy, image)

            if dparam.nb_tile_to_decode:
                _opj2.get_decoded_tile(codec, stream, image, dparam.tile_index)
            else:
                _opj2.set_decode_area(codec, image,
                                      dparam.DA_x0, dparam.DA_y0,
                                      dparam.DA_x1, dparam.DA_y1)
                _opj2.decode(codec, stream, image)
                _opj2.end_decompress(codec, stream)

            component = image.contents.comps[0]
            if component.sgnd:
                if component.prec <= 8:
                    dtype = np.int8
                elif component.prec <= 16:
                    dtype = np.int16
                else:
                    raise RuntimeError("Unhandled precision, datatype")
            else:
                if component.prec <= 8:
                    dtype = np.uint8
                elif component.prec <= 16:
                    dtype = np.uint16
                else:
                    raise RuntimeError("Unhandled precision, datatype")

            if as_bands:
                data = []
            else:
                nrows = image.contents.comps[0].h
                ncols = image.contents.comps[0].w
                ncomps = image.contents.numcomps
                data = np.zeros((nrows, ncols, ncomps), dtype)

            for k in range(image.contents.numcomps):
                component = image.contents.comps[k]
                nrows = component.h
                ncols = component.w

                if nrows == 0 or ncols == 0:
                    # Letting this situation continue would segfault
                    # Python.
                    msg = "Component {0} has dimensions {1} x {2}"
                    msg = msg.format(k, nrows, ncols)
                    raise IOError(msg)

                addr = ctypes.addressof(component.data.contents)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    band = np.ctypeslib.as_array(
                        (ctypes.c_int32 * nrows * ncols).from_address(addr))
                if as_bands:
                    data.append(np.reshape(band.astype(dtype), (nrows, ncols)))
                else:
                    data[:, :, k] = np.reshape(band.astype(dtype),
                                               (nrows, ncols))

        return data

    def read_bands(self, rlevel=0, layer=0, area=None, tile=None,
                   verbose=False):
        """Read a JPEG 2000 image.

        The only time you should use this method is when the image has
        different subsampling factors across components.  Otherwise you should
        use the read method.

        Parameters
        ----------
        layer : int, optional
            Number of quality layer to decode.
        rlevel : int, optional
            Factor by which to rlevel output resolution.
        area : tuple, optional
            Specifies decoding image area,
            (first_row, first_col, last_row, last_col)
        tile : int, optional
            Number of tile to decode.
        verbose : bool, optional
            Print informational messages produced by the OpenJPEG library.

        Returns
        -------
        lst : list
            The individual image components.

        See also
        --------
        read : read JPEG 2000 image

        Examples
        --------
        >>> import glymur
        >>> jfile = glymur.data.nemo()
        >>> jp = glymur.Jp2k(jfile)
        >>> components_lst = jp.read_bands(rlevel=1)

        Raises
        ------
        NotImplementedError
            If the openjp2 library is not available.
        """
        if _opj2.OPENJP2 is None:
            msg = "Requires openjp2 library."
            raise NotImplementedError(msg)

        lst = self._read_common(rlevel=rlevel,
                                layer=layer,
                                area=area,
                                tile=tile,
                                verbose=verbose,
                                as_bands=True)

        return lst

    def get_codestream(self, header_only=True):
        """Returns a codestream object.

        Parameters
        ----------
        header_only : bool, optional
            If True, only marker segments in the main header are parsed.
            Supplying False may impose a large performance penalty.

        Returns
        -------
        Object describing the codestream syntax.

        Examples
        --------
        >>> import glymur
        >>> jfile = glymur.data.nemo()
        >>> jp2 = glymur.Jp2k(jfile)
        >>> codestream = jp2.get_codestream()
        >>> print(codestream.segment[1])
        SIZ marker segment @ (3137, 47)
            Profile:  2
            Reference Grid Height, Width:  (1456 x 2592)
            Vertical, Horizontal Reference Grid Offset:  (0 x 0)
            Reference Tile Height, Width:  (1456 x 2592)
            Vertical, Horizontal Reference Tile Offset:  (0 x 0)
            Bitdepth:  (8, 8, 8)
            Signed:  (False, False, False)
            Vertical, Horizontal Subsampling:  ((1, 1), (1, 1), (1, 1))

        Raises
        ------
        IOError
            If the file is JPX with more than one codestream.
        """
        with open(self.filename, 'rb') as fptr:
            if self._codec_format == _opj2.CODEC_J2K:
                codestream = Codestream(fptr, header_only=header_only)
            else:
                box = [x for x in self.box if x.box_id == 'jp2c']
                if len(box) != 1:
                    msg = "JP2 files must have a single codestream."
                    raise RuntimeError(msg)
                fptr.seek(box[0].offset)
                read_buffer = fptr.read(8)
                (box_length, _) = struct.unpack('>I4s', read_buffer)
                if box_length == 1:
                    # Seek past the XL field.
                    read_buffer = fptr.read(8)
                codestream = Codestream(fptr, header_only=header_only)

            return codestream
