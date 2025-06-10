from pygam import LinearGAM, s, f, te
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("stats/table_mixed2.csv", sep="\t")

print(df['data'].astype('category').cat.categories)

# Convert categorical variables
df['expert'] = df['expert'].astype('category').cat.codes
df['data'] = df['data'].astype('category').cat.codes
df['phase'] = df['phase'].astype('category').cat.codes

# Define features and target
X = df[['minutes', 'expert', 'data', 'phase']].values
y = df['transcribed_delta'].values

# s(0): spline for minutes (column 0)
# f(1), f(2), f(3): factors for expert, data, phase
gam = LinearGAM(s(0) + f(1) + f(2) + f(3)).fit(X, y)

gam.summary()


XX = gam.generate_X_grid(term=0)
pdep, confi = gam.partial_dependence(term=0, X=XX, width=0.95)

plt.plot(XX[:, 0], pdep, label='Effect of Time (minutes)')
plt.fill_between(XX[:, 0], confi[:, 0], confi[:, 1], alpha=0.3, label='95% CI')
plt.xlabel('Minutes')
plt.ylabel('Partial effect on transcribed_delta')
plt.title('GAM: Effect of Time on Transcription')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/gam.png")
plt.clf()


y_pred = gam.predict(X)
ci = gam.confidence_intervals(X)

plt.errorbar(y_pred, y, yerr=[y_pred - ci[:, 0], ci[:, 1] - y_pred], fmt='o', alpha=0.4)
plt.plot([min(y), max(y)], [min(y), max(y)], 'k--', label='Perfect prediction')
plt.xlabel("Predicted")
plt.ylabel("Observed")
plt.title("Predicted vs Observed with 95% CI")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/predicted.png")
plt.clf()

fig, axs = plt.subplots(1, 4, figsize=(16, 4))
titles = ["minutes", "expert", "data", "phase"]

label_maps = {
    1: {0: "no", 1: "sì"},  # expert
    2: {0: "parlabo", 1: "pasti", 2: "straparla"},  # data
    3: {0: "1", 1: "2"},  # phase
}

for i, ax in enumerate(axs):
    XX = gam.generate_X_grid(term=i)
    pdep, confi = gam.partial_dependence(term=i, X=XX, width=0.95)
    ax.plot(XX[:, i], pdep)
    ax.fill_between(XX[:, i], confi[:, 0], confi[:, 1], alpha=0.3)
    ax.set_title(f"Effect of {titles[i]}")
    ax.set_xlabel(titles[i])
    ax.set_ylabel("partial effect")

    # Add custom tick labels for categorical terms
    if i in label_maps:
        ticks = sorted(label_maps[i].keys())
        labels = [label_maps[i][t] for t in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)

plt.tight_layout()
plt.savefig("plots/effects.png")
plt.clf()


# s(0): spline for minutes (column 0)
# f(1), f(2), f(3): factors for expert, data, phase
gam2 = LinearGAM(s(0) +
                f(1) + f(2) + f(3) +
                te(1,3)).fit(X, y)

gam2.summary()

XX = gam.generate_X_grid(term=0)
pdep, confi = gam2.partial_dependence(term=0, X=XX, width=0.95)

plt.plot(XX[:, 0], pdep, label='Effect of Time (minutes)')
plt.fill_between(XX[:, 0], confi[:, 0], confi[:, 1], alpha=0.3, label='95% CI')
plt.xlabel('Minutes')
plt.ylabel('Partial effect on transcribed_delta')
plt.title('GAM: Effect of Time on Transcription')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/gam2.png")
plt.clf()


y_pred = gam2.predict(X)
ci = gam2.confidence_intervals(X)

plt.errorbar(y_pred, y, yerr=[y_pred - ci[:, 0], ci[:, 1] - y_pred], fmt='o', alpha=0.4)
plt.plot([min(y), max(y)], [min(y), max(y)], 'k--', label='Perfect prediction')
plt.xlabel("Predicted")
plt.ylabel("Observed")
plt.title("Predicted vs Observed with 95% CI")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/predicted2.png")
plt.clf()

fig, axs = plt.subplots(1, 4, figsize=(16, 4))
titles = ["minutes", "expert", "data", "phase"]

label_maps = {
    1: {0: "no", 1: "sì"},  # expert
    2: {0: "parlabo", 1: "pasti", 2: "straparla"},  # data
    3: {0: "1", 1: "2"},  # phase
}

for i, ax in enumerate(axs):
    XX = gam2.generate_X_grid(term=i)
    pdep, confi = gam2.partial_dependence(term=i, X=XX, width=0.95)
    ax.plot(XX[:, i], pdep)
    ax.fill_between(XX[:, i], confi[:, 0], confi[:, 1], alpha=0.3)
    ax.set_title(f"Effect of {titles[i]}")
    ax.set_xlabel(titles[i])
    ax.set_ylabel("partial effect")

    # Add custom tick labels for categorical terms
    if i in label_maps:
        ticks = sorted(label_maps[i].keys())
        labels = [label_maps[i][t] for t in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)

plt.tight_layout()
plt.savefig("plots/effects2.png")
plt.clf()


print("Model 1 AIC:", gam.statistics_["AIC"])
print("Model 1 R²:", gam.statistics_['pseudo_r2'])

print("Model 2 AIC:", gam2.statistics_["AIC"])
print("Model 2 R²:", gam2.statistics_['pseudo_r2'])

df = pd.read_csv("stats/table_wer.csv", sep="\t")

# Convert categorical variables
df['expert'] = df['expert'].astype('category').cat.codes
df['data'] = df['data'].astype('category').cat.codes
df['phase'] = df['phase'].astype('category').cat.codes

# Define features and target
X = df[['expert', 'data', 'phase']].values
y = df['wer'].values

# s(0): spline for minutes (column 0)
# f(1), f(2), f(3): factors for expert, data, phase
gam = LinearGAM(f(0) + f(1) + f(2)).fit(X, y)
gam.summary()


y_pred = gam.predict(X)
ci = gam.confidence_intervals(X)

plt.errorbar(y_pred, y, yerr=[y_pred - ci[:, 0], ci[:, 1] - y_pred], fmt='o', alpha=0.4)
plt.plot([min(y), max(y)], [min(y), max(y)], 'k--', label='Perfect prediction')
plt.xlabel("Predicted")
plt.ylabel("Observed")
plt.title("Predicted vs Observed with 95% CI")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/predicted_wer.png")
plt.clf()

fig, axs = plt.subplots(1, 3, figsize=(12, 4))
titles = ["expert", "data", "phase"]

label_maps = {
    1: {0: "no", 1: "sì"},  # expert
    2: {0: "parlabo", 1: "pasti", 2: "straparla"},  # data
    3: {0: "1", 1: "2"},  # phase
}

for i, ax in enumerate(axs):
    XX = gam.generate_X_grid(term=i)
    pdep, confi = gam.partial_dependence(term=i, X=XX, width=0.95)
    ax.plot(XX[:, i], pdep)
    ax.fill_between(XX[:, i], confi[:, 0], confi[:, 1], alpha=0.3)
    ax.set_title(f"Effect of {titles[i]}")
    ax.set_xlabel(titles[i])
    ax.set_ylabel("partial effect")

    # Add custom tick labels for categorical terms
    if i in label_maps:
        ticks = sorted(label_maps[i].keys())
        labels = [label_maps[i][t] for t in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)

plt.tight_layout()
plt.savefig("plots/effects_wer.png")
plt.clf()