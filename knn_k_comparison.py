import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.datasets import make_moons
from sklearn.neighbors import KNeighborsClassifier

# 1. Dataset with a complex pattern and some noise
X, y = make_moons(n_samples=200, noise=0.3, random_state=42)

# K values to compare
k_values = [1, 15]

# The strategic "new point" that CHANGES class depending on k.
# NOTE: (0.5, 0.4) does NOT flip -- it is class 1 for both k=1 and k=15.
# (0.62, -0.35) sits inside a noisy pocket: k=1 takes the noise seriously (red),
# while k=15 ignores it and follows the real trend (green).
new_point = np.array([[0.62, -0.35]])

# --- Sanity check: does the point actually flip? -----------------------------
preds = {k: KNeighborsClassifier(n_neighbors=k).fit(X, y).predict(new_point)[0]
         for k in k_values}
print("Predicted class for the new point:", preds)
if len(set(preds.values())) == 1:
    print("WARNING: the point does NOT change class -- the slide loses its point!")
    print("         Pick another point (or run find_flipping_points() below).")
else:
    print("OK: the point changes class between the two k values.\n")
# -----------------------------------------------------------------------------

# 2. Plot colors
cmap_background = ListedColormap(['#FFAAAA', '#AAFFAA'])  # light red / light green (regions)
cmap_points = ListedColormap(['#D62728', '#2CA02C'])      # strong red / strong green (data)

# Mesh grid used to draw the decision boundary
h = 0.02
x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

titles = ["k=1  (Local decision / sensitive to noise)",
          "k=15  (Democratic decision / follows the trend)"]

plt.figure(figsize=(14, 6))

for i, k in enumerate(k_values):
    # Train the KNN model
    clf = KNeighborsClassifier(n_neighbors=k)
    clf.fit(X, y)

    # Predict over the whole mesh (paints the background)
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Prediction for the new point specifically
    new_pred = clf.predict(new_point)[0]
    new_point_color = '#D62728' if new_pred == 0 else '#2CA02C'
    class_name = 'RED' if new_pred == 0 else 'GREEN'

    # Plot
    plt.subplot(1, 2, i + 1)
    plt.contourf(xx, yy, Z, cmap=cmap_background, alpha=0.6)
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_points,
                edgecolor='k', s=30, alpha=0.8)

    # Highlight the new point with a giant star
    plt.scatter(new_point[:, 0], new_point[:, 1], c=new_point_color, marker='*',
                s=800, edgecolor='black', linewidth=2, zorder=5,
                label=f'New point -> classified {class_name}')

    plt.title(titles[i], fontsize=16, fontweight='bold', pad=15)
    plt.legend(loc='lower right', fontsize=12)
    plt.xticks(())
    plt.yticks(())

plt.suptitle("The SAME point, two values of k -> TWO different answers",
             fontsize=18, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('knn_comparacao_k1_k15.png', dpi=300, bbox_inches='tight')
plt.savefig('knn_comparacao_k1_k15.svg', format='svg', bbox_inches='tight')
print("Charts saved as .png and .svg successfully!")


# --- Helper: find points that flip class between the two k values -------------
def find_flipping_points(X, y, k_low=1, k_high=15, top=5):
    """Scan the grid and return points that change class between k_low and k_high,
    preferring dense regions (where the demo is most convincing)."""
    from scipy.spatial import cKDTree

    clf_low = KNeighborsClassifier(n_neighbors=k_low).fit(X, y)
    clf_high = KNeighborsClassifier(n_neighbors=k_high).fit(X, y)

    xs = np.arange(X[:, 0].min(), X[:, 0].max(), 0.05)
    ys = np.arange(X[:, 1].min(), X[:, 1].max(), 0.05)
    grid = np.array([[a, b] for a in xs for b in ys])

    flips = grid[clf_low.predict(grid) != clf_high.predict(grid)]
    if len(flips) == 0:
        return []

    # prefer dense areas: small distance to the k_high-th neighbor
    dist, _ = cKDTree(X).query(flips, k=k_high)
    order = np.argsort(dist[:, -1])
    return [tuple(np.round(flips[i], 2)) for i in order[:top]]


if __name__ == "__main__":
    print("\nOther good candidate points:", find_flipping_points(X, y))
