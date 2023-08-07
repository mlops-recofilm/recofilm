import pytest
from pathlib import Path
import pickle

def get_stability_dict():
    base_dir = Path(__file__).resolve().parent  # Pointe vers le dossier \kpi_movie_model
    file_path = base_dir /"kpi_movie_model"/ "dict_stability.pkl"

    with open(file_path, 'rb') as f:
        return pickle.load(f)

def get_pred_comparaison_dict():
    base_dir = Path(__file__).resolve().parent  # Pointe vers le dossier \kpi_movie_model
    file_path = base_dir /"kpi_movie_model"/ "dict_prediction_comparaison.pkl"

    with open(file_path, 'rb') as f:
        return pickle.load(f)

def test_movie_score_stability():
    stability_dict = get_stability_dict()
    
    # Vérifiez qu'au moins un film a un score associé supérieur à 0.8
    assert any(score > 0.8 for score in stability_dict.values()), "Aucun film n'a un score supérieur à 0.8"

def test_movie_score_prediction_comparaison():
    pred_compar_dict = get_pred_comparaison_dict()
    
    # Vérifiez qu'au moins un film a un score associé supérieur à 0.8
    assert any(score < 1 for score in pred_compar_dict.values())
