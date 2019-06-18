"""
mpbas module.  Contains the ModpathBas class. Note that the user can access
the ModpathBas class as `flopy.modflow.ModpathBas`.

Additional information for this MODFLOW/MODPATH package can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/index.html?bas6.htm>`_.

"""
import numpy as np
from numpy import empty, array
from ..pakbase import Package
from ..utils import Util2d, Util3d

class ModpathBas(Package):
    """
    MODPATH Basic Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.modpath.mp.Modpath`) to which
        this package will be added.
    hnoflo : float
        Head value assigned to inactive cells (default is -9999.).
    hdry : float
        Head value assigned to dry cells (default is -8888.).
    def_face_ct : int
        Number fo default iface codes to read (default is 0).
    bud_label : str or list of strs
        MODFLOW budget item to which a default iface is assigned.
    def_iface : int or list of ints
        Cell face (iface) on which to assign flows from MODFLOW budget file.
    laytyp : int or list of ints
        MODFLOW layer type (0 is convertible, 1 is confined).
    ibound : array of ints, optional
        The ibound array (the default is 1).
    prsity : array of ints, optional
        The porosity array (the default is 0.30).
    prsityCB : array of ints, optional
        The porosity array for confining beds (the default is 0.30).
    extension : str, optional
        File extension (default is 'mpbas').

    Attributes
    ----------
    heading : str
        Text string written to top of package input file.

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modpath.Modpath()
    >>> mpbas = flopy.modpath.ModpathBas(m)

    """
    def __init__(self, model, hnoflo=-9999., hdry=-8888.,
                 def_face_ct=0, bud_label=None, def_iface=None,
                 laytyp=0, ibound=1, prsity=0.30, prsityCB=0.30,
                 extension='mpbas', unitnumber = 86):
        """
        Package constructor.

        """
        Package.__init__(self, model, extension, 'MPBAS', unitnumber) 
        nrow, ncol, nlay, nper = self.parent.mf.nrow_ncol_nlay_nper
        self.parent.mf.get_name_file_entries()
        self.heading1 = '# MPBAS for Modpath, generated by Flopy.'
        self.heading2 = '#'
        self.hnoflo = hnoflo
        self.hdry = hdry
        self.def_face_ct = def_face_ct
        self.bud_label = bud_label
        self.def_iface = def_iface
        self.laytyp = laytyp
        self.ibound = Util3d(model, (nlay, nrow, ncol), np.int32, ibound,
                              name='ibound', locat=self.unit_number[0])
        
        self.prsity = prsity
        self.prsityCB = prsityCB
        self.prsity = Util3d(model,(nlay,nrow,ncol),np.float32,\
                              prsity,name='prsity',locat=self.unit_number[0])        
        self.prsityCB = Util3d(model,(nlay,nrow,ncol),np.float32,\
                                prsityCB,name='prsityCB',locat=self.unit_number[0])        
        self.parent.add_package(self)

    def write_file(self):
        """
        Write the package file

        Returns
        -------
        None

        """
        nrow, ncol, nlay, nper = self.parent.mf.nrow_ncol_nlay_nper
        ModflowDis = self.parent.mf.get_package('DIS')
        # Open file for writing
        f_bas = open(self.fn_path, 'w')
        f_bas.write('#{0:s}\n#{1:s}\n'.format(self.heading1,self.heading2))
        f_bas.write('{0:16.6f} {1:16.6f}\n'\
                    .format(self.hnoflo, self.hdry))
        f_bas.write('{0:4d}\n'\
                    .format(self.def_face_ct))
        if self.def_face_ct > 0:
            for i in range(self.def_face_ct):
                f_bas.write('{0:20s}\n'.format(self.bud_label[i]))
                f_bas.write('{0:2d}\n'.format(self.def_iface[i]))
        #f_bas.write('\n')
  
        flow_package = self.parent.mf.get_package('BCF6')
        if (flow_package != None):
            lc = Util2d(self.parent,(nlay,),np.int32,\
                         flow_package.laycon.get_value(),name='bas - laytype',\
                         locat=self.unit_number[0])
        else:
            flow_package = self.parent.mf.get_package('LPF')
            if (flow_package != None):
                lc = Util2d(self.parent,(nlay,),\
                             np.int32,flow_package.laytyp.get_value(),\
                             name='bas - laytype',locat=self.unit_number[0])
            else:
                flow_package = self.parent.mf.get_package('UPW')
                if (flow_package != None):
                    lc = Util2d(self.parent,(nlay,),\
                                 np.int32,flow_package.laytyp.get_value(),\
                                 name='bas - laytype', locat=self.unit_number[0])
        # need to reset lc fmtin
        lc.set_fmtin('(40I2)')
        f_bas.write(lc.string)
        # from modpath bas--uses keyword array types
        f_bas.write(self.ibound.get_file_entry())
        # from MT3D bas--uses integer array types
        #f_bas.write(self.ibound.get_file_entry())
        f_bas.write(self.prsity.get_file_entry())
        f_bas.write(self.prsityCB.get_file_entry())
        
        f_bas.close() 
