
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '\xfa)\x18K\xe9\x9b\xf9\xd8\xacGv~\xdf\x0bp9'
    
_lr_action_items = {'NUMBER':([3,5,6,7,],[5,6,7,8,]),'DIFFUSE':([0,1,2,4,8,],[3,-2,3,-1,-3,]),'$end':([1,2,4,8,],[-2,0,-1,-3,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'line':([0,2,],[1,4,]),'lines':([0,],[2,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> lines","S'",1,None,None,None),
  ('lines -> lines line','lines',2,'p_lines','/home/isaac/CS171/hw1/hw0parser.py',49),
  ('lines -> line','lines',1,'p_lines','/home/isaac/CS171/hw1/hw0parser.py',50),
  ('line -> DIFFUSE NUMBER NUMBER NUMBER NUMBER','line',5,'p_line_diffuse','/home/isaac/CS171/hw1/hw0parser.py',59),
]
