import pandas as pd

# Imports for the dimensionality reduction
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import umap
import pacmap

import numpy as np

from abc import ABC, abstractmethod

class DimensionalityReduction(ABC):
    """
    Class that allows to reduce the dimensionality of the data.
    """
    def __init__(self):
        """
        Constructor of the class DimensionalityReduction.
        """
        pass

    @abstractmethod
    def compute(self):
        pass
        
class PCA_computation(DimensionalityReduction):
    def compute(self, X, n, default=True):
        # definition of the method PCA, used for the EE and the EV
        if default:
            pca = PCA(n_components=n)
        pca.fit(X)
        X_pca = pca.transform(X)
        X_pca = pd.DataFrame(X_pca)
        return X_pca
    
class TSNE_computation(DimensionalityReduction):

    def compute(self, X, n, default=True):
        # definition of the method TSNE, used for the EE and the EV
        if default:
            tsne = TSNE(n_components=n)
        X_tsne = tsne.fit_transform(X)
        X_tsne = pd.DataFrame(X_tsne)
        return X_tsne
    
class UMAP_computation(DimensionalityReduction):
    def compute(self, X, n, default=True):
        # definition of the method UMAP, used for the EE and the EV
        if default:
            reducer = umap.UMAP(n_components=n)
        embedding = reducer.fit_transform(X)
        embedding = pd.DataFrame(embedding)
        return embedding
    
class PaCMAP_computation(DimensionalityReduction):
    def compute(self, X, n, default, *args):
        # definition of the method PaCMAP, used for the EE and the EV
        # if default : no change of parameters (only for PaCMAP for now)
        if default:
            reducer = pacmap.PaCMAP(n_components=n, random_state=9)
        else:
            reducer = pacmap.PaCMAP(
                n_components=n,
                n_neighbors=args[0],
                MN_ratio=args[1],
                FP_ratio=args[2],
                random_state=9,
            )
        embedding = reducer.fit_transform(X, init="pca")
        embedding = pd.DataFrame(embedding)
        return embedding
    
def DimensionalityReductionChooser(method):
    if method == 'PCA':
        return PCA_computation()
    elif method == 't-SNE':
        return TSNE_computation()
    elif method == 'UMAP':
        return UMAP_computation()
    elif method == 'PaCMAP':
        return PaCMAP_computation()


def initialize_dim_red_EV(X, default_projection):
    dim_red = DimensionalityReductionChooser(method=default_projection)
    return dim_red.compute(X, 2, True), dim_red.compute(X, 3, True)

def initialize_dim_red_EE(EXP, default_projection):
    dim_red = DimensionalityReductionChooser(method=default_projection)
    return dim_red.compute(EXP, 2, True), dim_red.compute(EXP, 3, True)

def fonction_score(y, y_chap):
    # function that calculates the score of a machine-learning model
    y = np.array(y)
    y_chap = np.array(y_chap)
    return round(np.sqrt(sum((y - y_chap) ** 2) / len(y)), 3)

def update_figures(gui, exp, projEV, projEE):
    # fig1 : EV 2D, fig2 : EE 2D
    # fig1_3D : EV 3D, fig2_3D : EE 3D
    with gui.fig1.batch_update():
        gui.fig1.data[0].x, gui.fig1.data[0].y  = gui.dim_red['EV'][projEV][0][0], gui.dim_red['EV'][projEV][0][1]
    with gui.fig2.batch_update():
        gui.fig2.data[0].x, gui.fig2.data[0].y = gui.dim_red['EE'][exp][projEE][0][0], gui.dim_red['EE'][exp][projEE][0][1]
    with gui.fig1_3D.batch_update():
        gui.fig1_3D.data[0].x, gui.fig1_3D.data[0].y, gui.fig1_3D.data[0].z = gui.dim_red['EV'][projEV][1][0], gui.dim_red['EV'][projEV][1][1], gui.dim_red['EV'][projEV][1][2]
    with gui.fig2_3D.batch_update():
        gui.fig2_3D.data[0].x, gui.fig2_3D.data[0].y, gui.fig2_3D.data[0].z = gui.dim_red['EE'][exp][projEE][1][0], gui.dim_red['EE'][exp][projEE][1][1], gui.dim_red['EE'][exp][projEE][1][2]

def fonction_beeswarm_shap(gui, exp, nom_colonne):
    X = gui.atk.dataset.X
    Exp = gui.atk.explain[exp]
    y = gui.atk.dataset.y_pred
    
    # redefinition de la figure beeswarm de shap
    def positions_ordre_croissant(lst):
        positions = list(range(len(lst)))  # Create a list of initial positions
        positions.sort(key=lambda x: lst[x])
        l = []
        for i in range(len(positions)):
            l.append(positions.index(i))  # Sort positions by list items
        return l
    
    nom_colonne_shap = nom_colonne + "_shap"
    y_histo_shap = [0] * len(Exp)
    nombre_div = 60
    garde_indice = []
    garde_valeur_y = []
    for i in range(nombre_div):
        garde_indice.append([])
        garde_valeur_y.append([])
    liste_scale = np.linspace(
        min(Exp[nom_colonne_shap]), max(Exp[nom_colonne_shap]), nombre_div + 1
    )
    for i in range(len(Exp)):
        for j in range(nombre_div):
            if (
                Exp[nom_colonne_shap][i] >= liste_scale[j]
                and Exp[nom_colonne_shap][i] <= liste_scale[j + 1]
            ):
                garde_indice[j].append(i)
                garde_valeur_y[j].append(y[i])
                break
    for i in range(nombre_div):
        l = positions_ordre_croissant(garde_valeur_y[i])
        for j in range(len(garde_indice[i])):
            ii = garde_indice[i][j]
            if l[j] % 2 == 0:
                y_histo_shap[ii] = l[j]
            else:
                y_histo_shap[ii] = -l[j]
    marker_shap = dict(
        size=4,
        opacity=0.6,
        color=X[nom_colonne],
        colorscale="Bluered_r",
        colorbar=dict(thickness=20, title=nom_colonne),
    )
    return [y_histo_shap, marker_shap]