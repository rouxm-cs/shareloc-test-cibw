#!/usr/bin/env python
# coding: utf8
#
# Copyright (c) 2020 Centre National d'Etudes Spatiales (CNES).
#
# This file is part of Shareloc
# (see https://github.com/CNES/shareloc).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from xml.dom import minidom
from os.path import basename
import numpy as np


def renvoie_linesep(txt_liste_lines):
	"""Renvoie le separateur de ligne d'un texte sous forme de liste de lignes
	Obtenu par readlines
	"""
	if txt_liste_lines[0].endswith('\r\n'):
		line_sep = '\r\n'
	elif txt_liste_lines[0].endswith('\n'):
		line_sep = '\n'
	return line_sep


def identify_dimap(xml_file):
    """
    parse xml file to identify dimap and its version
    :param xml_file : dimap rpc file
    :type xml_file : str
    :return dimap info : dimap_version and None if not an dimap file
    :rtype str
    """
    try :
        xmldoc = minidom.parse(xml_file)
        mtd = xmldoc.getElementsByTagName('Metadata_Identification')
        mtd_format = mtd[0].getElementsByTagName('METADATA_FORMAT')[0].firstChild.data
        is_dimap = mtd_format == 'DIMAP_PHR'
        version = mtd[0].getElementsByTagName('METADATA_PROFILE')[0].attributes.items()[0][1]
        return version
    except:
        return None

def identify_ossim_kwl(ossim_kwl_file):
    """
    parse geom file to identify if it is an ossim model
    :param ossim_kwl_file : ossim keyword list file
    :type ossim_kwl_file : str
    :return ossim kwl info : ossimmodel or not if not an ossim kwl file
    :rtype str
    """
    try :
        with open(ossim_kwl_file) as f:
            content = f.readlines()

        geom_dict = dict()
        for line in content:
            (key, val) = line.split(': ')
            geom_dict[key] = val.rstrip()
        if 'type' in geom_dict.keys():
            if geom_dict['type'].strip().startswith('ossim') :
                return geom_dict['type'].strip()
            else:
                return None
    except:
        return None


def read_eucl_file(eucl_file):
    """
    read euclidium file and parse it
    :param eucl_file : euclidium file
    :type eucl_file : str
    :return parsed file
    :rtype dict
    """
    parsed_file = dict()
    with open(eucl_file, 'r') as fid:
        txt = fid.readlines()

    lsep = renvoie_linesep(txt)

    ind_debut_PX = txt.index('>>\tCOEFF POLYNOME PXOUT' + lsep)
    ind_debut_QX = txt.index('>>\tCOEFF POLYNOME QXOUT' + lsep)
    ind_debut_PY = txt.index('>>\tCOEFF POLYNOME PYOUT' + lsep)
    ind_debut_QY = txt.index('>>\tCOEFF POLYNOME QYOUT' + lsep)

    coeff_PX_str = txt[ind_debut_PX + 1:ind_debut_PX + 21]
    coeff_QX_str = txt[ind_debut_QX + 1:ind_debut_QX + 21]
    coeff_PY_str = txt[ind_debut_PY + 1:ind_debut_PY + 21]
    coeff_QY_str = txt[ind_debut_QY + 1:ind_debut_QY + 21]

    parsed_file['coeff_PX'] = [float(coeff.split()[1]) for coeff in coeff_PX_str]
    parsed_file['coeff_QX'] = [float(coeff.split()[1]) for coeff in coeff_QX_str]
    parsed_file['coeff_PY'] = [float(coeff.split()[1]) for coeff in coeff_PY_str]
    parsed_file['coeff_QY'] = [float(coeff.split()[1]) for coeff in coeff_QY_str]

    # list [offset , scale]
    normalisation_coeff = dict()
    for l in txt:
        if l.startswith('>>\tTYPE_OBJET'):
            if l.split()[-1].endswith('Inverse'):
                parsed_file['type_fic'] = 'I'
            if l.split()[-1].endswith('Directe'):
                parsed_file['type_fic'] = 'D'
        if l.startswith('>>\tXIN_OFFSET'):
            lsplit = l.split()
            if parsed_file['type_fic'] == 'I':
                param ='X'
            else:
                param = 'COL'
            normalisation_coeff[param] = [float(lsplit[4]), float(lsplit[5])]
        if l.startswith('>>\tYIN_OFFSET'):
            if parsed_file['type_fic'] == 'I':
                param ='Y'
            else:
                param = 'LIG'
            lsplit = l.split()
            normalisation_coeff[param] = [float(lsplit[4]), float(lsplit[5])]
        if l.startswith('>>\tZIN_OFFSET'):
            lsplit = l.split()
            normalisation_coeff['ALT'] = [float(lsplit[4]), float(lsplit[5])]
        if l.startswith('>>\tXOUT_OFFSET'):
            lsplit = l.split()
            if parsed_file['type_fic'] == 'D':
                param ='X'
            else:
                param = 'COL'
            normalisation_coeff[param] = [float(lsplit[4]), float(lsplit[5])]
        if l.startswith('>>\tYOUT_OFFSET'):
            lsplit = l.split()
            if parsed_file['type_fic'] == 'D':
                param ='Y'
            else:
                param = 'LIG'
            normalisation_coeff[param] = [float(lsplit[4]), float(lsplit[5])]
    parsed_file['normalisation_coeffs'] = normalisation_coeff
    return parsed_file


def check_coeff_consistency(dict1, dict2):
    """
    print an error message inf normalisations coeff are not consistent
    :param dict1 : normalisation coeffs 1
    :type dict1 : dict
    :param dict2 : normalisation coeffs 2
    :type dict2 : dict

    """
    for key, value in dict1.items() :
        if dict2[key] != value:
            print("normalisation coeffs are different between"
                  " direct en inverse one : {} : {} {}".format(key,value,dict2[key]))


class RPC:
    def __init__(self,rpc_params):
        for a, b in rpc_params.items():
            setattr(self, a, b)

        self.type = 'rpc'
        self.lim_extrapol = 1.0001
        #chaque mononome: c[0]*X**c[1]*Y**c[2]*Z**c[3]
        ordre_monomes_LAI = \
                [[1,0,0,0],[1,1,0,0],[1,0,1,0],\
                 [1,0,0,1],[1,1,1,0],[1,1,0,1],\
                 [1,0,1,1],[1,2,0,0],[1,0,2,0],\
                 [1,0,0,2],[1,1,1,1],[1,3,0,0],\
                 [1,1,2,0],[1,1,0,2],[1,2,1,0],\
                 [1,0,3,0],[1,0,1,2],[1,2,0,1],\
                 [1,0,2,1],[1,0,0,3]]

        self.Monomes    = ordre_monomes_LAI

        #coefficient des degres monomes avec derivation 1ere variable
        self.monomes_deriv_1 = \
                [[0,0,0,0],[1,0,0,0],[0,0,1,0],\
                 [0,0,0,1],[1,0,1,0],[1,0,0,1],\
                 [0,0,1,1],[2,1,0,0],[0,0,2,0],\
                 [0,0,0,2],[1,0,1,1],[3,2,0,0],\
                 [1,0,2,0],[1,0,0,2],[2,1,1,0],\
                 [0,0,3,0],[0,0,1,2],[2,1,0,1],\
                 [0,0,2,1],[0,0,0,3]]

        #coefficient des degres monomes avec derivation 1ere variable
        self.monomes_deriv_2 = \
                [[0,0,0,0],[0,1,0,0],[1,0,0,0],\
                 [0,0,0,1],[1,1,0,0],[0,1,0,1],\
                 [1,0,0,1],[0,2,0,0],[2,0,1,0],\
                 [0,0,0,2],[1,1,0,1],[0,3,0,0],\
                 [2,1,1,0],[0,1,0,2],[1,2,0,0],\
                 [3,0,2,0],[1,0,0,2],[0,2,0,1],\
                 [2,0,1,1],[0,0,0,3]]

    @classmethod
    def from_dimap_v1(cls, dimap_filepath, topleftconvention=False):
        """ load from dimap 
        :param topleftconvention  : [0,0] position
	:param topleftconvention  : boolean 
        If False : [0,0] is at the center of the Top Left pixel 
        If True : [0,0] is at the top left of the Top Left pixel (OSSIM)
        """

        rpc_params = dict()

        if not basename(dimap_filepath).endswith('XML'.upper()):
            raise ValueError("dimap must ends with .xml")


        xmldoc= minidom.parse(dimap_filepath)

        mtd = xmldoc.getElementsByTagName('Metadata_Identification')
        version = mtd[0].getElementsByTagName('METADATA_PROFILE')[0].attributes.items()[0][1]
        rpc_params['driver_type'] = 'dimap_v' + version

        GLOBAL_RFM    = xmldoc.getElementsByTagName('Global_RFM')
        RFM_Validity     = xmldoc.getElementsByTagName('RFM_Validity')
        coeff_LON = [float(el) for el in GLOBAL_RFM[0].getElementsByTagName('F_LON')[0].firstChild.data.split()]
        coeff_LAT = [float(el) for el in GLOBAL_RFM[0].getElementsByTagName('F_LAT')[0].firstChild.data.split()]
        coeff_COL = [float(el) for el in GLOBAL_RFM[0].getElementsByTagName('F_COL')[0].firstChild.data.split()]
        coeff_LIG = [float(el) for el in GLOBAL_RFM[0].getElementsByTagName('F_ROW')[0].firstChild.data.split()]

        A_lon = float(RFM_Validity[0].getElementsByTagName('Lon')[0].getElementsByTagName('A')[0].firstChild.data)
        B_lon = float(RFM_Validity[0].getElementsByTagName('Lon')[0].getElementsByTagName('B')[0].firstChild.data)
        A_lat = float(RFM_Validity[0].getElementsByTagName('Lat')[0].getElementsByTagName('A')[0].firstChild.data)
        B_lat = float(RFM_Validity[0].getElementsByTagName('Lat')[0].getElementsByTagName('B')[0].firstChild.data)
        A_alt = float(RFM_Validity[0].getElementsByTagName('Alt')[0].getElementsByTagName('A')[0].firstChild.data)
        B_alt = float(RFM_Validity[0].getElementsByTagName('Alt')[0].getElementsByTagName('B')[0].firstChild.data)
        A_col = float(RFM_Validity[0].getElementsByTagName('Col')[0].getElementsByTagName('A')[0].firstChild.data)
        B_col = float(RFM_Validity[0].getElementsByTagName('Col')[0].getElementsByTagName('B')[0].firstChild.data)
        A_row = float(RFM_Validity[0].getElementsByTagName('Row')[0].getElementsByTagName('A')[0].firstChild.data)
        B_row = float(RFM_Validity[0].getElementsByTagName('Row')[0].getElementsByTagName('B')[0].firstChild.data)


        rpc_params['offset_COL']    = B_col
        rpc_params['scale_COL']    = A_col
        rpc_params['offset_LIG']    = B_row
        rpc_params['scale_LIG']    = A_row
        rpc_params['offset_ALT']    = B_alt
        rpc_params['scale_ALT']    = A_alt
        rpc_params['offset_X']    = B_lon
        rpc_params['scale_X']    = A_lon
        rpc_params['offset_Y']    = B_lat
        rpc_params['scale_Y']    = A_lat
        rpc_params['Num_X']    = coeff_LON[0:20]
        rpc_params['Den_X']    = coeff_LON[20::]
        rpc_params['Num_Y']    = coeff_LAT[0:20]
        rpc_params['Den_Y']    = coeff_LAT[20::]
        rpc_params['Num_COL']    = coeff_COL[0:20]
        rpc_params['Den_COL']    = coeff_COL[20::]
        rpc_params['Num_LIG']    = coeff_LIG[0:20]
        rpc_params['Den_LIG']    = coeff_LIG[20::]
        #If top left convention, 0.5 pixel shift added on col/row offsets
        if topleftconvention:
            rpc_params['offset_COL'] += 0.5
            rpc_params['offset_LIG'] += 0.5
        return cls(rpc_params)



    @classmethod
    def from_ossim_kwl(cls, ossim_kwl_filename, topleftconvention=False):
        """ Load from a geom file
        :param topleftconvention  : [0,0] position
	:param topleftconvention  : boolean 
        If False : [0,0] is at the center of the Top Left pixel 
        If True : [0,0] is at the top left of the Top Left pixel (OSSIM)
        """

        rpc_params = dict()
        #OSSIM keyword list
        rpc_params['driver_type'] = 'ossim_kwl'


        with open(ossim_kwl_filename) as f:
            content = f.readlines()

        geom_dict = dict()
        for line in content:
            (key, val) = line.split(': ')
            geom_dict[key] = val.rstrip()

        rpc_params['Den_LIG']= [np.nan] * 20
        rpc_params['Num_LIG'] = [np.nan] * 20
        rpc_params['Den_COL']= [np.nan] * 20
        rpc_params['Num_COL'] = [np.nan] * 20
        for index in range(0, 20):
            axis = "line"
            num_den = "den"
            key = "{0}_{1}_coeff_{2:02d}".format(axis, num_den, index)
            rpc_params['Den_LIG'][index] = float(geom_dict[key])
            num_den = "num"
            key = "{0}_{1}_coeff_{2:02d}".format(axis, num_den, index)
            rpc_params['Num_LIG'][index] = float(geom_dict[key])
            axis = "samp"
            key = "{0}_{1}_coeff_{2:02d}".format(axis, num_den, index)
            rpc_params['Num_COL'][index] = float(geom_dict[key])
            num_den = "den"
            key = "{0}_{1}_coeff_{2:02d}".format(axis, num_den, index)
            rpc_params['Den_COL'][index] = float(geom_dict[key])
        rpc_params['offset_COL']    = float(geom_dict["samp_off"])
        rpc_params['scale_COL']    = float(geom_dict["samp_scale"])
        rpc_params['offset_LIG']    = float(geom_dict["line_off"])
        rpc_params['scale_LIG']    = float(geom_dict["line_scale"])
        rpc_params['offset_ALT']    = float(geom_dict["height_off"])
        rpc_params['scale_ALT']    = float(geom_dict["height_scale"])
        rpc_params['offset_X']    = float(geom_dict["long_off"])
        rpc_params['scale_X']    = float(geom_dict["long_scale"])
        rpc_params['offset_Y']    = float(geom_dict["lat_off"])
        rpc_params['scale_Y']    = float(geom_dict["lat_scale"])
        #inverse coeff are not defined
        rpc_params['Num_X'] = None
        rpc_params['Den_X'] = None
        rpc_params['Num_Y'] = None
        rpc_params['Den_Y'] = None
        #If top left convention, 0.5 pixel shift added on col/row offsets
        if topleftconvention:
            rpc_params['offset_COL'] += 0.5
            rpc_params['offset_LIG'] += 0.5

        return cls(rpc_params)



    @classmethod
    def from_euclidium(cls, inverse_euclidium_coeff, direct_euclidium_coeff=None, topleftconvention=False):
        """ load from euclidium
        :param topleftconvention  : [0,0] position
	:param topleftconvention  : boolean 
        If False : [0,0] is at the center of the Top Left pixel 
        If True : [0,0] is at the top left of the Top Left pixel (OSSIM)
        """

        rpc_params = dict()
        rpc_params['driver_type'] = 'euclidium'

        #lecture fichier euclide
        inverse_coeffs = read_eucl_file(inverse_euclidium_coeff)

        if inverse_coeffs['type_fic'] != 'I':
            print("inverse euclidium file is of {} type".format(inverse_coeffs['type_fic']))

        rpc_params['Num_COL'] = inverse_coeffs['coeff_PX']
        rpc_params['Den_COL'] = inverse_coeffs['coeff_QX']
        rpc_params['Num_LIG'] = inverse_coeffs['coeff_PY']
        rpc_params['Den_LIG'] = inverse_coeffs['coeff_QY']

        rpc_params['normalisation_coeffs'] = inverse_coeffs['normalisation_coeffs']
        for key, value in inverse_coeffs['normalisation_coeffs'].items():
            rpc_params['offset_' + key] = value[0]
            rpc_params['scale_' + key] = value[1]

        if direct_euclidium_coeff is not None :
            direct_coeffs = read_eucl_file(direct_euclidium_coeff)
            if direct_coeffs['type_fic'] != 'D':
                print("direct euclidium file is of {} type".format(direct_coeffs['type_fic']))

            check_coeff_consistency(inverse_coeffs['normalisation_coeffs'], direct_coeffs['normalisation_coeffs'])
            rpc_params['Num_X'] = direct_coeffs['coeff_PX']
            rpc_params['Den_X'] = direct_coeffs['coeff_QX']
            rpc_params['Num_Y'] = direct_coeffs['coeff_PY']
            rpc_params['Den_Y'] = direct_coeffs['coeff_QY']
        else:
            rpc_params['Num_X'] = None
            rpc_params['Den_X'] = None
            rpc_params['Num_Y'] = None
            rpc_params['Den_Y'] = None

        #If top left convention, 0.5 pixel shift added on col/row offsets
        if topleftconvention:
            rpc_params['offset_COL'] += 0.5
            rpc_params['offset_LIG'] += 0.5
			
        return cls(rpc_params)

    @classmethod
    def from_any(cls, primary_file, secondary_file=None, topleftconvention=False):

        if basename(primary_file).endswith('XML'.upper()):
           dimap_version = identify_dimap(primary_file)
           if dimap_version is not None :
            if float(dimap_version)<2.0 :
                return cls.from_dimap_v1(primary_file, topleftconvention)
        else:
            ossim_model = identify_ossim_kwl(primary_file)
            if ossim_model is not None:
                    return cls.from_ossim_kwl(primary_file, topleftconvention)
        return cls.from_euclidium(primary_file, secondary_file, topleftconvention)



    def calcule_derivees_inv(self,lon,lat,alt):
        """ calcul analytiques des derivees partielles de la loc inverse
            DCdx: derivee de loc_inv_C p/r a X
            DLdy: derivee de loc_inv_L p/r a Y
        """

        if self.Num_COL:
            Xnorm = (lon - self.offset_X)/self.scale_X
            Ynorm = (lat - self.offset_Y)/self.scale_Y
            Znorm = (alt - self.offset_ALT)/self.scale_ALT
            monomes = np.array([self.Monomes[i][0]*\
                 Xnorm**int(self.Monomes[i][1])*\
                 Ynorm**int(self.Monomes[i][2])*\
                 Znorm**int(self.Monomes[i][3]) for i in range(self.Monomes.__len__())])
            NumDC = np.dot(np.array(self.Num_COL),monomes)
            DenDC = np.dot(np.array(self.Den_COL),monomes)
            NumDL = np.dot(np.array(self.Num_LIG),monomes)
            DenDL = np.dot(np.array(self.Den_LIG),monomes)

            monomes_deriv_x = np.array([self.monomes_deriv_1[i][0]*\
                Xnorm**int(self.monomes_deriv_1[i][1])*\
                Ynorm**int(self.monomes_deriv_1[i][2])*\
                Znorm**int(self.monomes_deriv_1[i][3]) for i in range(self.monomes_deriv_1.__len__())])

            monomes_deriv_y = np.array([self.monomes_deriv_2[i][0]*\
                Xnorm**int(self.monomes_deriv_2[i][1])*\
                Ynorm**int(self.monomes_deriv_2[i][2])*\
                Znorm**int(self.monomes_deriv_2[i][3]) for i in range(self.monomes_deriv_2.__len__())])

            NumDCdx = np.dot(np.array(self.Num_COL),monomes_deriv_x)
            DenDCdx = np.dot(np.array(self.Den_COL),monomes_deriv_x)
            NumDLdx = np.dot(np.array(self.Num_LIG),monomes_deriv_x)
            DenDLdx = np.dot(np.array(self.Den_LIG),monomes_deriv_x)

            NumDCdy = np.dot(np.array(self.Num_COL),monomes_deriv_y)
            DenDCdy = np.dot(np.array(self.Den_COL),monomes_deriv_y)
            NumDLdy = np.dot(np.array(self.Num_LIG),monomes_deriv_y)
            DenDLdy = np.dot(np.array(self.Den_LIG),monomes_deriv_y)

            #derive (u/v)' = (u'v - v'u)/(v*v)
            DCdx = self.scale_COL/self.scale_X*(NumDCdx*DenDC - DenDCdx*NumDC)/DenDC**2
            DCdy = self.scale_COL/self.scale_Y*(NumDCdy*DenDC - DenDCdy*NumDC)/DenDC**2
            DLdx = self.scale_LIG/self.scale_X*(NumDLdx*DenDL - DenDLdx*NumDL)/DenDL**2
            DLdy = self.scale_LIG/self.scale_Y*(NumDLdy*DenDL - DenDLdy*NumDL)/DenDL**2

        return (DCdx,DCdy,DLdx,DLdy)


    def direct_loc_dtm(self, row, col, dtm):
        """
        direct localization on dtm
        :param row :  line sensor position
        :type row : float
        :param col :  column sensor position
        :type col : float
        :param dtm : dtm model
        :type dtm  : shareloc.dtm
        :return ground position (lon,lat,h)
        :rtype numpy.array
        """
        print("direct localization not yet impelemented for RPC model")
        return None

    def direct_loc_h(self,row,col, alt):
        """
        direct localization at constant altitude
        :param row :  line sensor position
        :type row : float or 1D numpy.ndarray dtype=float64
        :param col :  column sensor position
        :type col : float or 1D numpy.ndarray dtype=float64
        :param alt :  altitude
        :type alt : float
        :return ground position (lon,lat,h)
        :rtype numpy.ndarray
        """
        if not isinstance(col, (list, np.ndarray)):
            col = np.array([col])
            row = np.array([row])

        # Direct localization using direct RPC
        if self.Num_X:
            # ground position
            P = np.zeros((col.size, 3))

            Xnorm = (col - self.offset_COL)/self.scale_COL
            Ynorm = (row - self.offset_LIG)/self.scale_LIG
            Znorm = (alt - self.offset_ALT)/self.scale_ALT

            if np.sum(abs(Xnorm) > self.lim_extrapol) == Xnorm.shape[0]:
                print("!!!!! l'evaluation au point est extrapolee en colonne ", Xnorm, col)
            if np.sum(abs(Ynorm) > self.lim_extrapol) == Ynorm.shape[0]:
                print("!!!!! l'evaluation au point est extrapolee en ligne ", Ynorm, row)
            if abs(Znorm) > self.lim_extrapol :
                print("!!!!! l'evaluation au point est extrapolee en altitude ", Znorm, alt)

            monomes = np.array([self.Monomes[i][0]*Xnorm**int(self.Monomes[i][1])*\
                 Ynorm**int(self.Monomes[i][2])*\
                 Znorm**int(self.Monomes[i][3]) for i in range(self.Monomes.__len__())])

            P[:, 0] = np.dot(np.array(self.Num_X), monomes)/np.dot(np.array(self.Den_X), monomes)*self.scale_X+self.offset_X
            P[:, 1] = np.dot(np.array(self.Num_Y), monomes)/np.dot(np.array(self.Den_Y), monomes)*self.scale_Y+self.offset_Y
            P[:, 2] = alt

        # Direct localization using inverse RPC
        else:
            # ground position
            P = np.zeros((col.size, 3))
            P[:, 2] = alt
            (P[:, 0], P[:, 1], P[:, 2]) = self.direct_loc_inverse_iterative(row, col, alt)

        return np.squeeze(P)

    def direct_loc_grid_h(self, row0, col0, steprow, stepcol, nbrow, nbcol, alt):
        """calcule une grille de loc directe a partir des RPC directs
         direct localization  grid at constant altitude
         :param row0 :  grid origin (row)
         :type row0 : int
         :param col0 :  grid origin (col)
         :type col0 : int
         :param steprow :  grid step (row)
         :type steprow : int
         :param stepcol :  grid step (col)
         :type stepcol : int
         :param nbrow :  grid nb row
         :type nbrow : int
         :param nbcol :  grid nb col
         :type nbcol : int
         :param alt : altitude of the grid
         :type alt  : float
         :return direct localization grid
         :rtype numpy.array
        """
        gri_lon = np.zeros((nbrow,nbcol))
        gri_lat = np.zeros((nbrow,nbcol))
        for c in range(int(nbcol)):
            col = col0 + stepcol*c
            for l in range(int(nbrow)):
                row = row0 + steprow*l
                (gri_lon[l,c],gri_lat[l,c],__) = self.direct_loc_h(row,col,alt)
        return (gri_lon,gri_lat)

    def inverse_loc(self, lon, lat, alt):
        """
        Inverse localization

        :param lon: longitude position
        :type lon : float or 1D numpy.ndarray dtype=float64
        :param lat: latitude position
        :type lat : float or 1D numpy.ndarray dtype=float64
        :param alt: altitude
        :type alt : float
        :return: sensor position (row, col, True)
        :rtype numpy.ndarray
        """
        if self.Num_COL:
            if not isinstance(lon, (list, np.ndarray)):
                lon = np.array([lon])
                lat = np.array([lat])

            Xnorm = (lon - self.offset_X)/self.scale_X
            Ynorm = (lat - self.offset_Y)/self.scale_Y
            Znorm = (alt - self.offset_ALT)/self.scale_ALT

            if np.sum(abs(Xnorm) > self.lim_extrapol) == Xnorm.shape[0]:
                print("!!!!! l'evaluation au point est extrapolee en longitude ", Xnorm,lon)
            if np.sum(abs(Ynorm) > self.lim_extrapol) == Ynorm.shape[0]:
                print("!!!!! l'evaluation au point est extrapolee en latitude ", Ynorm,lat)
            if abs(Znorm) > self.lim_extrapol:
                print("!!!!! l'evaluation au point est extrapolee en altitude ", Znorm, alt)

            monomes = np.array([self.Monomes[i][0]*Xnorm**int(self.Monomes[i][1])*\
                Ynorm**int(self.Monomes[i][2])*\
                Znorm**int(self.Monomes[i][3]) for i in range(self.Monomes.__len__())])

            Cout = np.dot(np.array(self.Num_COL), monomes)/np.dot(np.array(self.Den_COL), monomes)*self.scale_COL+self.offset_COL
            Lout = np.dot(np.array(self.Num_LIG), monomes)/np.dot(np.array(self.Den_LIG), monomes)*self.scale_LIG+self.offset_LIG
        else:
            print("!!!!! les coefficient inverses n'ont pas ete definis")
            (Cout, Lout) = (None, None)
        return Lout, Cout, True

    def direct_loc_inverse_iterative(self, row, col, alt, nb_iter_max=10, fill_nan = True):
        """
        Iterative direct localization using inverse RPC

        :param row :  line sensor position
        :type row : float or 1D numpy.ndarray dtype=float64
        :param col :  column sensor position
        :type col : float or 1D numpy.ndarray dtype=float64
        :param alt :  altitude
        :type alt : float
        :param nb_iter_max: max number of iteration
        :type alt : int
        :param fill_nan: fill numpy.nan values with lon and lat offset if true (same as OTB/OSSIM), nan is returned
            otherwise
        :type fill_nan : boolean
        :return: ground position (lon,lat,h)
        :rtype list of numpy.array
        """
        if self.Num_COL:

            if not isinstance(row, (list, np.ndarray)):
                col = np.array([col])
                row = np.array([row])
            filter_nan = np.logical_not(np.logical_or(np.isnan(col),np.isnan(row)))

            if fill_nan:
                lon_nan_value = self.offset_X
                lat_nan_value = self.offset_Y
            else:
                lon_nan_value = np.nan
                lat_nan_value = np.nan
            long_out = np.full(row.size,lon_nan_value)
            lat_out = np.full(row.size, lat_nan_value)

            row=row[filter_nan]
            col=col[filter_nan]

            # if all coord
            #  contains Nan then return
            if not np.any(filter_nan):
                return long_out, lat_out, alt

            # inverse localization starting from the center of the scene
            X = np.array([self.offset_X])
            Y = np.array([self.offset_Y])
            (l0, c0, __) = self.inverse_loc(X, Y, alt)

            # desired precision in pixels
            eps = 1e-6

            iteration = 0
            # computing the residue between the sensor positions and those estimated by the inverse localization
            dc = col - c0
            dl = row - l0

            # ground coordinates (latitude and longitude) of each point
            X = np.repeat(X, dc.size)
            Y = np.repeat(Y, dc.size)
            # while the required precision is not achieved
            while (np.max(abs(dc)) > eps or np.max(abs(dl)) > eps) and iteration < nb_iter_max:
                # list of points that require another iteration
                iter_ = np.where((abs(dc) > eps) | (abs(dl) > eps))[0]

                # partial derivatives
                (Cdx, Cdy, Ldx, Ldy) = self.calcule_derivees_inv(X[iter_], Y[iter_], alt)
                det = Cdx*Ldy-Ldx*Cdy

                dX = (Ldy*dc[iter_] - Cdy*dl[iter_])/det
                dY = (-Ldx*dc[iter_] + Cdx*dl[iter_])/det

                # update ground coordinates
                X[iter_] += dX
                Y[iter_] += dY

                # inverse localization
                (l, c, __) = self.inverse_loc(X[iter_], Y[iter_], alt)

                # updating the residue between the sensor positions and those estimated by the inverse localization
                dc[iter_] = col[iter_] - c
                dl[iter_] = row[iter_] - l
                iteration += 1
            long_out[filter_nan] = X
            lat_out[filter_nan] = Y

        else:
            print("!!!!! les coefficient inverses n'ont pas ete definis")
            (long_out, lat_out) = (None, None)

        return long_out, lat_out, alt

    def get_alt_min_max(self):
        """
        returns altitudes min and max layers
        :return alt_min,lat_max
        :rtype list
        """
        return [self.offset_ALT - self.scale_ALT / 2.0, self.offset_ALT + self.scale_ALT / 2.0]

    def los_extrema(self, row, col, alt_min, alt_max):
        """
        compute los extrema
        :param row  :  line sensor position
        :type row  : float
        :param col :  column sensor position
        :type col : float
        :param alt_min : los alt min
        :type alt_min  : float
        :param alt_max : los alt max
        :type alt_max : float
        :return los extrema
        :rtype numpy.array (2x3)
        """
        los_edges = np.zeros([2, 3])
        los_edges[0, :] = self.direct_loc_h(row, col, alt_max)
        los_edges[1, :] = self.direct_loc_h(row, col, alt_min)
        return los_edges
