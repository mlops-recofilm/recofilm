import pytest
from pathlib import Path
import pickle
import os
import sys
sys.path.append('..')
from utils.path import user_model_unittest_folder

def get_stability_dict():
    file_path = os.path.join(user_model_unittest_folder, "dict_stability.pkl")

    with open(file_path, 'rb') as f:
        return pickle.load(f)

def get_pred_comparaison_dict():
    file_path = os.path.join(user_model_unittest_folder, "dict_prediction_comparaison.pkl")

    with open(file_path, 'rb') as f:
        return pickle.load(f)

def test_user_score_stability():
    stability_dict = get_stability_dict()
    
    # Vérifiez qu'au moins un film a un score associé supérieur à 0.8 (score à confirmer)
    assert any(score > 0.8 for score in stability_dict.values()), "Aucun film n'a un score supérieur à 0.8"

def test_user_score_prediction_comparaison():
    pred_compar_dict = get_pred_comparaison_dict()
    
    # Vérifiez qu'au moins un film a un score a un score inférieur à 1 (score à confirmer)
    assert any(score < 1 for score in pred_compar_dict.values())
