from traits.trait_types import self

__author__ = 'Robert Meyer'

import numpy as np
import unittest
from pypet.parameter import Parameter, PickleParameter, BaseResult, ArrayParameter, PickleResult, BaseParameter
from pypet.trajectory import Trajectory, SingleRun
from pypet.storageservice import LazyStorageService
from pypet.utils.explore import cartesian_product
from pypet.environment import Environment
from pypet.storageservice import HDF5StorageService
from pypet import globally
import pickle
import logging
import cProfile
from pypet.utils.helpful_functions import flatten_dictionary
import scipy.sparse as spsp
import os
import shutil
import pandas as pd
from pypet.utils.comparisons import results_equal,parameters_equal
from pypet.utils.helpful_functions import nested_equal

## Removes all the files again to clean up after the tests
REMOVE = True


def simple_calculations(traj, arg1, simple_kwarg):


        all_mat = traj.csc_mat + traj.lil_mat + traj.csr_mat
        Normal_int= traj.Normal.int
        Sum= np.sum(traj.Numpy.double)

        result_mat = all_mat * Normal_int * Sum * arg1 * simple_kwarg



        my_dict = {}

        my_dict2={}
        my_dict3={}
        my_dict4={}
        for key, val in traj.f_to_dict(fast_access=True,short_names=False).items():
            newkey = key.replace('.','_')
            my_dict[newkey] = str(val)
            my_dict2[newkey] =(str(val)+' juhu!')
            my_dict3[newkey] =[str(val)+' juhuhu!']
            my_dict4[newkey]= np.array([str(val)+' Woopieee!'])

        keys = traj.f_to_dict(short_names=False).keys()
        for idx,key in enumerate(keys):
            keys[idx] = key.replace('.','_')

        traj.f_add_result('List.Of.Keys', dict1=my_dict, dict2=my_dict2, dict3=my_dict3,dict4=my_dict4)
        traj.f_add_result('DictsNFrame', keys=keys)
        traj.f_add_result('ResMatrix',result_mat.todense())
        traj.f_add_derived_parameter('All.To.String', str(traj.f_to_dict(fast_access=True,short_names=False)))

        myframe = pd.DataFrame(data ={'TC1':[1,2,3],'TC2':['Waaa',np.nan,''],'TC3':[1.2,42.2,np.nan]})

        traj.DictsNFrame.f_set(myframe)

        traj.f_add_result('IStore.SimpleThings',1.0,3,np.float32(5.0), 'Iamstring',(1,2,3),[4,5,6],zwei=2)

        traj.f_add_result(PickleResult, 'PickleTerror',  test=traj.SimpleThings).f_set_annotations(
            *[1,'hhhhh'],
            **{'peter':np.array([1,2,3,4]),'cat':'fish',
                                     'kkk' : np.array(['1','2','sdfsf'])})

class EnvironmentTest(unittest.TestCase):


    def set_mode(self):
        self.mode = 'LOCK'
        self.multiproc = False
        self.ncores = 1

    def _create_param_dict(self):
        self.param_dict = {}

        self.param_dict['Normal'] = {}
        self.param_dict['Numpy'] = {}
        self.param_dict['Sparse'] ={}
        self.param_dict['Numpy_2D'] = {}
        self.param_dict['Numpy_3D'] = {}
        self.param_dict['Tuples'] ={}

        normal_dict = self.param_dict['Normal']
        normal_dict['string'] = 'Im a test string!'
        normal_dict['int'] = 42
        normal_dict['double'] = 42.42
        normal_dict['bool'] =True
        normal_dict['trial'] = 0

        numpy_dict=self.param_dict['Numpy']
        numpy_dict['string'] = np.array(['Uno', 'Dos', 'Tres'])
        numpy_dict['int'] = np.array([1,2,3,4])
        numpy_dict['double'] = np.array([1.0,2.0,3.0,4.0])
        numpy_dict['bool'] = np.array([True,False, True])

        self.param_dict['Numpy_2D']['double'] = np.array([[1.0,2.0],[3.0,4.0]])
        self.param_dict['Numpy_3D']['double'] = np.array([[[1.0,2.0],[3.0,4.0]],[[3.0,-3.0],[42.0,41.0]]])

        spsparse_csc = spsp.csc_matrix((2222,22))
        spsparse_csc[1,2] = 44.6

        spsparse_csr = spsp.csr_matrix((2222,22))
        spsparse_csr[1,3] = 44.7

        spsparse_lil = spsp.lil_matrix((2222,22))
        spsparse_lil[3,2] = 44.5

        self.param_dict['Sparse']['lil_mat'] = spsparse_lil
        self.param_dict['Sparse']['csc_mat'] = spsparse_csc
        self.param_dict['Sparse']['csr_mat'] = spsparse_csr

        self.param_dict['Tuples']['int'] = (1,2,3)
        self.param_dict['Tuples']['float'] = (44.4,42.1,3.)
        self.param_dict['Tuples']['str'] = ('1','2wei','dr3i')


    def add_params(self,traj):

        flat_dict = flatten_dictionary(self.param_dict,'.')

        for key, val in flat_dict.items():
            if isinstance(val, (np.ndarray,list, tuple)):
                traj.f_add_parameter(ArrayParameter,key,val, )
            elif isinstance(val, (int,str,bool,float)):
                traj.f_add_parameter(Parameter,key,val, comment='Im a comment!')
            elif spsp.isspmatrix(val):
                traj.f_add_parameter(PickleParameter,key,val).v_annotations.f_set(
                    **{'Name':key,'Val' :str(val),'Favorite_Numbers:':[1,2,3],
                                     'Second_Fav':np.array([43.0,43.0])})
            else:
                raise RuntimeError('You shall not pass, %s is %s!' % (str(val),str(type(val))))

        traj.f_add_derived_parameter('Another.String', 'Hi, how are you?')



    def explore(self, traj):
        self.explored ={'Normal.trial': [0],
            'Numpy.double': [np.array([1.0,2.0,3.0,4.0]), np.array([-1.0,3.0,5.0,7.0])],
            'lil_mat' :[spsp.lil_matrix((2222,22)), spsp.lil_matrix((2222,22))]}

        self.explored['lil_mat'][0][1,2]=44.0
        self.explored['lil_mat'][1][2,2]=33


        traj.f_explore(cartesian_product(self.explored))



    def setUp(self):
        self.set_mode()

        logging.basicConfig(level = logging.DEBUG)

        self.filename = '../../experiments/tests/HDF5/test.hdf5'
        self.logfolder = '../../experiments/tests/Log'
        self.trajname = 'Test'

        env = Environment(trajectory=self.trajname,filename=self.filename,
                          file_title=self.trajname, log_folder=self.logfolder)

        traj = env.v_trajectory

        traj.multiproc = self.multiproc
        traj.wrap_mode = self.mode
        traj.ncores = self.ncores

        traj.v_standard_parameter=Parameter

        ## Create some parameters
        self._create_param_dict()
        ### Add some parameter:
        self.add_params(traj)

        #remember the trajectory and the environment
        self.traj = traj
        self.env = env



    def make_run(self):

        ### Make a test run
        simple_arg = -13
        simple_kwarg= 13.0
        self.env.f_run(simple_calculations,simple_arg,simple_kwarg=simple_kwarg)


    def test_run(self):

        ###Explore
        self.explore(self.traj)

        ###Test, that you cannot append to data
        with self.assertRaises(ValueError):
            self.traj.f_store_item('filename')

        self.make_run()

        newtraj = self.load_trajectory(trajectory_index=-1,as_new=True)
        self.traj.f_update_skeleton()
        self.traj.f_load_items(self.traj.f_to_dict().keys(), only_empties=True)

        self.compare_trajectories(self.traj,newtraj)



    def load_trajectory(self,trajectory_index=None,trajectory_name=None,as_new=True):
        ### Load The Trajectory and check if the values are still the same
        newtraj = Trajectory()
        newtraj.v_storage_service=HDF5StorageService(filename=self.filename)
        newtraj.f_load(trajectory_name=trajectory_name, load_derived_parameters=2,load_results=2,
                       trajectory_index=trajectory_index)
        return newtraj

    def compare_trajectories(self,traj1,traj2):

        old_items = traj1.f_to_dict(fast_access=False)
        new_items = traj2.f_to_dict(fast_access=False)



        self.assertEqual(len(old_items),len(new_items))
        for key,item in new_items.items():
            old_item = old_items[key]
            if key.startswith('config'):
                continue

            if isinstance(item, BaseParameter):
                self.assertTrue(parameters_equal(item,old_item),
                                'For key %s: %s not equal to %s' %(key,str(old_item),str(item)))
            elif isinstance(item,BaseResult):
                self.assertTrue(results_equal(item, old_item),
                                'For key %s: %s not equal to %s' %(key,str(old_item),str(item)))
            else:
                raise RuntimeError('You shall not pass')

            self.assertTrue(nested_equal(item.v_annotations,old_item.v_annotations),'%s != %s' %
                        (item.v_annotations.f_ann_to_str(),old_item.v_annotations.f_ann_to_str()))


class MultiprocQueueTest(EnvironmentTest):

    def set_mode(self):
        self.mode = globally.WRAP_MODE_QUEUE
        self.multiproc = True
        self.ncores = 2


class MultiprocLockTest(EnvironmentTest):

     def set_mode(self):
        self.mode = globally.WRAP_MODE_LOCK
        self.multiproc = True
        self.ncores = 2




if __name__ == '__main__':
    if REMOVE:
        shutil.rmtree('../../Test',True)
    unittest.main()