from tempfile import NamedTemporaryFile

import numpy as np

# Use nose for testing
from neuroimaging.externals.scipy.testing import *
from neuroimaging.utils.test_decorators import slow

from neuroimaging.core.api import Image, load_image, save_image
from neuroimaging.testing import anatfile
from neuroimaging.data_io.formats import nifti1


def default_value(fieldname):
    """Return default value from _field_defaults."""
    try:
        val = nifti1._field_defaults[fieldname]
        return val
    except KeyError:
        msg = "Nifti1 does not have default value for key '%s'" % fieldname
        raise KeyError, msg

class TestHeaderDefaults(TestCase):
    """Test default header values for nifti io."""
    def setUp(self):
        """Create a default header."""
        self.header = nifti1.create_default_header()

    def test_sizeof_hdr(self):
        key = 'sizeof_hdr'
        self.assertEqual(self.header[key], default_value(key))

    def test_scl_slope(self):
        key = 'scl_slope'
        self.assertEqual(self.header[key], default_value(key))

    def test_magic(self):
        key = 'magic'
        self.assertEqual(self.header[key], default_value(key))

    def test_pixdim(self):
        key = 'pixdim'
        self.assertEqual(self.header[key], default_value(key))

    def test_vox_offset(self):
        key = 'vox_offset'
        self.assertEqual(self.header[key], default_value(key))

class test_Nifti(TestCase):
    def setUp(self):
        self.anat = load_image(anatfile)

class test_NiftiRead(test_Nifti):
    def test_read1(self):
        imgarr = np.asarray(self.anat)
        assert_approx_equal(imgarr.min(), 1910.0)
        assert_approx_equal(imgarr.max(), 7902.0)

class test_NiftiWrite(test_Nifti):
    def setUp(self):
        print self.__class__
        super(self.__class__, self).setUp()
        self.tmpfile = NamedTemporaryFile(prefix='nifti', suffix='.nii')

    def teardown(self):
        self.tmpfile.unlink

    def test_roundtrip_affine(self):
        save_image(self.anat, self.tmpfile.name, clobber=True, dtype=np.float64)
        outimg = load_image(self.tmpfile.name)
        assert_almost_equal(outimg.affine, self.anat.affine)

    def test_roundtrip_dtype(self):
        # Test some dtypes, presume we don't need to test all as numpy
        # should catch major dtype errors?
        # uint8
        save_image(self.anat, self.tmpfile.name, clobber=True, dtype=np.uint8)
        outimg = load_image(self.tmpfile.name)
        self.assertEquals(outimg._data.dtype.type, np.uint8,
                          'Error roundtripping dtype uint8')
        # int16
        save_image(self.anat, self.tmpfile.name, clobber=True, dtype=np.int16)
        outimg = load_image(self.tmpfile.name)
        self.assertEquals(outimg._data.dtype.type, np.int16,
                          'Error roundtripping dtype int16')
        # int32
        save_image(self.anat, self.tmpfile.name, clobber=True, dtype=np.int32)
        outimg = load_image(self.tmpfile.name)
        self.assertEquals(outimg._data.dtype.type, np.int32,
                          'Error roundtripping dtype int32')
        # float32
        save_image(self.anat, self.tmpfile.name, clobber=True, dtype=np.float32)
        outimg = load_image(self.tmpfile.name)
        self.assertEquals(outimg._data.dtype.type, np.float32,
                          'Error roundtripping dtype float32')
        # float64
        save_image(self.anat, self.tmpfile.name, clobber=True, dtype=np.float64)
        outimg = load_image(self.tmpfile.name)
        self.assertEquals(outimg._data.dtype.type, np.float64,
                          'Error roundtripping dtype float64')
        
## Comment out old tests for now...
"""
class test_NiftiDataType(test_Nifti):

    @slow
    def test_datatypes(self):
        for sctype in nifti1.sctype2datatype.keys():
            _out = np.ones(self.anatfile.grid.shape, sctype)
            out = Image(_out, self.anatfile.grid)
            save_image(out, 'out.nii', clobber=True)
            new = load_image('out.nii')
            self.assertEquals(new.fmt.header['datatype'],
                              nifti1.sctype2datatype[sctype])
            self.assertEquals(new.fmt.dtype.type, sctype)
            self.assertEquals(new.fmt.header['vox_offset'], 352)
            self.assertEquals(os.stat('out.nii').st_size,
                              np.product(self.image.grid.shape) *
                              _out.dtype.itemsize +
                              new.fmt.header['vox_offset'])
            np.testing.assert_almost_equal(np.asarray(new), _out)
        os.remove('out.nii')

    @slow
    def test_datatypes2(self):
        for sctype in nifti1.sctype2datatype.keys():
            for _sctype in nifti1.sctype2datatype.keys():
                _out = np.ones(self.anatfile.grid.shape, sctype)
                out = Image(_out, self.anatfile.grid)
                save_image(out, 'out.nii', clobber=True)
                new = load_image('out.nii')
                self.assertEquals(new.fmt.header['datatype'],
                                  nifti1.sctype2datatype[_sctype])
                self.assertEquals(new.fmt.dtype.type, _sctype)
                self.assertEquals(new.fmt.header['vox_offset'], 352.0)
                self.assertEquals(os.stat('out.nii').st_size,
                                  np.product(self.image.grid.shape) *
                                  np.dtype(_sctype).itemsize +
                                  new.fmt.header['vox_offset'])
                np.testing.assert_almost_equal(np.asarray(new), _out)

        os.remove('out.nii')
"""

if __name__ == '__main__':
    # usage: nosetests -sv test_nifti1.py
    nose.runmodule()