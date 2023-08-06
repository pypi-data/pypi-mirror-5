    # encoding: utf-8
import mozaik
import numpy
from mozaik.connectors import Connector
from mozaik.connectors.modular_connector_functions import ModularConnectorFunction
from collections import Counter
from parameters import ParameterSet, ParameterDist
from mozaik.tools.misc import sample_from_bin_distribution, normal_function
from mozaik import load_component


logger = mozaik.getMozaikLogger()

class ModularConnector(Connector):
    """
    An abstract connector than allows for mixing of various factors that can affect the connectivity.
    
    The connector sepparates the implementation of delays from the implementation of weights.
    
    It receives a dictionary of weight functions and a dictonary of delays functions each being an instance of ModularConnectorFunction. 
    In both cases the list of functions is combined by using expression string which is a parameter of this class (see parameters for details). 
    
    The values returned by the ModularConnectorFunction will be considered to be in miliseconds when used for specifying delays, or the units used by pyNN for weights 
    in case of specifying weights.
    
    The ModularConnector then sets such computed values of weights and delays directly in the connections.
    
    
    """

    required_parameters = ParameterSet({
        'weight_functions' : ParameterSet, # a dictionary of ModularConnectorFunction's and their parameters that will be used to determine the weights.
                                           # strucutured as follows
                                           #            {
                                           #                 component : 'class_name_of_the_ModularConnectorFunction',
                                           #                 params : {
                                           #                           ...
                                           #                         }
                                           #             }
        'delay_functions' : ParameterSet, # the same as weight_functions but for delays
        'weight_expression' : str, # a python expression that can use variables f1..fn where n is the number of functions in weight_functions, and fi corresponds to the name given to a ModularConnectorFunction in weight_function ParameterSet. It determines how are the weight functions combined to obtain the weights
        'delay_expression' : str, # a python expression that can use variables f1..fn where n is the number of functions in delays_functions, and fi corresponds to the name given to a ModularConnectorFunction in delays_function ParameterSet. It determines how are the delays functions combined to obtain the delays
    })
    
    def __init__(self, network, name,source, target, parameters):
      Connector.__init__(self, network, name, source,target,parameters)
      
      # lets load up the weight ModularConnectorFunction's
      self.weight_functions = {}
      for k in self.parameters.weight_functions.keys():
          self.weight_functions[k] = load_component(self.parameters.weight_functions[k].component)(self.source,self.target,self.parameters.weight_functions[k].params)
          assert isinstance(self.weight_functions[k],ModularConnectorFunction)
          
      # lets load up the delay ModularConnectorFunction's
      self.delay_functions = {}
      for k in self.parameters.delay_functions.keys():
          self.delay_functions[k] = load_component(self.parameters.delay_functions[k].component)(self.source,self.target,self.parameters.delay_functions[k].params)
    
    def _obtain_weights(self,i):
        """
        This function calculates the combined weights from the ModularConnectorFunction in weight_functions
        """
        evaled = {}
        for k in self.weight_functions.keys():
            evaled[k] = self.weight_functions[k].evaluate(i)
        return numpy.zeros((self.source.pop.size,)) + eval(self.parameters.weight_expression,globals(),evaled)
        
    def _obtain_delays(self,i):
        """
        This function calculates the combined weights from the ModularConnectorFunction in weight_functions
        """
        evaled = {}
        for k in self.delay_functions.keys():
            evaled[k] = self.delay_functions[k].evaluate(i)
        
        delays = numpy.zeros((self.source.pop.size,)) + eval(self.parameters.delay_expression,globals(),evaled)
        #round to simulation step            
        delays = numpy.rint(delays / self.sim.get_time_step()) * self.sim.get_time_step()
        return delays
        
    def _connect(self):
        connection_list = []
        z = numpy.zeros((self.target.pop.size,))
        for i in xrange(0,self.target.pop.size):
            connection_list.extend(zip(numpy.arange(0,self.source.pop.size,1),z+i,self._obtain_weights(i).flatten(),self._obtain_delays(i).flatten()))
        
        self.method = self.sim.FromListConnector(connection_list)
        self.proj = self.sim.Projection(
                                self.source.pop,
                                self.target.pop,
                                self.method,
                                synapse_type=self.init_synaptic_mechanisms(),
                                label=self.name,
                                receptor_type=self.parameters.target_synapses)

class ModularSamplingProbabilisticConnector(ModularConnector):
    """
    ModularConnector that interprets the weights as proportional probabilities of connectivity
    and for each neuron out connections it samples num_samples of
    connections that actually get realized according to these weights.
    Each such sample connections will have weight equal to
    base_weight/num_samples but note that there can be multiple
    connections between a pair of neurons in this sample (in which case the
    weights are set to the multiple of the base weights times the number of
    occurrences in the sample).
    """

    required_parameters = ParameterSet({
        'num_samples': int,
        'base_weight' : float
    })

    def _connect(self):
        cl = []
        for i in xrange(0,self.target.pop.size):
            weights = self._obtain_weights(i)
            delays = self._obtain_delays(i)
            co = Counter(sample_from_bin_distribution(weights, self.parameters.num_samples))
            cl.extend([(k,i,self.parameters.base_weight*co[k]/self.parameters.num_samples,delays[k]) for k in co.keys()])
        
        method = self.sim.FromListConnector(cl)
        self.proj = self.sim.Projection(
                                self.source.pop,
                                self.target.pop,
                                method,
                                synapse_type=self.init_synaptic_mechanisms(),
                                label=self.name,
                                receptor_type=self.parameters.target_synapses)
    

class ModularSingleWeightProbabilisticConnector(ModularConnector):
    """
    ModularConnector that interprets the weights as proportional probabilities of connectivity.
    The parameter connection_probability is interepreted as the average probability that two neurons will be connected in this 
    projection. For each pair this connecter will make one random choice of connecting them (where the probability of this choice
    is determined as the proportional probability of the corresponding weight normalized by the connection_probability parameter).
    It will set each connections to the weight base_weight.
    """

    required_parameters = ParameterSet({
        'connection_probability': float,
        'base_weight' : float
    })

    def _connect(self):
        cl = []
        for i in xrange(0,self.target.pop.size):
            weights = self._obtain_weights(i)
            delays = self._obtain_delays(i)
            conections_probabilities = weights/numpy.sum(weights)*self.parameters.connection_probability*len(weights)
            connection_indices = numpy.flatnonzero(conections_probabilities > numpy.random.rand(len(conections_probabilities)))
            cl.extend([(k,i,self.parameters.base_weight,delays[k]) for k in connection_indices])
        
        method = self.sim.FromListConnector(cl)
        self.proj = self.sim.Projection(
                                self.source.pop,
                                self.target.pop,
                                method,
                                synapse_type=self.init_synaptic_mechanisms(),
                                label=self.name,
                                receptor_type=self.parameters.target_synapses)





