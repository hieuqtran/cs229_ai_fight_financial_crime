from util.config import *
import tensorflow as tf
from prediction.predictor import *

log = logging.getLogger(__name__)

class FCNNPredictor(Predictor):

    """
    Class implementing the Predictor interface for NN only with fully connected layers
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.batch_size = kwargs.pop('batch_size')

    def load_model(self):

        """
        Loads the model from a file
        :return:
        """
        self.model = tf.keras.models.load_model(self.weights_file)


    def transform_data(self):

        """
        Transforms the data to the shapes required by Keras/TensorFlow 2.0 NN
        :return: transformed features and labels
        """

        n_examples = np.shape(self.x)[0]
        n_features = np.shape(self.x)[1]

        # we are doing classification
        n_outputs = 1

        # reshape the arrays to match the input expected by Keras
        self.x = self.x.reshape(n_examples, 1, n_features)
        self.y = self.y.reshape(n_examples, 1, n_outputs)

        return self.x, self.y


    def predict(self):

        """
        Performs prediction

        :return: predicted labels
        """

        x_trans, y_trans = self.transform_data()

        self.y_pred = (self.model.predict(x_trans, batch_size=self.batch_size) >= 0.5).astype(int).reshape(-1, 1)

        return self.y_pred

    def explain(self):
        """
        Explain the output based on the inputs using Sensitivity Analysis

        :return: the derivative of the output w.r.t to the input, i.e. dy/dx
        """

        x = tf.Variable(self.x, dtype=float)

        with tf.GradientTape(persistent=True) as t:
            y_pred = self.model(x)

        dy_dx = t.gradient(y_pred, x).numpy() ** 2

        del t

        # Multiply each feature by "how important it is"
        self.x *= dy_dx

        return dy_dx
