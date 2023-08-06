# Copyright (c) 2012 Leif Johnson <leif@leifjohnson.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''This file contains optimization methods for neural networks.'''

import collections
import itertools
import lmj.cli
import numpy as np
import numpy.random as rng
import theano
import theano.tensor as TT
import sys

from . import dataset
from . import feedforward
from . import recurrent

logging = lmj.cli.get_logger(__name__)

def mean_map(f, xs):
    return np.mean([f(*x) for x in xs], axis=0)


class Trainer(object):
    '''This is a base class for all trainers.'''

    def train(self, train_set, valid_set=None, **kwargs):
        '''By default, we train in iterations and evaluate periodically.'''
        best_cost = 1e100
        best_iter = 0
        best_params = [p.get_value().copy() for p in self.params]
        for i in xrange(self.iterations):
            if i - best_iter > self.patience:
                logging.error('patience elapsed, bailing out')
                break
            try:
                fmt = 'SGD update %i/%i @%.2e train %s'
                args = (i + 1,
                        self.iterations,
                        self.learning_rate,
                        mean_map(self.f_train, train_set),
                        )
                if (i + 1) % self.validation_frequency == 0:
                    metrics = mean_map(self.f_eval, valid_set)
                    fmt += ' valid %s'
                    args += (metrics, )
                    if (best_cost - metrics[0]) / best_cost > self.min_improvement:
                        best_cost = metrics[0]
                        best_iter = i
                        best_params = [p.get_value().copy() for p in self.params]
                        fmt += ' *'
                    else:
                        self.validation_stagnant()
                self.finish_iteration()
            except KeyboardInterrupt:
                logging.info('interrupted !')
                break
            logging.info(fmt, *args)
        self.update_params(best_params)

    def update_params(self, targets):
        for param, target in zip(self.params, targets):
            param.set_value(target)

    def finish_iteration(self):
        pass

    def validation_stagnant(self):
        pass

    def evaluate(self, test_set):
        return mean_map(self.f_eval, test_set)


class SGD(Trainer):
    '''Stochastic gradient descent network trainer.'''

    def __init__(self, network, **kwargs):
        self.params = network.params(**kwargs)
        self.validation_frequency = kwargs.get('validate', 3)
        self.min_improvement = kwargs.get('min_improvement', 0.)
        self.iterations = kwargs.get('num_updates', 1e100)
        self.patience = kwargs.get('patience', 1e100)
        logging.info('SGD: %d named parameters to learn', len(self.params))

        decay = kwargs.get('learning_rate_decay', 0.01)
        m = kwargs.get('momentum', 0.1)
        lr = kwargs.get('learning_rate', 0.1)

        J = network.J(**kwargs)
        t = theano.shared(np.cast['float32'](0), name='t')
        updates = collections.OrderedDict()
        updates.update(network.updates)
        for param in self.params:
            grad = TT.grad(J, param)
            heading = theano.shared(
                np.zeros_like(param.get_value(borrow=True)),
                name='grad_%s' % param.name)
            updates[param] = param + heading
            updates[heading] = m * heading - lr * ((1 - decay) ** t) * grad

        costs = [J] + network.monitors
        self.f_eval = theano.function(network.inputs, costs)
        self.f_train = theano.function(network.inputs, costs, updates=updates)
        self.f_rate = theano.function([], [lr * ((1 - decay) ** t)])
        self.f_finish = theano.function([], [t], updates={t: t + 1})

        #theano.printing.pydotprint(
        #    theano.function(network.inputs, [J]), '/tmp/theano-network.png')

        #g = self.f_train.maker.fgraph.toposort()
        #for x in g:
        #    print x

    @property
    def learning_rate(self):
        return self.f_rate()[0]

    def validation_stagnant(self):
        self.f_finish()


class CG(Trainer):
    '''Conjugate gradient trainer for neural networks.'''

    def __init__(self, network, **kwargs):
        raise NotImplementedError


class HF(Trainer):
    '''The hessian free trainer shells out to an external implementation.

    hf.py was implemented by Nicholas Boulanger-Lewandowski and made available
    to the public (yay !). If you don't have a copy of the module handy, this
    class will attempt to download it from github.
    '''

    URL = 'https://raw.github.com/boulanni/theano-hf/master/hf.py'

    def __init__(self, network, **kwargs):
        import os, tempfile, urllib
        sys.path.append(tempfile.gettempdir())

        try:
            import hf
        except:
            # if hf failed to import, try downloading it and saving it locally.
            logging.error('hf import failed, attempting to download %s', HF.URL)
            path = os.path.join(tempfile.gettempdir(), 'hf.py')
            urllib.urlretrieve(HF.URL, path)
            logging.error('downloaded hf code to %s', path)
            import hf

        self.params = network.params(**kwargs)
        self.opt = hf.hf_optimizer(
            self.params,
            network.inputs,
            network.y,
            [network.J(**kwargs)] + network.monitors,
            network.hiddens[-1] if isinstance(network, recurrent.Network) else None)
        logging.info('HF: %d named parameters to learn', len(self.params))

        # fix mapping from kwargs into a dict to send to the hf optimizer
        kwargs['validation_frequency'] = kwargs.pop('validate', sys.maxint)
        for k in set(kwargs) - set(self.opt.train.im_func.func_code.co_varnames[1:]):
            kwargs.pop(k)
        self.kwargs = kwargs

    def train(self, train_set, valid_set=None, **kwargs):
        self.update_params(self.opt.train(
            train_set, kwargs['cg_set'], validation=valid_set, **self.kwargs))


class Cascaded(Trainer):
    '''This trainer allows running multiple trainers sequentially.'''

    def __init__(self, trainers):
        self.trainers = trainers

    def __call__(self, network, **kwargs):
        self.trainers = (t(network, **kwargs) for t in self.trainers)
        return self

    def train(self, train_set, valid_set=None, **kwargs):
        for trainer in self.trainers:
            trainer.train(train_set, valid_set=valid_set, **kwargs)


class Sample(Trainer):
    '''This trainer replaces network weights with samples from the input.'''

    @staticmethod
    def reservoir(xs, n):
        '''Select a random sample of n items from xs.'''
        pool = []
        for i, x in enumerate(xs):
            if len(pool) < n:
                pool.append(x / np.linalg.norm(x))
                continue
            j = rng.randint(i + 1)
            if j < n:
                pool[j] = x / np.linalg.norm(x)
        # if the pool still has fewer than n items, pad with distorted random
        # duplicates from the source data.
        L = len(pool)
        while len(pool) < n:
            x = pool[rng.randint(L)]
            pool.append(x + x.std() * 0.1 * rng.randn(*x.shape))
        return pool

    def __init__(self, network, **kwargs):
        self.network = network

    def train(self, train_set, valid_set=None, **kwargs):
        ifci = itertools.chain.from_iterable
        first = lambda x: x[0] if isinstance(x, (tuple, list)) else x
        samples = ifci(first(t) for t in train_set)
        for i, h in enumerate(self.network.hiddens):
            w = self.network.weights[i]
            m, k = w.get_value(borrow=True).shape
            logging.info('setting weights for %s: %d x %d', w.name, m, k)
            w.set_value(np.vstack(Sample.reservoir(samples, k)).T)
            samples = ifci(self.network.forward(first(t))[i-1] for t in train_set)


class Layerwise(Trainer):
    '''This trainer adapts parameters using greedy layerwise pretraining.'''

    def __init__(self, network, **kwargs):
        self.network = network
        self.kwargs = kwargs

    def train(self, train_set, valid_set=None, **kwargs):
        i = 0

        # construct training and validation datasets for autoencoding
        first = lambda x: x[0] if isinstance(x, (tuple, list)) else x
        bs = len(first(train_set.minibatches[0]))
        p = lambda z: np.vstack(first(x) for x in z.minibatches)
        _train = dataset.SequenceDataset(
            'train-0', p(train_set), size=bs, batches=train_set.limit)
        _valid = None
        if valid_set is not None:
            _valid = dataset.SequenceDataset(
                'valid-0', p(valid_set), size=bs, batches=valid_set.limit)

        while i < len(self.network.biases) - 1:
            weights = self.network.weights[i]
            bias = self.network.biases[i]
            n = weights.get_value(borrow=True).shape[0]
            k = bias.get_value(borrow=True).shape[0]

            logging.info('layerwise training: layer %d with %d hidden units', i + 1, k)

            # train a phantom autoencoder object on our dataset
            ae = feedforward.Autoencoder([n, k, n], TT.nnet.sigmoid)
            t = SGD(ae, **self.kwargs)
            t.train(_train, _valid)

            # copy the trained weights
            weights.set_value(ae.weights[0].get_value())
            bias.set_value(ae.biases[0].get_value())

            # map data through the network for the next layer
            i += 1
            p = lambda z: np.vstack(ae.forward(x[0])[0] for x in z.minibatches)
            _train = dataset.SequenceDataset(
                'train-%d' % i, p(_train), size=bs, batches=_train.limit)
            if _valid is not None:
                _valid = dataset.SequenceDataset(
                    'valid-%d' % i, p(_valid), size=bs, batches=_valid.limit)


class FORCE(Trainer):
    '''FORCE is a training method for recurrent nets by Sussillo & Abbott.'''

    def __init__(self, network, **kwargs):
        W_in, W_pool, W_out = network.weights

        n = W_pool.get_value(borrow=True).shape[0]
        self.alpha = kwargs.get('learning_rate', 1. / n)
        P = theano.shared(np.eye(n).astype(FLOAT) * self.alpha)

        k = TT.dot(P, network.state)
        rPr = TT.dot(network.state, k)
        c = 1. / (1. + rPr)
        dw = network.error(**kwargs) * c * k

        J = network.J(**kwargs)
        updates = {}
        updates[P] = P - c * TT.outer(k, k)
        updates[W_pool] = W_pool - dw
        updates[W_out] = W_out - dw
        updates[b_out] = b_out - self.alpha * TT.grad(J, b_out)

        costs = [J] + network.monitors
        self.f_eval = theano.function(network.inputs, costs)
        self.f_train = theano.function(network.inputs, costs, updates=updates)

    @property
    def learning_rate(self):
        return self.alpha
