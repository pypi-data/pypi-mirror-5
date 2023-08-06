# -*- coding: utf-8 -*-

#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

import numbers
from struct import pack, unpack

from blist import blist, btuple

from python_patterns.utils.decorators import Property

from .crypto import merkle
from .mixins import HashableMixin, SerializableMixin
from .numeric import mpq
from .serialize import (
    serialize_varchar, deserialize_varchar,
    serialize_hash, deserialize_hash,
    serialize_list, deserialize_list)
from .utils import StringIO, target_from_compact

__all__ = [
    'ChainParameters',
    'Output',
    'OutPoint',
    'Input',
    'Transaction',
    'MerkleNode',
    'Block',
]

# ===----------------------------------------------------------------------===

from collections import namedtuple

ChainParameters = namedtuple('ChainParameters', ['magic', 'port', 'genesis',
    'testnet', 'max_value', 'transient_reward', 'transient_budget',
    'perpetual_reward', 'perpetual_budget', 'fee_budget', 'maximum_target',
    'next_target', 'alert_keys','checkpoints', 'features'])

# ===----------------------------------------------------------------------===

from .script import Script

# ===----------------------------------------------------------------------===

class Output(SerializableMixin):
    def __init__(self, amount=0, contract=None, *args, **kwargs):
        if contract is None:
            contract = self.get_script_class()()
        super(Output, self).__init__(*args, **kwargs)
        self.amount = amount
        self.contract = contract

    @classmethod
    def get_script_class(cls):
        return getattr(cls, 'script_class', Script)

    def serialize(self):
        result  = pack('<Q', self.amount)
        result += self.contract.serialize()
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['amount'] = unpack('<Q', file_.read(8))[0]
        initargs['contract'] = cls.get_script_class().deserialize(file_)
        return cls(**initargs)

    def __eq__(self, other):
        return (self.amount   == other.amount and
                self.contract == other.contract)
    def __repr__(self):
        return '%s(amount=%d.%08d, contract=%s)' % (
            self.__class__.__name__,
            self.amount // 100000000,
            self.amount  % 100000000,
            repr(self.contract))

# ===----------------------------------------------------------------------===

class OutPoint(SerializableMixin):
    def __init__(self, hash=0, n=0xffffffff, *args, **kwargs):
        super(OutPoint, self).__init__(*args, **kwargs)
        self.hash = hash
        self.n = n

    def serialize(self):
        result  = serialize_hash(self.hash, 32)
        result += pack('<I', self.n)
        return result
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['hash'] = deserialize_hash(file_, 32)
        initargs['n'] = unpack('<I', file_.read(4))[0]
        return cls(**initargs)

    def __nonzero__(self):
        return not (self.hash==0 and self.n==0xffffffff)

    def __eq__(self, other):
        return self.hash==other.hash and self.n==other.n
    def __repr__(self):
        return '%s(hash=%064x, n=%d)' % (
            self.__class__.__name__,
            self.hash,
            self.n==0xffffffff and -1 or self.n)

# ===----------------------------------------------------------------------===

class Input(SerializableMixin):
    def __init__(self, outpoint=None, endorsement=None, sequence=0xffffffff,
                 *args, **kwargs):
        if outpoint is None:
            outpoint = self.deserialize_outpoint(StringIO('\x00'*32 + '\xff'*4))
        if endorsement is None:
            endorsement = kwargs.pop('coinbase', self.get_script_class()())
        super(Input, self).__init__(*args, **kwargs)
        self.outpoint = outpoint
        self.endorsement = endorsement
        self.sequence = sequence

    @classmethod
    def get_outpoint_class(cls):
        return getattr(cls, 'outpoint_class', OutPoint)

    @classmethod
    def get_script_class(cls):
        return getattr(cls, 'script_class', Script)

    def serialize(self):
        result = self.outpoint.serialize()
        if hasattr(self.endorsement, 'serialize'):
            result += self.endorsement.serialize()
        else:
            result += serialize_varchar(self.endorsement) # <-- coinbase
        result += pack('<I', self.sequence)
        return result
    @staticmethod
    def deserialize_outpoint(file_):
        return self.get_outpoint_class().deserialize(file_)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['outpoint'] = cls.deserialize_outpoint(file_)
        str_ = deserialize_varchar(file_) # <-- might be coinbase!
        initargs['sequence'] = unpack('<I', file_.read(4))[0]
        if not initargs['outpoint'] and initargs['sequence']==0xffffffff:
            initargs['coinbase'] = str_
        else:
            initargs['endorsement'] = cls.get_script_class().deserialize(
                StringIO(serialize_varchar(str_)))
        return cls(**initargs)

    @Property
    def is_coinbase():
        def fget(self):
            return not outpoint and sequence==0xffffffff
        return locals()

    def __eq__(self, other):
        return (self.outpoint    == other.outpoint    and
                self.endorsement == other.endorsement and
                self.sequence    == other.sequence)
    def __repr__(self):
        sequence_str = (self.sequence!=0xffffffff
            and ', sequence=%d' % self.sequence
             or '')
        return '%s(outpoint=%s, %s=%s%s)' % (
            self.__class__.__name__,
            repr(self.outpoint),
            self.outpoint and 'endorsement' or 'coinbase',
            repr(self.endorsement),
            sequence_str)

# ===----------------------------------------------------------------------===

class Transaction(SerializableMixin, HashableMixin):
    def __init__(self, version=1, inputs=None, outputs=None, lock_time=0,
                 reference_height=0, *args, **kwargs):
        if inputs is None: inputs = ()
        if outputs is None: outputs = ()
        super(Transaction, self).__init__(*args, **kwargs)
        self.version = version
        getattr(self, 'inputs_create', lambda x:setattr(x, 'inputs', blist()))(self)
        self.inputs.extend(inputs)
        getattr(self, 'outputs_create', lambda x:setattr(x, 'outputs', blist()))(self)
        self.outputs.extend(outputs)
        self.lock_time = lock_time
        self.reference_height = reference_height

    @classmethod
    def get_input_class(cls):
        return getattr(cls, 'input_class', Input)

    @classmethod
    def get_output_class(cls):
        return getattr(cls, 'output_class', Output)

    def serialize(self):
        if self.version not in (1,2):
            raise NotImplementedError()
        result  = pack('<I', self.version)
        result += serialize_list(self.inputs, lambda i:i.serialize())
        result += serialize_list(self.outputs, lambda o:o.serialize())
        result += pack('<I', self.lock_time)
        if self.version==2:
            result += pack('<I', self.reference_height)
        return result
    @classmethod
    def deserialize_input(cls, file_, *args, **kwargs):
        return cls.get_input_class().deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize_output(cls, file_, *args, **kwargs):
        return cls.get_output_class().deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['version'] = unpack('<I', file_.read(4))[0]
        if initargs['version'] not in (1,2):
            raise NotImplementedError()
        initargs['inputs'] = blist(deserialize_list(file_, lambda f:cls.deserialize_input(f)))
        initargs['outputs'] = blist(deserialize_list(file_, lambda f:cls.deserialize_output(f)))
        initargs['lock_time'] = unpack('<I', file_.read(4))[0]
        if initargs['version'] in (2,):
            initargs['reference_height'] = unpack('<I', file_.read(4))[0]
        return cls(**initargs)

    @Property
    def is_coinbase():
        def fget(self):
            return 1==len(self.inputs) and not self.inputs[0].outpoint
        return locals()

    def __eq__(self, other):
        return (self.version          == other.version          and
                self.lock_time        == other.lock_time        and
                self.reference_height == other.reference_height and
                btuple(self.inputs)   == btuple(other.inputs)   and
                btuple(self.outputs)  == btuple(other.outputs))
    def __repr__(self):
        reference_height_str = (self.version in (2,)
            and ', reference_height=%d' % self.reference_height
             or '')
        return ('%s(version=%d, '
                   'inputs=%s, '
                   'outputs=%s, '
                   'lock_time=%d%s)' % (
            self.__class__.__name__,
            self.version,
            repr(self.inputs),
            repr(self.outputs),
            self.lock_time,
            reference_height_str))

# ===----------------------------------------------------------------------===

class MerkleNode(SerializableMixin, HashableMixin):
    def __init__(self, children=None, *args, **kwargs):
        if children is None: children = ()
        super(MerkleNode, self).__init__(*args, **kwargs)
        getattr(self, 'children_create', lambda x:setattr(x, 'children', blist()))(self)
        for child in children:
            if hasattr(child, 'hash') and not isinstance(child, MerkleNode):
                child = child.hash
            self.children.append(child)

    # TODO: handle explicit merkle trees
    def serialize(self):
        if not all(map(lambda h:isinstance(h, numbers.Integral), self.children)):
            raise NotImplementedError()
        return serialize_list(self.children, lambda x:serialize_hash(x, 32))
    @classmethod
    def deserialize(cls, file_):
        return cls(deserialize_list(file_, lambda x:deserialize_hash(x, 32)))

    def hash__getter(self):
        return merkle(self.children)

    def __eq__(self, other):
        return self.hash == other.hash
    def __repr__(self):
        return ''.join([
            self.__class__.__name__,
            '([',
            ', '.join(map(repr, self.children)),
            '])'])

# ===----------------------------------------------------------------------===

class Block(SerializableMixin, HashableMixin):
    def __init__(self, version=1, prev_block=0, merkle_root=None, time=0,
                 bits=0x1d00ffff, nonce=0, vtx=None, *args, **kwargs):
        if None not in (merkle_root, vtx):
            if getattr(merkle_root, 'hash', merkle_root) != merkle(vtx):
                raise ValueError(
                    u"merkle_root does not match merkle(vtx); are you "
                    u"sure you know what you're doing?")
        else:
            if vtx         is None: vtx         = ()
            if merkle_root is None: merkle_root = MerkleNode(children=vtx)
        super(Block, self).__init__(*args, **kwargs)
        self.version = version
        self.prev_block_hash = getattr(prev_block, 'hash', prev_block)
        self.merkle_root_hash = getattr(merkle_root, 'hash', merkle_root)
        self.time = time
        self.bits = bits
        self.nonce = nonce

    def serialize(self):
        if self.version not in (1,2):
            raise NotImplementedError()
        result  = pack('<I', self.version)
        result += serialize_hash(self.prev_block_hash, 32)
        result += serialize_hash(self.merkle_root_hash, 32)
        result += pack('<I', self.time)
        result += pack('<I', self.bits)
        result += pack('<I', self.nonce)
        return result
    def __bytes__(self):
        return self.serialize()
    @staticmethod
    def deserialize_transaction(file_, *args, **kwargs):
        return Transaction.deserialize(file_, *args, **kwargs)
    @classmethod
    def deserialize(cls, file_):
        initargs = {}
        initargs['version'] = unpack('<I', file_.read(4))[0]
        if initargs['version'] not in (1,2):
            raise NotImplementedError()
        initargs['prev_block'] = deserialize_hash(file_, 32)
        initargs['merkle_root'] = deserialize_hash(file_, 32)
        initargs['time'] = unpack('<I', file_.read(4))[0]
        initargs['bits'] = unpack('<I', file_.read(4))[0]
        initargs['nonce'] = unpack('<I', file_.read(4))[0]
        return cls(**initargs)

    def __eq__(self, other):
        return (self.version          == other.version          and
                self.prev_block_hash  == other.prev_block_hash  and
                self.merkle_root_hash == other.merkle_root_hash and
                self.time             == other.time             and
                self.bits             == other.bits             and
                self.nonce            == other.nonce)
    def __repr__(self):
        return ('%s(version=%d, '
                   'prev_block=0x%064x, '
                   'merkle_root=0x%064x, '
                   'time=%s, '
                   'bits=0x%08x, '
                   'nonce=0x%08x)' % (
            self.__class__.__name__,
            self.version,
            self.prev_block_hash,
            self.merkle_root_hash,
            self.time,
            self.bits,
            self.nonce))

    @Property
    def difficulty():
        def fget(self):
            return mpq(2**256-1, target_from_compact(self.bits))
        return locals()

#
# End of File
#
