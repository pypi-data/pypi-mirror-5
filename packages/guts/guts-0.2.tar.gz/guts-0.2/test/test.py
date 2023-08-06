
import unittest
import calendar
import math
import re
import sys

sys.path[0:0] = [ '../src' ]

from guts import *

class SamplePat(StringPattern):
    pattern = r'[a-z]{3}'

class SampleChoice(StringChoice):
    choices = [ 'a', 'bcd', 'efg' ]

basic_types = (Bool, Int, Float, String, Complex, Timestamp,
        SamplePat, SampleChoice)

def tstamp(*args):
    return float(calendar.timegm(args))

samples = {}
samples[Bool] = [ True, False ]
samples[Int] = [ 2**n for n in [1,30] ] #,31,65] ] 
samples[Float] = [ 0., 1., math.pi, float('inf'), float('-inf'), float('nan') ]
samples[String] = [ '', 'test', 'abc def', '<', '\n', '"', '\'', 
        ''.join(chr(x) for x in range(32,128)) ] # chr(0) and other special chars don't work with xml...
samples[Complex] = [ 1.0+5J, 0.0J, complex('inf'), complex(math.pi,1.0) ]
samples[Timestamp] = [ 0.0, 
        tstamp(2030,1,1,0,0,0), 
        tstamp(1960,1,1,0,0,0),
        tstamp(2010,10,10,10,10,10) + 0.000001]

samples[SamplePat] = [ 'aaa', 'zzz' ]
samples[SampleChoice] = [ 'a', 'bcd', 'efg' ]

regularize = {}
regularize[Bool] = [ (1, True), (0, False), ('0', False), ('False', False) ]
regularize[Int] = [ ('1', 1), (1.0, 1), (1.1, 1) ]
regularize[Float] = [ ('1.0', 1.0), (1, 1.0), ('inf', float('inf')) ]
regularize[String] = [ (1, '1') ]
regularize[Timestamp] = [ 
        ('2010-01-01 10:20:01', tstamp(2010,1,1,10,20,1)),
        ('2010-01-01T10:20:01', tstamp(2010,1,1,10,20,1)),
        ('2010-01-01T10:20:01.11Z', tstamp(2010,1,1,10,20,1)+0.11),
        ('2030-12-12 00:00:10.11111', tstamp(2030,12,12,0,0,10)+0.11111)
]

class TestGuts(unittest.TestCase):

    def assertEqualNanAware(self, a, b):
        if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
            return 
        
        self.assertEqual(a,b)

    def testChoice(self):
        class X(Object):
            m = StringChoice.T(['a', 'b'])

        x = X(m='a')
        x.validate()
        x = X(m='c')
        with self.assertRaises(ValidationError):
            x.validate()

    def testUnion(self):

        class X1(Object):
            m = Union.T(members=[Int.T(), StringChoice.T(['small', 'large'])])

        class U(Union):
            members = [ Int.T(), StringChoice.T(['small', 'large']) ]
    
        class X2(Object):
            m = U.T()

        X = X2
        x1 = X(m='1')
        with self.assertRaises(ValidationError):
            x1.validate()

        x1.validate(regularize=True)
        self.assertEqual(x1.m, 1)

        x2 = X(m='small')
        x2.validate()
        x3 = X(m='fail!')
        with self.assertRaises(ValidationError):
            x3.validate()
        with self.assertRaises(ValidationError):
            x3.validate(regularize=True)

    def testTooMany(self):

        class A(Object):
            m = List.T(Int.T())
            xmltagname = 'a'

        a = A(m=[1,2,3])

        class A(Object):
            m = Int.T()
            xmltagname = 'a'
        
        with self.assertRaises(ArgumentError):
            a2 = load_xml_string(a.dump_xml())

    def testDeferred(self):
        class A(Object):
            p = Defer('B.T', optional=True)

        class B(Object):
            p = A.T()

        a = A(p=B(p=A()))

    def testListDeferred(self):
        class A(Object):
            p = List.T(Defer('B.T'))
            q = List.T(Defer('B.T'))

        class B(Object):
            p = List.T(A.T())

        a = A(p=[B(p=[A()])], q=[B(),B()])

    def testSelfDeferred(self):
        class A(Object):
            a = Defer('A.T', optional=True)

        a = A(a=A(a=A()))

    def testContentStyleXML(self):

        class Duration(Object):
            unit = String.T(optional=True, xmlstyle='attribute')
            uncertainty = Float.T(optional=True)
            value = Float.T(optional=True, xmlstyle='content')

            xmltagname = 'duration'

        s = '<duration unit="s"><uncertainty>0.1</uncertainty>10.5</duration>'
        dur = load_xml_string(s)
        self.assertEqual(dur.value, float('10.5'))
        self.assertEqual(dur.unit, 's')
        self.assertEqual(dur.uncertainty, float('0.1'))
        self.assertEqual(re.sub(r'\n\s*', '', dur.dump_xml()), s)

    def testPO(self):
        class SKU(StringPattern):
            pattern = '\\d{3}-[A-Z]{2}'

        class Comment(String):
            xmltagname = 'comment'

        class Quantity(Int):
            pass

        class USAddress(Object):
            country = String.T(default='US', optional=True, xmlstyle='attribute')
            name = String.T()
            street = String.T()
            city = String.T()
            state = String.T()
            zip = Float.T()

        class Item(Object):
            part_num = SKU.T(xmlstyle='attribute')
            product_name = String.T()
            quantity = Quantity.T()
            us_price = Float.T(xmltagname='USPrice')
            comment = Comment.T(optional=True)
            ship_date = DateTimestamp.T(optional=True)

        class Items(Object):
            item_list = List.T(Item.T())

        class PurchaseOrderType(Object):
            order_date = DateTimestamp.T(optional=True, xmlstyle='attribute')
            ship_to = USAddress.T()
            bill_to = USAddress.T()
            comment = Comment.T(optional=True)
            items = Items.T()

        class PurchaseOrder(PurchaseOrderType):
            xmltagname = 'purchaseOrder'

        xml = '''<?xml version="1.0"?>
<purchaseOrder orderDate="1999-10-20">
   <shipTo country="US">
      <name>Alice Smith</name>
      <street>123 Maple Street</street>
      <city>Mill Valley</city>
      <state>CA</state>
      <zip>90952</zip>
   </shipTo>
   <billTo country="US">
      <name>Robert Smith</name>
      <street>8 Oak Avenue</street>
      <city>Old Town</city>
      <state>PA</state>
      <zip>95819</zip>
   </billTo>
   <comment>Hurry, my lawn is going wild</comment>
   <items>
      <item partNum="872-AA">
         <productName>Lawnmower</productName>
         <quantity>1</quantity>
         <USPrice>148.95</USPrice>
         <comment>Confirm this is electric</comment>
      </item>
      <item partNum="926-AA">
         <productName>Baby Monitor</productName>
         <quantity>1</quantity>
         <USPrice>39.98</USPrice>
         <shipDate>1999-05-21</shipDate>
      </item>
   </items>
</purchaseOrder>
'''
        po1 = load_xml_string(xml) 
        po2 = load_xml_string(po1.dump_xml())
        
        self.assertEqual(po1.dump(), po2.dump())

    def testDumpLoad(self):

        from tempfile import NamedTemporaryFile as NTF
        from cStringIO import StringIO

        class A(Object):
            xmltagname = 'a'
            p = Int.T()

        a1 = A(p=33)
        an = [ a1, a1, a1 ]

        def check1(a,b):
            self.assertEqual(a.p, b.p)

        def checkn(a,b):
            for ea, eb in zip(a,b):
                self.assertEqual(ea.p, eb.p)

        for (a, xdump, xload, check) in [
                    (a1, dump, load, check1), 
                    (a1, dump_xml, load_xml, check1),
                    (an, dump_all, load_all, checkn), 
                    (an, dump_all, iload_all, checkn), 
                    (an, dump_all_xml, load_all_xml, checkn),
                    (an, dump_all_xml, iload_all_xml, checkn)
                ]:

            for header in (False, True, 'custom header'):
                # via string
                s = xdump(a, header=header)
                b = xload(string=s)
                check(a,b)

                # via file
                f = NTF()
                xdump(a, filename=f.name, header=header)
                b = xload(filename=f.name)
                check(a,b)
                f.close()

                # via stream
                f = NTF()
                xdump(a, stream=f, header=header)
                f.seek(0)
                b = xload(stream=f)
                check(a,b)
                f.close()

        b1 = A.load(string=a1.dump())
        check1(a1,b1)

        f = NTF()
        a1.dump(filename=f.name)
        b1 = A.load(filename=f.name)
        check1(a1,b1)
        f.close()

        f = NTF()
        a1.dump(stream=f)
        f.seek(0)
        b1 = A.load(stream=f)
        check1(a1,b1)
        f.close()
    
        b1 = A.load_xml(string=a1.dump_xml())
        check1(a1,b1)

        f = NTF()
        a1.dump_xml(filename=f.name)
        b1 = A.load_xml(filename=f.name)
        check1(a1,b1)
        f.close()

        f = NTF()
        a1.dump_xml(stream=f)
        f.seek(0)
        b1 = A.load_xml(stream=f)
        check1(a1,b1)
        f.close()

def makeBasicTypeTest(Type, sample, sample_in=None, xml=False):

    if sample_in is None:
        sample_in = sample

    def basicTypeTest(self):

        class X(Object):
            a = Type.T()
            b = Type.T(optional=True)
            c = Type.T(default=sample)
            d = List.T(Type.T())
            e = Tuple.T(1, Type.T())
            xmltagname = 'x'

        x = X(a=sample_in, e=(sample_in,))
        x.d.append(sample_in)
        if sample_in is not sample:
            with self.assertRaises(ValidationError):
                x.validate()

        x.validate(regularize=sample_in is not sample)
        self.assertEqualNanAware(sample, x.a)
        
        if not xml:
            x2 = load_string(x.dump())

        else:
            x2 = load_xml_string(x.dump_xml())

        self.assertEqualNanAware(x.a, x2.a)
        self.assertIsNone(x.b)
        self.assertIsNone(x2.b)
        self.assertEqualNanAware(sample, x.c)
        self.assertEqualNanAware(sample, x2.c)
        self.assertTrue(isinstance(x.d, list))
        self.assertTrue(isinstance(x2.d, list))
        self.assertEqualNanAware(x.d[0], sample)
        self.assertEqualNanAware(x2.d[0], sample)
        self.assertEqual(len(x.d), 1)
        self.assertEqual(len(x2.d), 1)
        self.assertTrue(isinstance(x.e, tuple))
        self.assertTrue(isinstance(x2.e, tuple))
        self.assertEqualNanAware(x.e[0], sample)
        self.assertEqualNanAware(x2.e[0], sample)
        self.assertEqual(len(x.e), 1)
        self.assertEqual(len(x2.e), 1)

    return basicTypeTest

for Type in samples:
    for isample, sample in enumerate(samples[Type]):
        for xml in (False, True):
            setattr(TestGuts, 'testBasicType' + Type.__name__ + 
                    str(isample) + ['','XML'][xml], 
                    makeBasicTypeTest(Type, sample, xml=xml))

for Type in regularize:
    for isample, (sample_in, sample) in enumerate(regularize[Type]):
        for xml in (False, True):
            setattr(TestGuts, 'testBasicTypeRegularize' + Type.__name__ +
                    str(isample) + ['','XML'][xml], 
                    makeBasicTypeTest(Type, sample, sample_in=sample_in, xml=xml))
                
if __name__ == '__main__':
    unittest.main()

