#
# RGBMap.py -- color mapping
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import math
import numpy

from ginga.misc import Callback

class RGBMapError(Exception):
    pass

class RGBImage(object):
    def __init__(self, **kwdargs):
        self.__dict__.update(kwdargs)
    
class RGBMapper(Callback.Callbacks):

    def __init__(self):
        Callback.Callbacks.__init__(self)

        # For color and intensity maps
        self.cmap = None
        self.imap = None
        self.arr = None
        self.iarr = None
        self.carr = None
        self.sarr = None

        # For color scale algorithms
        self.hashalgs = { 'linear': self.calc_linear_hash,
                          'logarithmic': self.calc_logarithmic_hash,
                          'exponential': self.calc_exponential_hash,
                          }
        self.hashalg = 'linear'
        self.maxhashsize = 1024*1024
        self.hashsize = 65536
        self.expo = 10.0
        self.calc_hash()

        # For callbacks
        for name in ('changed', ):
            self.enable_callback(name)

    def set_cmap(self, cmap, callback=True):
        self.cmap = cmap
        self.calc_cmap()
        self.recalc(callback=callback)

    def get_cmap(self):
        return self.cmap
    
    def calc_cmap(self):
        clst = self.cmap.clst
        arr = numpy.array(clst).transpose() * 255.0
        #self.carr = arr.astype('uint8')
        self.carr = numpy.round(arr).astype('uint8')

    def get_rgb(self, index):
        return tuple(self.arr[index])

    def get_rgbval(self, index):
        assert (index >= 0) and (index < 256), \
               RGBMapError("Index must be in range 0-255 !")
        index = self.sarr[index].clip(0, 255)
        return (self.arr[0][index],
                self.arr[1][index],
                self.arr[2][index])

    def set_imap(self, imap, callback=True):
        self.imap = imap
        self.calc_imap()
        self.recalc(callback=callback)

    def get_imap(self):
        return self.imap
    
    def calc_imap(self):
        arr = numpy.array(self.imap.ilst) * 255.0
        self.iarr = numpy.round(arr).astype('uint')

    def reset_sarr(self, callback=True):
        self.sarr = numpy.array(range(256))
        if callback:
            self.make_callback('changed')

    def set_sarr(self, sarr, callback=True):
        assert len(sarr) == 256, \
               RGBMapError("shift map length %d != 256" % (len(sarr)))
        self.sarr = sarr.astype('uint')

        if callback:
            self.make_callback('changed')

    def get_sarr(self):
        return self.sarr
    
    def recalc(self, callback=True):
        self.arr = numpy.copy(self.carr)
        # Apply intensity map to rearrange colors
        if self.iarr != None:
            idx = self.iarr
            self.arr[0] = self.arr[0][idx]
            self.arr[1] = self.arr[1][idx]
            self.arr[2] = self.arr[2][idx]

        self.reset_sarr(callback=callback)
        
    def get_hash_size(self):
        return self.hashsize

    def set_hash_size(self, size, callback=True):
        assert (size >= 256) and (size <= self.maxhashsize), \
               RGBMapError("Bad hash size!")
        self.hashsize = size
        self.calc_hash()
        if callback:
            self.make_callback('changed')
    
    def get_hash_algorithms(self):
        return self.hashalgs.keys()
    
    def get_hash_algorithm(self):
        return self.hashalg
    
    def set_hash_algorithm(self, name, callback=True):
        if not name in self.hashalgs.keys():
            raise RGBMapError("Invalid hash algorithm '%s'" % (name))
        self.hashalg = name
        self.calc_hash()
        if callback:
            self.make_callback('changed')
    
    def _get_rgbarray(self, idx):
        # NOTE: data is assumed to be in the range 0-255 at this point
        # but clip as a precaution
        idx = idx.clip(0, 255)
        # run it through the shift array
        idx = self.sarr[idx].clip(0, 255)
        ar = self.arr[0][idx]
        ag = self.arr[1][idx]
        ab = self.arr[2][idx]
        return (ar, ag, ab)
        
    def _get_rgbarray_rgb(self, idx_r, idx_g, idx_b):
        # NOTE: data is assumed to be in the range 0-255 at this point
        # but clip as a precaution
        idx_r = idx_r.clip(0, 255)
        idx_r = self.sarr[idx_r].clip(0, 255)
        ar = self.arr[0][idx_r]
        idx_g = idx_g.clip(0, 255)
        idx_g = self.sarr[idx_g].clip(0, 255)
        ag = self.arr[1][idx_g]
        idx_b = idx_b.clip(0, 255)
        idx_b = self.sarr[idx_b].clip(0, 255)
        ab = self.arr[2][idx_b]
        return (ar, ag, ab)

    def get_rgbarray(self, idx):
        shape = idx.shape
        if len(shape) == 2:
            # 2D monochrome image
            idx = self.get_hasharray(idx)
            ar, ag, ab = self._get_rgbarray(idx)
        elif len(shape) == 3:
            # Assume 2D color image
            assert shape[2] in (3, 4), \
                   RGBMapError("Number of color channels != 3")
            idx_r = self.get_hasharray(idx[:, :, 0])
            idx_g = self.get_hasharray(idx[:, :, 1])
            idx_b = self.get_hasharray(idx[:, :, 2])
            # alpha channel is usually 3
            ar, ag, ab = self._get_rgbarray_rgb(idx_r, idx_g, idx_b)

        ht, wd = ab.shape
        aa = numpy.zeros((ht, wd), dtype=numpy.uint8)
        aa.fill(255)

        res = RGBImage(a=aa, r=ar, g=ag, b=ab)
        return res
        
    
    def get_hasharray(self, idx):
        # NOTE: data is assumed to be in the range 0..hashsize-1 at this point
        # but clip as a precaution
        idx = idx.clip(0, self.hashsize-1)
        arr = self.hash[idx]
        return arr
        
    # def rshift(self, pct, callback=True):
    #     self.reset_sarr()
    #     num = int(255.0 * pct)
    #     arr = numpy.roll(self.sarr, num)
    #     arr[0:num] = 0
    #     self.sarr = arr
    #     if callback:
    #         self.make_callback('changed')
            
    # def lshift(self, pct, callback=True):
    #     self.reset_sarr()
    #     num = int(255.0 * pct)
    #     arr = numpy.roll(self.sarr, -num)
    #     arr[256-num:256] = 255
    #     self.sarr = arr
    #     if callback:
    #         self.make_callback('changed')

    def _shift(self, sarr, pct, rotate=False):
        n = len(sarr)
        num = int(n * pct)
        arr = numpy.roll(sarr, num)
        if not rotate:
            if num > 0:
                arr[0:num] = sarr[0]
            elif num < 0:
                arr[n+num:n] = sarr[-1]
        return arr

    def _stretch(self, sarr, scale):
        old_wd = len(sarr)
        new_wd = int(round(scale * old_wd))

        # Is there a more efficient way to do this?
        xi = numpy.mgrid[0:new_wd]
        iscale_x = float(old_wd) / float(new_wd)
            
        xi *= iscale_x 
        xi = xi.astype('int').clip(0, old_wd-1)
        newdata = sarr[xi]
        return newdata
    
    def shift(self, pct, rotate=False, callback=True):
        work = self._shift(self.sarr, pct, rotate=rotate)
        assert len(work) == 256, \
               RGBMapError("shifted shift map is != 256")
        self.sarr = work
        if callback:
            self.make_callback('changed')
        
    def scaleNshift(self, scale_pct, shift_pct, callback=True):
        """Stretch and/or shrink the color map via altering the shift map.
        """
        self.reset_sarr(callback=False)
        
        #print "amount=%.2f location=%.2f" % (scale_pct, shift_pct)
        # limit shrinkage to 5% of original size
        scale = max(scale_pct, 0.050)

        work = self._stretch(self.sarr, scale)
        n = len(work)
        if n < 256:
            # pad on the lowest and highest values of the shift map
            m = (256 - n) // 2 + 1
            barr = numpy.array([0]*m)
            tarr = numpy.array([255]*m)
            work = numpy.concatenate([barr, work, tarr])
            work = work[:256]

        # we are mimicing ds9's stretch and shift algorithm here.
        # ds9 seems to cut the center out of the stretched array
        # BEFORE shifting
        n = len(work) // 2
        work = work[n-128:n+128].astype('uint')
        assert len(work) == 256, \
               RGBMapError("scaled shift map is != 256")

        # shift map according to the shift_pct
        work = self._shift(work, shift_pct)
        assert len(work) == 256, \
               RGBMapError("shifted shift map is != 256")

        self.sarr = work
        if callback:
            self.make_callback('changed')


    # Color scale distribution algorithms are all based on similar
    # algorithms in skycat
    
    def calc_linear_hash(self):
        l = []
        step = int(round(self.hashsize / 256.0))
        for i in xrange(int(self.hashsize / step) + 1):
            l.extend([i]*step)
        l = l[:self.hashsize]
        self.hash = numpy.array(l)
        hashlen = len(self.hash)
        assert hashlen == self.hashsize, \
               RGBMapError("Computed hash table size (%d) != specified size (%d)" % (hashlen, self.hashsize))
            

    def calc_logarithmic_hash(self):
        if self.expo >= 0:
            scale = float(self.hashsize) / (math.exp(self.expo) - 1.0)
        else:
            scale = float(self.hashsize) / (1.0 - math.exp(self.expo))

        l = []
        prevstep = 0
        for i in xrange(256+1):
            if self.expo > 0:
                step = int(((math.exp((float(i) / 256.0) * self.expo) - 1.0) * scale) + 0.5)
            else:
                step = int((1.0 - math.exp((float(i) / 256.0) * self.expo) * scale) + 0.5)
            #print "step is %d delta=%d" % (step, step-prevstep)
            l.extend([i] * (step - prevstep))
            prevstep = step
        #print "length of l=%d" % (len(l))
        l = l[:self.hashsize]
        self.hash = numpy.array(l)
        hashlen = len(self.hash)
        assert hashlen == self.hashsize, \
               RGBMapError("Computed hash table size (%d) != specified size (%d)" % (hashlen, self.hashsize))

    def calc_exponential_hash(self):
        l = []
        prevstep = 0
        for i in xrange(256+1):
            step = int((math.pow((float(i) / 256.0), self.expo) * self.hashsize) + 0.5)
            #print "step is %d delta=%d" % (step, step-prevstep)
            l.extend([i] * (step - prevstep))
            prevstep = step
        #print "length of l=%d" % (len(l))
        l = l[:self.hashsize]
        self.hash = numpy.array(l)
        hashlen = len(self.hash)
        assert hashlen == self.hashsize, \
               RGBMapError("Computed hash table size (%d) != specified size (%d)" % (hashlen, self.hashsize))

    def calc_hash(self):
        method = self.hashalgs[self.hashalg]
        method()

    def copy_attributes(self, dst_rgbmap):
        dst_rgbmap.set_cmap(self.cmap)
        dst_rgbmap.set_imap(self.imap)
        dst_rgbmap.set_hash_algorithm(self.hashalg)

    def reset_cmap(self):
        self.recalc()
        
#END
