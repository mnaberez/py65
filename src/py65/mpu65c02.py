#from py65.utils.conversions import convert_to_bin, convert_to_bcd
from mpu6502 import MPU as MPU6502

class MPU(MPU6502):
  def __init__(self, memory=None, pc=0x0000):
    MPU6502.__init__(self, memory=memory, pc=pc)

  # code pages

  """
  instruct = [
    i00, i01, ini, ini, ini, i05, i06, ini,
    i08, i09, i0a, ini, ini, i0d, i0e, ini,
    i10, i11, ini, ini, ini, i15, i16, ini,
    i18, i19, ini, ini, ini, i1d, i1e, ini,
    i20, i21, ini, ini, i24, i25, i26, ini,
    i28, i29, i2a, ini, i2c, i2d, i2e, ini,
    i30, i31, ini, ini, ini, i35, i36, ini,
    i38, i39, ini, ini, ini, i3d, i3e, ini,
    i40, i41, ini, ini, ini, i45, i46, ini,
    i48, i49, i4a, ini, i4c, i4d, i4e, ini,
    i50, i51, ini, ini, ini, i55, i56, ini,
    i58, i59, ini, ini, ini, i5d, i5e, ini,
    i60, i61, ini, ini, ini, i65, i66, ini,
    i68, i69, i6a, ini, i6c, i6d, i6e, ini,
    i70, i71, ini, ini, ini, i75, i76, ini,
    i78, i79, ini, ini, ini, i7d, i7e, ini,
    ini, i81, ini, ini, i84, i85, i86, ini,
    i88, ini, i8a, ini, i8c, i8d, i8e, ini,
    i90, i91, ini, ini, i94, i95, i96, ini,
    i98, i99, i9a, ini, ini, i9d, ini, ini,
    ia0, ia1, ia2, ini, ia4, ia5, ia6, ini,
    ia8, ia9, iaa, ini, iac, iad, iae, ini,
    ib0, ib1, ini, ini, ib4, ib5, ib6, ini,
    ib8, ib9, iba, ini, ibc, ibd, ibe, ini,
    ic0, ic1, ini, ini, ic4, ic5, ic6, ini,
    ic8, ic9, ica, ini, icc, icd, ice, ini,
    id0, id1, ini, ini, ini, id5, id6, ini,
    id8, id9, ini, ini, ini, idd, ide, ini,
    ie0, ie1, ini, ini, ie4, ie5, ie6, ini,
    ie8, ie9, iea, ini, iec, ied, iee, ini,
    if0, if1, ini, ini, ini, if5, if6, ini,
    if8, if9, ini, ini, ini, ifd, ife, ini
  ]

  cycletime = [
    7, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 0, 4, 6, 0,  # 00
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 10
    6, 6, 0, 0, 3, 3, 5, 0, 4, 2, 2, 0, 4, 4, 6, 0,  # 20
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 30
    6, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 3, 4, 6, 0,  # 40
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 50
    6, 6, 0, 0, 0, 3, 5, 0, 4, 2, 2, 0, 5, 4, 6, 0,  # 60
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 70
    0, 6, 0, 0, 3, 3, 3, 0, 2, 0, 2, 0, 4, 4, 4, 0,  # 80
    2, 6, 0, 0, 4, 4, 4, 0, 2, 5, 2, 0, 0, 5, 0, 0,  # 90
    2, 6, 2, 0, 3, 3, 3, 0, 2, 2, 2, 0, 4, 4, 4, 0,  # A0
    2, 5, 0, 0, 4, 4, 4, 0, 2, 4, 2, 0, 4, 4, 4, 0,  # B0
    2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 3, 0,  # C0
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # D0
    2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 6, 0,  # E0
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0   # F0
  ]

  extracycles = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 00
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 10
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 20
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 30
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 40
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 50
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 60
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 70
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 80
    2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 90
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # A0
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0,  # B0
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # C0
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # D0
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # E0
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0   # F0
  ]
  """
