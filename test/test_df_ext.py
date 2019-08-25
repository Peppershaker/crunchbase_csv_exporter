import os

import numpy as np
import pandas as pd

from ..cbexporter import Df_ext


def test_Df_ext_with_list():
    data = Df_ext([
        ["Facebook", "1 Hacker Way", "100B", np.nan, None],
        ["Facebook", np.nan, np.nan, "1.4B", '2003'],
        ["Facebook", np.nan, np.nan, "2.4B", np.nan],
        ["Youtube", "901 Cherry Ave", "13B", np.nan, np.nan],
        ["Youtube", np.nan, np.nan, "1.2B", "2001"]])

    data = data.combine_row()

    ground_truth = Df_ext([
        ["Facebook", "1 Hacker Way", "100B", "1.4B", '2003'],
        ["Youtube", "901 Cherry Ave", "13B", "1.2B", "2001"]])

    assert np.array_equal(data.values, ground_truth.values) == True


def test_Df_ext_with_csv():
    test_root_dir = os.path.dirname(os.path.abspath(__file__))
    test_data_path = os.path.join(test_root_dir, 'test_data/df_ext.csv')
    
    data = Df_ext(pd.read_csv(test_data_path)).combine_row()

    # cast Value3 column to ints, can't speify dtype in read_csv because volumn has np.nan
    data.Value3 = data.Value3.astype(float).astype(int)

    test_truth_data_path = os.path.join(test_root_dir, 'test_data/df_ext_ground_truth.csv')
    ground_truth = Df_ext(pd.read_csv(test_truth_data_path))

    assert np.array_equal(data.values[1,:], ground_truth.values[1,:]) == True
