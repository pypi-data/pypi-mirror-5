import pypet

__author__ = 'Robert Meyer'


import numpy as np
import unittest
from pypet.parameter import Parameter, PickleParameter, BaseParameter, ArrayParameter
import pickle
import scipy.sparse as spsp
import pypet.petexceptions as pex


class Dummy():
    pass

class ParameterTest(unittest.TestCase):


    def testMetaSettings(self):
        for key, param in self.param.__dict__.items():
            self.assertEqual(param.v_full_name, self.location+'.'+key)
            self.assertEqual(param.v_name, key)
            self.assertEqual(param.v_location, self.location)


    def make_params(self):
        self.param = Dummy()
        for key, val in self.data.__dict__.items():
            self.param.__dict__[key] = Parameter(self.location+'.'+key, val, comment=key)


    def setUp(self):

        if not hasattr(self,'data'):
            self.data=Dummy()

        self.data.val0 = 1
        self.data.val1 = 1.0
        self.data.val2 = True
        self.data.val3 = 'String'
        self.data.npfloat = np.array([1.0,2.0,3.0])
        self.data.npfloat_2d = np.array([[1.0,2.0],[3.0,4.0]])
        self.data.npbool= np.array([True,False, True])
        self.data.npstr = np.array(['Uno', 'Dos', 'Tres'])
        self.data.npint = np.array([1,2,3])

        self.location = 'MyName.Is.myParam'





        self.make_params()




        # with self.assertRaises(AttributeError):
        #     self.param.val0.f_set([[1,2,3],[1,2,3]])

        #Add explortation:
        self.explore()

    def explore(self):
        self.explore_dict={'npstr':[np.array(['Uno', 'Dos', 'Tres']),
                               np.array(['Cinco', 'Seis', 'Siette']),
                            np.array(['Ocho', 'Nueve', 'Diez'])],
                           'val0':[1,2,3]}

        ## Explore the parameter:
        for key, vallist in self.explore_dict.items():
            self.param.__dict__[key]._explore(vallist)




    def test_the_insertion_made_implicetly_in_setUp(self):
        for key, val in self.data.__dict__.items():

            if not key in self.explore_dict:
                param_val = self.param.__dict__[key].f_get()
                self.assertTrue(np.all(str(val) == str(param_val)),'%s != %s'  %(str(val),str(param_val)))





    def test_exploration(self):
        for key, vallist in self.explore_dict.items():

            param = self.param.__dict__[key]

            for idx, val in enumerate(vallist):
                assert isinstance(param, BaseParameter)
                param.f_set_parameter_access(idx)

                self.assertTrue(np.all(repr(param.f_get())==repr(val))),'%s != %s'%( str(param.f_get()),str(val))


    def test_storage_and_loading(self):

        for key, param in self.param.__dict__.items():
            store_dict = param._store()

            constructor = param.__class__

            param.f_unlock()
            param.f_empty()

            param = constructor('')

            param._load(store_dict)

            param._rename(self.location+'.'+key)

            self.param.__dict__[key] = param


        self.test_the_insertion_made_implicetly_in_setUp()

        self.test_exploration()

        self.testMetaSettings()


    def test_pickling_without_multiprocessing(self):
        for key, param in self.param.__dict__.items():
            param.f_unlock()
            param.v_full_copy=True

            dump = pickle.dumps(param)

            newParam = pickle.loads(dump)



            self.param.__dict__[key] = newParam

        self.test_exploration()

        self.test_the_insertion_made_implicetly_in_setUp()

        self.testMetaSettings()


    def test_pickling_with_multiprocessing(self):
        for key, param in self.param.__dict__.items():
            param.f_unlock()
            param.v_full_copy=False

            dump = pickle.dumps(param)

            newParam = pickle.loads(dump)



            self.param.__dict__[key] = newParam

        #self.test_exploration()

        self.test_the_insertion_made_implicetly_in_setUp()

        self.testMetaSettings()


    def testresizinganddeletion(self):

        for key, param in self.param.__dict__.items():
            param.f_lock()
            with self.assertRaises(pex.ParameterLockedException):
                 param.f_set(42)

            with self.assertRaises(pex.ParameterLockedException):
                param._shrink()

            param.f_unlock()


            if len(param)> 1:
                self.assertTrue(param.f_is_array())

            if param.f_is_array():
                self.assertTrue(len(param)>1)

            param._shrink()
            self.assertTrue(len(param) == 1)

            self.assertFalse(param.f_is_empty())
            self.assertFalse(param.f_is_array())



            param.f_empty()

            self.assertTrue(param.f_is_empty())
            self.assertFalse(param.f_is_array())

class ArrayParameterTest(ParameterTest):

    def setUp(self):


        if not hasattr(self,'data'):
            self.data=Dummy()


        self.data.myinttuple = (1,2,3)
        self.data.mydoubletuple = (42.0,43.7,33.3)
        self.data.mystringtuple = ('Eins','zwei','dr3i')

        super(ArrayParameterTest,self).setUp()

        ## For the rest of the checkings, lists are converted to tuples:
        for key, val in self.data.__dict__.items():
            if isinstance(val, list):
                self.data.__dict__[key] = tuple(val)


    def make_params(self):
        self.param = Dummy()
        for key, val in self.data.__dict__.items():
            self.param.__dict__[key] = ArrayParameter(self.location+'.'+key, val, comment=key)


    def explore(self):

        matrices = []


        self.explore_dict={'npstr':[np.array(['Uno', 'Dos', 'Tres']),
                               np.array(['Cinco', 'Seis', 'Siette']),
                            np.array(['Ocho', 'Nueve', 'Diez'])],
                           'val0':[1,2,3],
                           'myinttuple':[(1,2,1),(4,5,6),(5,6,7)]}

        ### Convert the explored stuff into numpy arrays
        #for idx, val in enumerate(self.explore_dict['myinttuple']):
         #   self.explore_dict['myinttuple'][idx] = np.array(val)


        ## Explore the parameter:
        for key, vallist in self.explore_dict.items():
            self.param.__dict__[key]._explore(vallist)


class PickleParameterTest(ParameterTest):

    def setUp(self):


        if not hasattr(self,'data'):
            self.data=Dummy()

        self.data.spsparse_csc = spsp.csc_matrix((1000,100))
        self.data.spsparse_csc[1,2] = 44.5

        self.data.spsparse_csr = spsp.csr_matrix((2222,22))
        self.data.spsparse_csr[1,3] = 44.5

        self.data.spsparse_lil = spsp.lil_matrix((111,111))
        self.data.spsparse_lil[3,2] = 44.5

        super(PickleParameterTest,self).setUp()


    def make_params(self):
        self.param = Dummy()
        for key, val in self.data.__dict__.items():
            self.param.__dict__[key] = PickleParameter(self.location+'.'+key, val, comment=key)



    def explore(self):




        matrices = []
        for irun in range(3):

            spsparse_lil = spsp.lil_matrix((111,111))
            spsparse_lil[3,2] = 44.5*irun

            matrices.append(spsparse_lil)


        self.explore_dict={'npstr':[np.array(['Uno', 'Dos', 'Tres']),
                               np.array(['Cinco', 'Seis', 'Siette']),
                            np.array(['Ocho', 'Nueve', 'Diez'])],
                           'val0':[1,2,3],
                           'spsparse_lil' : matrices}




        ## Explore the parameter:
        for key, vallist in self.explore_dict.items():
            self.param.__dict__[key]._explore(vallist)




if __name__ == '__main__':
    unittest.main()
