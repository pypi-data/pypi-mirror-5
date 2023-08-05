# -*- coding: utf-8 -*-

# Copyright (c) 2011 Mitch Garnaat http://garnaat.org/
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Some unit tests for the S3 MultiPartUpload
"""

# Note:
# Multipart uploads require at least one part. If you upload
# multiple parts then all parts except the last part has to be
# bigger than 5M. Hence we just use 1 part so we can keep
# things small and still test logic.

import unittest
import time
import StringIO
from boto.s3.connection import S3Connection


class S3MultiPartUploadTest(unittest.TestCase):
    s3 = True

    def setUp(self):
        self.conn = S3Connection(is_secure=False)
        self.bucket_name = 'multipart-%d' % int(time.time())
        self.bucket = self.conn.create_bucket(self.bucket_name)

    def tearDown(self):
        for key in self.bucket:
            key.delete()
        self.bucket.delete()

    def test_abort(self):
        key_name = u"テスト"
        mpu = self.bucket.initiate_multipart_upload(key_name)
        mpu.cancel_upload()

    def test_complete_ascii(self):
        key_name = "test"
        mpu = self.bucket.initiate_multipart_upload(key_name)
        fp = StringIO.StringIO("small file")
        mpu.upload_part_from_file(fp, part_num=1)
        fp.close()
        cmpu = mpu.complete_upload()
        self.assertEqual(cmpu.key_name, key_name)
        self.assertNotEqual(cmpu.etag, None)

    def test_complete_japanese(self):
        key_name = u"テスト"
        mpu = self.bucket.initiate_multipart_upload(key_name)
        fp = StringIO.StringIO("small file")
        mpu.upload_part_from_file(fp, part_num=1)
        fp.close()
        cmpu = mpu.complete_upload()
        # LOL... just found an Amazon bug when it returns the
        # key in the completemultipartupload result. AWS returns
        # ??? instead of the correctly encoded key name. We should
        # fix this to the comment line below when amazon fixes this
        # and this test starts failing due to below assertion.
        self.assertEqual(cmpu.key_name, "???")
        #self.assertEqual(cmpu.key_name, key_name)
        self.assertNotEqual(cmpu.etag, None)

    def test_list_japanese(self):
        key_name = u"テスト"
        mpu = self.bucket.initiate_multipart_upload(key_name)
        rs = self.bucket.list_multipart_uploads()
        # New bucket, so only one upload expected
        lmpu = iter(rs).next()
        self.assertEqual(lmpu.id, mpu.id)
        self.assertEqual(lmpu.key_name, key_name)
        # Abort using the one returned in the list
        lmpu.cancel_upload()

    def test_list_multipart_uploads(self):
        key_name = u"テスト"
        mpus = []
        mpus.append(self.bucket.initiate_multipart_upload(key_name))
        mpus.append(self.bucket.initiate_multipart_upload(key_name))
        rs = self.bucket.list_multipart_uploads()
        # uploads (for a key) are returned in time initiated asc order
        for lmpu in rs:
            ompu = mpus.pop(0)
            self.assertEqual(lmpu.key_name, ompu.key_name)
            self.assertEqual(lmpu.id, ompu.id)
        self.assertEqual(0, len(mpus))

    def test_four_part_file(self):
        key_name = "k"
        contents = "01234567890123456789"
        sfp = StringIO.StringIO(contents)

        # upload 20 bytes in 4 parts of 5 bytes each
        mpu = self.bucket.initiate_multipart_upload(key_name)
        mpu.upload_part_from_file(sfp, part_num=1, size=5)
        mpu.upload_part_from_file(sfp, part_num=2, size=5)
        mpu.upload_part_from_file(sfp, part_num=3, size=5)
        mpu.upload_part_from_file(sfp, part_num=4, size=5)
        sfp.close()

        etags = {}
        pn = 0
        for part in mpu:
            pn += 1
            self.assertEqual(5, part.size)
            etags[pn] = part.etag
        self.assertEqual(pn, 4)
        # etags for 01234
        self.assertEqual(etags[1], etags[3])
        # etags for 56789
        self.assertEqual(etags[2], etags[4])
        # etag 01234 != etag 56789
        self.assertNotEqual(etags[1], etags[2])

        # parts are too small to compete as each part must
        # be a min of 5MB so so we'll assume that is enough
        # testing and abort the upload.
        mpu.cancel_upload()
