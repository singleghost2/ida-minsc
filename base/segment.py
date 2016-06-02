'''
segment-context

generic tools for working with segments
'''
import logging,os
import six,types

import internal,ui,database
from internal import utils

import idaapi

## enumerating
def iterate():
    '''Iterate through each segment defined in the database.'''
    for n in xrange(idaapi.get_segm_qty()):
        yield idaapi.getnseg(n)
    return
def list():
    '''List all the segments defined in the database by name.'''
    for n in iterate():
        yield idaapi.get_true_segm_name(n) or ""
    return

## searching
def by_name(name):
    '''Return the segment with the given ``name``.'''
    s = idaapi.get_segm_by_name(name)
    if s is None:
        raise Exception("{:s}.by_name({!r}) : Unable to locate segment".format(__name__, name))
    return s
byName = by_name
def by_selector(selector):
    '''Return the segment associated with ``selector``.'''
    s = idaapi.get_segm_by_sel(selector)
    if s is None:
        raise Exception("{:s}.by_selector(0x{:x}) : Unable to locate segment".format(__name__, selector))
    return s
bySelector = by_selector
def by_address(ea):
    '''Return the segment that contains the specified ``ea``.'''
    s = idaapi.getseg(ea)
    if s is None:
        raise Exception("{:s}.by_address(0x{:x}) : Unable to locate segment".format(__name__, ea))
    return s
byAddress = by_address
@utils.multicase(seg=idaapi.segment_t)
def by(segment):
    '''Return a segment by it's segment_t.'''
    return segment
@utils.multicase(name=basestring)
def by(name):
    '''Return the segment by it's ``name``.'''
    return by_name(name)
@utils.multicase(ea=six.integer_types)
def by(ea):
    '''Return the segment containing the address ``ea``.'''
    return by_address(ea)

## properties
@utils.multicase()
def range():
    '''Return the range of the current segment.'''
    seg = ui.current.segment()
    if seg is None: raise LookupError("{:s}.range() : Not currently positioned within a segment".format(__name__))
    return seg.startEA, seg.endEA
@utils.multicase()
def range(segment):
    '''Return the range of the segment specified by ``seg``.'''
    seg = by(segment)
    return seg.startEA, seg.endEA

@utils.multicase()
def size():
    '''Return the size of the current segment.'''
    seg = ui.current.segment()
    if seg is None: raise LookupError("{:s}.size() : Not currently positioned within a segment".format(__name__))
    return seg.endEA - seg.startEA
@utils.multicase()
def size(segment):
    '''Return the size of the segment specified by ``segment``.'''
    seg = by(segment)
    return seg.endEA - seg.startEA

@utils.multicase()
def string():
    '''Return the contents of the current segment as a string.'''
    segment = ui.current.segment()
    if segment is None: raise LookupError("{:s}.string() : Not currently positioned within a segment".format(__name__))
    return idaapi.get_many_bytes(segment.startEA, segment.endEA-segment.startEA)
@utils.multicase()
def string(segment):
    '''Return the contents of the segment identified by ``segment`` as a string.'''
    seg = by(segment)
    return idaapi.get_many_bytes(seg.startEA, seg.endEA-seg.startEA)

@utils.multicase()
def repr():
    '''Return a repr() of the current segment.'''
    segment = ui.current.segment()
    if segment is None: raise LookupError("{:s}.repr() : Not currently positioned within a segment".format(__name__))
    return '{:s} {:s} {:x}-{:x} (+{:x})'.format(object.__repr__(segment),idaapi.get_true_segm_name(segment),segment.startEA,segment.endEA,segment.endEA-segment.startEA)
@utils.multicase()
def repr(segment):
    '''Return a repr() of the segment identified by ``segment``.'''
    '''Given a segment_t/address, return a printable representation of it'''
    seg = by(segment)
    return '{:s} {:s} {:x}-{:x} (+{:x})'.format(object.__repr__(seg),idaapi.get_true_segm_name(seg),seg.startEA,seg.endEA,seg.endEA-seg.startEA)

@utils.multicase()
def top():
    '''Return the top address of the current segment.'''
    segment = ui.current.segment()
    if segment is None: raise LookupError("{:s}.top() : Not currently positioned within a segment".format(__name__))
    return segment.startEA
@utils.multicase()
def top(segment):
    '''Return the top address of the segment identified by ``segment``.'''
    seg = by(segment)
    return seg.startEA

@utils.multicase()
def bottom():
    '''Return the bottom address of the current segment.'''
    seg = ui.current.segment()
    if seg is None: raise LookupError("{:s}.bottom() : Not currently positioned within a segment".format(__name__))
    return seg.endEA
@utils.multicase()
def bottom(segment):
    '''Return the bottom address of the segment identified by ``segment``.'''
    seg = by(segment)
    return seg.endEA

@utils.multicase()
def name():
    '''Return the name of the current segment.'''
    seg = ui.current.segment()
    if seg is None: raise LookupError("{:s}.name() : Not currently positioned within a segment".format(__name__))
    return idaapi.get_true_segm_name(seg)
@utils.multicase()
def name(segment):
    '''Return the name of the segment identified by ``segment``.'''
    seg = by(segment)
    return idaapi.get_true_segm_name(seg)

@utils.multicase(none=types.NoneType)
def set_color(segment, none):
    '''Clear the color of the segment identified by ``segment``.'''
    seg = by(segment)
    seg.color = 0xffffffff
    return bool(seg.update())
@utils.multicase(rgb=int)
def set_color(segment, rgb):
    '''Set the color of the segment identified by ``segment`` to ``rgb``.'''
    r,b = (rgb&0xff0000) >> 16, rgb&0x0000ff
    seg = by(segment)
    seg.color = (b<<16)|(rgb&0x00ff00)|r
    return bool(seg.update())
@utils.multicase(rgb=int)
def set_color(rgb):
    '''Set the color of the current segment to ``rgb``.'''
    return set_color(ui.current.segment(), rgb)
@utils.multicase(none=types.NoneType)
def set_color(none):
    '''Clear the color of the current segment.'''
    return set_color(ui.current.segment(), None)

@utils.multicase()
def get_color():
    '''Return the color of the current segment.'''
    seg = ui.current.segment()
    if seg is None: raise LookupError("{:s}.get_color() : Not currently positioned within a segment".format(__name__))
    b,r = (seg.color&0xff0000)>>16, seg.color&0x0000ff
    return None if seg.color == 0xffffffff else (r<<16)|(seg.color&0x00ff00)|b
@utils.multicase()
def get_color(segment):
    '''Return the color of the segment identified by ``segment``.'''
    seg = by(segment)
    b,r = (seg.color&0xff0000)>>16, seg.color&0x0000ff
    return None if seg.color == 0xffffffff else (r<<16)|(seg.color&0x00ff00)|b

@utils.multicase()
def color():
    '''Return the color of the current segment.'''
    return get_color(ui.current.segment())
@utils.multicase()
def color(segment):
    '''Return the color of the segment identified by ``segment``.'''
    return get_color(segment)
@utils.multicase(none=types.NoneType)
def color(none):
    '''Clear the color of the current segment.'''
    return set_color(ui.current.segment(), None)
@utils.multicase(none=types.NoneType)
def color(segment, none):
    '''Clear the color of the segment identified by ``segment``.'''
    return set_color(segment, None)
@utils.multicase(rgb=int)
def color(segment, rgb):
    '''Sets the color of the segment identified by ``segment`` to ``rgb``.'''
    return set_color(segment, rgb)

## functions
# shamefully ripped from idc.py
def _load_file(filename, ea, size, offset=0):
    path = os.path.abspath(filename)
    li = idaapi.open_linput(path, False)
    if not li:
        raise Exception('{:s}.load_file : Unable to create loader_input_t : {:s}'.format(__name__, path))
    res = idaapi.file2base(li, offset, ea, ea+size, True)
    idaapi.close_linput(li)
    return res

def _save_file(filename, ea, size, offset=0):
    path = os.path.abspath(filename)
    of = idaapi.fopenWB(path)
    if not of:
        raise Exception('{:s}.save_file : Unable to open target file : {:s}'.format(__name__, path))
    res = idaapi.base2file(of, offset, ea, ea+size)
    idaapi.eclose(of)
    return res

def load(filename, ea, size=None, offset=0, **kwds):
    """Load the specified ``filename`` to the address ``ea`` as a segment.
    If ``size`` is not specified, use the length of the file.
    ``offset`` represents the offset into the file to use.
    ``name`` can be used to name the segment.
    """
    filesize = os.stat(filename).st_size

    if size is None:
        size = filesize - offset
    res = _load_file(filename, size, ea, offset)
    if not res:
        raise Exception("{:s}.load : Unable to load file into 0x{:x}:+0x{:x} : {:s}".format(__name__, ea, size, os.path.relpath(filename)))
    return create(ea, size, kwds.get('name', os.path.split(filename)[1]))

def map(ea, size, newea, **kwds):
    """Map ``size`` bytes of data from ``ea`` into a new segment at ``newea``.
    ``name`` can be used to name the segment.
    """
    fpos,data = idaapi.get_fileregion_offset(ea),database.read(ea, size)
    if len(data) != size:
        raise Exception("{:s}.map : Unable to read 0x{:x} bytes from 0x{:x}".format(__name__, size, ea))
    res = idaapi.mem2base(data, newea, fpos)
    if not res:
        raise Exception("{:s}.map : Unable to remap 0x{:x}:+0x{:x} to 0x{:x}".format(__Name__, ea, size, newea))
    return create(newea, size, kwds.get('name', 'map_{:x}'.format(ea)))
    #return create(newea, size, kwds.get('name', 'map_{:s}'.format(newea>>4)))

# creation/destruction
def create(offset, size, name, **kwds):
    """Create a segment at ``offset`` with ``size`` and name it according to ``name``.
    ``bits`` can be used to specify the bit size of the segment
    ``comb`` can be used to specify any flags (idaapi.sc*)
    ``align`` can be used to specify paragraph alignment (idaapi.sa*)
    ``org`` specifies the origin of the segment (must be paragraph aligned due to ida)
    """
    s = idaapi.get_segm_by_name(name)
    if s is not None:
        logging.fatal("{:s}.create({:x}, {:x}, {!r}, {!r}) : a segment with the specified name already exists : {:s}".format(__name__, offset, size, name, kwds, name))
        return None

    bits = kwds.get( 'bits', 32 if idaapi.getseg(offset) is None else idaapi.getseg(offset).abits()) # FIXME: use disassembler default bit length instead of 32

    if bits == 16:
        ## create a selector with the requested origin
        org = kwds.get('org',0)
        if org&0xf > 0:
            logging.fatal("{:s}.create({:x}, {:x}, {!r}, {!r}) : origin (.org) is not aligned to the size of a paragraph (0x10) : {:x}".format(__name__, offset, size, name, kwds, org))
            return None

        para = offset/16
        sel = idaapi.allocate_selector(para)
        idaapi.set_selector(sel, (para-kwds.get('org',0)/16)&0xffffffff)
    else:
        ## auto-create a selector for everything else
        sel = idaapi.setup_selector(kwds['selector']) if 'selector' in kwds else idaapi.find_free_selector()

    # create segment. ripped from idc
    s = idaapi.segment_t()
    s.startEA = offset
    s.endEA = offset+size
    s.sel = sel
    s.bitness = {16:0,32:1,64:2}[bits]
    s.comb = kwds.get('comb', idaapi.scPub)       # public
    s.align = kwds.get('align', idaapi.saRelByte)  # paragraphs

    res = idaapi.add_segm_ex(s, name, "", idaapi.ADDSEG_NOSREG|idaapi.ADDSEG_SPARSE)
    if res == 0:
        logging.warn("{:s}.create({:x}, {:x}, {!r}, {!r}) : unable to add a new segment".format(__name__, offset, size, name, kwds))
        res = idaapi.del_selector(sel)
        #assert res != 0
        return None
    return s

def delete(segment, remove=False):
    """Remove the segment identified by ``segment``.
    If the bool ``remove`` is specified, then remove the content of the segment from the database.
    """
    if not isinstance(segment, idaapi.segment_t):
        raise AssertionError('{:s}.delete : segment is not of an idaapi.segment_t : {!r}'.format(__name__, type(segment)))
    res = idaapi.del_selector(segment.sel)
    if res == 0:
        logging.warn("{:s}.delete({!r}):Unable to delete selector {:x}".format(__name__, segment, segment.sel))
    res = idaapi.del_segm(segment.startEA, idaapi.SEGMOD_KILL if remove else idaapi.SEGMOD_KEEP)
    if res == 0:
        logging.warn("{:s}.delete({!r}):Unable to delete segment {:s} : {:s}".format(__name__, segment, segment.name, segment.sel))
    return res

def save(filename, segment, offset=0):
    """Export the segment identified by ``segment`` to the file named ``filename``.

    If the int ``offset`` is specified, then begin writing into the file at the specified offset.
    """
    if isinstance(segment, idaapi.segment_t):
        return _save_file(filename, segment.startEA, size(segment), offset)
    return save(filename, by(segment))

#res = idaapi.add_segment_translation(ea, selector)
#res = idaapi.del_segment_translation(ea)

