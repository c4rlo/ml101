#!/usr/bin/python3
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split

### Assignment Owner: Tian Wang

#######################################
#### Normalization


def feature_normalization(train, test):
    """Rescale the data so that each feature in the training set is in
    the interval [0,1], and apply the same transformations to the test
    set, using the statistics computed on the training set.

    Args:
        train - training set, a 2D numpy array of size (num_instances, num_features)
        test  - test set, a 2D numpy array of size (num_instances, num_features)
    Returns:
        train_normalized - training set after normalization
        test_normalized  - test set after normalization

    """
    train_min = np.minimum.reduce(train, axis=0)
    train_max = np.maximum.reduce(train, axis=0)
    breadth = train_max - train_min
    train_normalized = (train - train_min) / breadth
    test_normalized = (test - train_min) / breadth
    # TODO discard constant-valued features (though none exist in the training
    # set)

    return train_normalized, test_normalized


########################################
#### The square loss function

def compute_square_loss(X, y, theta):
    """
    Given a set of X, y, theta, compute the square loss for predicting y with X*theta

    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        theta - the parameter vector, 1D array of size (num_features)

    Returns:
        loss - the square loss, scalar
    """

    return ((X @ theta - y)**2).sum() / len(y)



########################################
### compute the gradient of square loss function
def compute_square_loss_gradient(X, y, theta):
    """
    Compute gradient of the square loss (as defined in compute_square_loss), at the point theta.

    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        theta - the parameter vector, 1D numpy array of size (num_features)

    Returns:
        grad - gradient vector, 1D numpy array of size (num_features)
    """

    return 2/len(y) * (X.T @ (X @ theta - y))



###########################################
### Gradient Checker
#Getting the gradient calculation correct is often the trickiest part
#of any gradient-based optimization algorithm.  Fortunately, it's very
#easy to check that the gradient calculation is correct using the
#definition of gradient.
#See http://ufldl.stanford.edu/wiki/index.php/Gradient_checking_and_advanced_optimization
def grad_checker(X, y, theta, epsilon=1e-4, tolerance=1e-2):
    """Implement Gradient Checker
    Check that the function compute_square_loss_gradient returns the
    correct gradient for the given X, y, and theta.

    Let d be the number of features. Here we numerically estimate the
    gradient by approximating the directional derivative in each of
    the d coordinate directions:
    (e_1 = (1,0,0,...,0), e_2 = (0,1,0,...,0), ..., e_d = (0,...,0,1)

    The approximation for the directional derivative of J at the point
    theta in the direction e_i is given by:
    ( J(theta + epsilon * e_i) - J(theta - epsilon * e_i) ) / (2*epsilon).

    We then look at the Euclidean distance between the gradient
    computed using this approximation and the gradient computed by
    compute_square_loss_gradient(X, y, theta).  If the Euclidean
    distance exceeds tolerance, we say the gradient is incorrect.

    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        theta - the parameter vector, 1D numpy array of size (num_features)
        epsilon - the epsilon used in approximation
        tolerance - the tolerance error

    Return:
        A boolean value indicate whether the gradient is correct or not

    """
    true_gradient = compute_square_loss_gradient(X, y, theta) #the true gradient
    num_features = len(theta)
    err = 0
    for i in range(num_features):
        j1 = compute_square_loss(X, y, perturb(theta, i, epsilon))
        j2 = compute_square_loss(X, y, perturb(theta, i, -epsilon))
        approx_deriv = (j1 - j2) / (2*epsilon)
        err += (approx_deriv - true_gradient[i]) ** 2

    if err >= tolerance**2:
        print("err = {}, norm(grad) = {}".format(err,
            np.linalg.norm(true_gradient)))
        return False
    return True

def perturb(a, i, eps):
    r = np.copy(a)
    r[i] += eps
    return r

#################################################
### Generic Gradient Checker
def generic_gradient_checker(X, y, theta, objective_func, gradient_func, epsilon=0.01, tolerance=1e-4):
    """
    The functions takes objective_func and gradient_func as parameters. And check whether gradient_func(X, y, theta) returned
    the true gradient for objective_func(X, y, theta).
    Eg: In LSR, the objective_func = compute_square_loss, and gradient_func = compute_square_loss_gradient
    """
    #TODO


####################################
#### Batch Gradient Descent
def batch_grad_descent(X, y, alpha=0.1, num_iter=1000, check_gradient=False):
    """
    In this question you will implement batch gradient descent to
    minimize the square loss objective

    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        alpha - step size in gradient descent
        num_iter - number of iterations to run
        check_gradient - a boolean value indicating whether checking the gradient when updating

    Returns:
        theta_hist - store the the history of parameter vector in iteration, 2D numpy array of size (num_iter+1, num_features)
                    for instance, theta in iteration 0 should be theta_hist[0], theta in ieration (num_iter) is theta_hist[-1]
        loss_hist - the history of objective function vector, 1D numpy array of size (num_iter+1)
    """
    num_instances, num_features = X.shape[0], X.shape[1]
    theta_hist = np.zeros((num_iter, num_features))  #Initialize theta_hist
    loss_hist = np.zeros(num_iter) #initialize loss_hist
    theta = np.zeros(num_features) #initialize theta

    for i in range(num_iter):
        if check_gradient:
            if not grad_checker(X, y, theta):
                print("Gradient calculation is broken!")
                sys.exit(1)
        grad = compute_square_loss_gradient(X, y, theta)
        theta -= alpha * grad
        theta_hist[i] = theta
        loss_hist[i] = compute_square_loss(X, y, theta)

    return theta_hist, loss_hist

####################################
###Q2.4b: Implement backtracking line search in batch_gradient_descent
###Check http://en.wikipedia.org/wiki/Backtracking_line_search for details
#TODO


def compute_regularized_square_loss(X, y, theta, lambda_reg):
    return ((X@theta - y)**2).sum() / len(y) + lambda_reg*(theta**2).sum()

###################################################
### Compute the gradient of Regularized Batch Gradient Descent
def compute_regularized_square_loss_gradient(X, y, theta, lambda_reg):
    """
    Compute the gradient of L2-regularized square loss function given X, y and theta

    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        theta - the parameter vector, 1D numpy array of size (num_features)
        lambda_reg - the regularization coefficient

    Returns:
        grad - gradient vector, 1D numpy array of size (num_features)
    """

    return 2*( X.T @ (X@theta - y) / len(y) + lambda_reg*theta )

###################################################
### Batch Gradient Descent with regularization term
def regularized_grad_descent(X, y, alpha=0.1, lambda_reg=1, num_iter=1000):
    """
    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        alpha - step size in gradient descent
        lambda_reg - the regularization coefficient
        num_iter - number of iterations to run

    Returns:
        theta_hist - the history of parameter vector, 2D numpy array of size (num_iter+1, num_features)
        loss_hist - the history of loss function without the regularization term, 1D numpy array.
    """
    (num_instances, num_features) = X.shape
    theta = np.zeros(num_features) #Initialize theta
    theta_hist = np.zeros((num_iter, num_features))  #Initialize theta_hist
    loss_hist = np.zeros(num_iter) #Initialize loss_hist

    for i in range(num_iter):
        grad = compute_regularized_square_loss_gradient(X, y, theta, lambda_reg)
        theta -= alpha * grad
        theta_hist[i] = theta
        loss_hist[i] = compute_square_loss(X, y, theta)

    return theta_hist, loss_hist

#############################################
## Visualization of Regularized Batch Gradient Descent
##X-axis: log(lambda_reg)
##Y-axis: square_loss

#############################################
### Stochastic Gradient Descent
def stochastic_grad_descent(X, y, alpha=0.1, lambda_reg=1, eta0=None, t0=1, num_iter=1000):
    """
    In this question you will implement stochastic gradient descent with a regularization term

    Args:
        X - the feature vector, 2D numpy array of size (num_instances, num_features)
        y - the label vector, 1D numpy array of size (num_instances)
        alpha - string or float. step size in gradient descent
                NOTE: In SGD, it's not always a good idea to use a fixed step size. Usually it's set to 1/sqrt(t) or 1/t
                if alpha is a float, then the step size in every iteration is alpha.
                if alpha == "1/sqrt(t)", alpha = 1/sqrt(t)
                if alpha == "1/t", alpha = 1/t
        lambda_reg - the regularization coefficient
        num_iter - number of epochs (i.e number of times) to go through the whole training set

    Returns:
        theta_hist - the history of parameter vector, 3D numpy array of size (num_iter, num_instances, num_features)
        loss hist - the history of regularized loss function vector, 2D numpy array of size(num_iter, num_instances)
    """
    num_instances, num_features = X.shape[0], X.shape[1]
    theta = np.ones(num_features) #Initialize theta

    theta_hist = np.zeros((num_iter, num_instances, num_features))  #Initialize theta_hist
    loss_hist = np.zeros((num_iter, num_instances)) #Initialize loss_hist

    t = t0
    for epoch in range(num_iter):
        for i in range(num_instances):
            grad = compute_sgd_gradient(X[i], y[i], theta, lambda_reg)
            if alpha == "1/t":
                a = 1/t
            elif alpha == "1/sqrt(t)":
                a = 1/np.sqrt(t)
            elif alpha == "special":
                a = eta0 / (1 + eta0*lambda_reg*t)
            else:
                a = alpha
            theta -= a * grad
            theta_hist[epoch, i] = theta
            loss_hist[epoch, i] = compute_regularized_square_loss(X, y, theta,
                    lambda_reg)
            t += 1

    return theta_hist, loss_hist

def compute_sgd_gradient(xi, yi, theta, lambda_reg):
    return 2*( (theta.T @ xi - yi)*xi + lambda_reg*theta )

def compute_sgd_loss(xi, yi, theta, lambda_reg):
    return ((theta.T @ xi - yi)**2).sum() + lambda_reg*(theta**2).sum()

################################################
### Visualization that compares the convergence speed of batch
###and stochastic gradient descent for various approaches to step_size
##X-axis: Step number (for gradient descent) or Epoch (for SGD)
##Y-axis: log(objective_function_value) and/or objective_function_value

def main():
    try:
        mode = sys.argv[1]
    except IndexError:
        print("usage: {} MODE".format(sys.argv[0]))
        sys.exit(2)

    #Loading the dataset
    print('loading the dataset')

    df = pd.read_csv('data.csv', delimiter=',')
    X = df.values[:,:-1]
    y = df.values[:,-1]

    print('Split into Train and Test')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size =100, random_state=10)

    print("Scaling all to [0, 1]")
    X_train, X_test = feature_normalization(X_train, X_test)
    X_train = np.hstack((X_train, np.ones((X_train.shape[0], 1))))  # Add bias term
    X_test = np.hstack((X_test, np.ones((X_test.shape[0], 1)))) # Add bias term
    X_full = np.vstack((X_train, X_test))
    y_full = y

    print("Doing some machine learning (mode={})!".format(mode))

    def search_range(start, stop, num):
        step = (stop - start) / num
        a = start
        for _ in range(num):
            yield a
            a += step

    if mode == 'reg_gd_lambda':

        lambdas = []
        train_losses = []
        test_losses = []

        for lambda_reg in search_range(0, .1, 50):
            theta_hist, loss_hist = regularized_grad_descent(X_train, y_train,
                    alpha=0.05, lambda_reg=lambda_reg)
            theta = theta_hist[-1]
            train_loss = loss_hist[-1]
            test_loss = compute_square_loss(X_test, y_test, theta)
            print("For λ={}: loss = {} (train) / {} (test)".format(lambda_reg,
                train_loss, test_loss))
            lambdas.append(lambda_reg)
            train_losses.append(train_loss)
            test_losses.append(test_loss)

        plt.plot(lambdas, train_losses, 'r--', lambdas, test_losses, 'b--')
        plt.xlabel("λ")
        plt.ylabel("Square loss (non-regularized)")
        plt.legend(["training loss", "test loss"])
        plt.savefig('fig1.svg')

    elif mode == 'reg_gd':

        theta_hist, loss_hist = regularized_grad_descent(X_train, y_train,
                alpha=0.05, lambda_reg=0.023848)
        theta = theta_hist[-1]
        test_loss = compute_square_loss(X_test, y_test, theta)
        print("θ =", theta)
        print("test loss =", test_loss)

    elif mode == 'reg_gd_full':

        theta_hist, loss_hist = regularized_grad_descent(X_full, y_full,
                alpha=0.05, lambda_reg=0.023848)
        theta = theta_hist[-1]
        print("θ =", theta)
        print("loss =", loss_hist[-1])

    elif mode == 'reg_sgd':

        for i, a in enumerate((0.0005, 0.001, 0.002, 0.003, "1/t", "1/sqrt(t)")):
            theta_hist, loss_hist = stochastic_grad_descent(X_train, y_train,
                    alpha=a, lambda_reg=0.023848, t0=300)
            losses = loss_hist[:, -1]
            plt.clf()
            plt.semilogy(losses, 'r--')
            plt.title("η={}, final loss is {}".format(a, losses[-1]))
            plt.xlabel("Epoch")
            plt.ylabel("Objective function (regularized square loss)")
            plt.savefig("fig2-{}.svg".format(i))
            theta = theta_hist[-1, -1]
            objective = losses[-1]
            test_loss = compute_square_loss(X_test, y_test, theta)
            print("For η={}, objective is {}, test loss is {}".format(a,
                objective, test_loss))

    elif mode == 'reg_sgd_adaptive':

        # for eta0 in 0.01, 0.02, 0.03, 0.035, 0.04, 0.045, 0.05:
        for eta0 in 0.035, 0.045:
            theta_hist, loss_hist = stochastic_grad_descent(X_train, y_train,
                    alpha="special", eta0=eta0, lambda_reg=0.023848)
            objective = loss_hist[-1, -1]
            theta = theta_hist[-1, -1]
            test_loss = compute_square_loss(X_test, y_test, theta)
            print("For eta0={}, objective is {}, test loss is {}".format(eta0,
                objective, test_loss))

    else:
        print("Unknown mode")
        sys.exit(2)


main()
