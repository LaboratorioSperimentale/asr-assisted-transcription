import pandas as pd
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.pyplot as plt
from pygam import LinearGAM, s, f  # s = spline term, f = factor (categorical)



# df = pd.read_csv("table_tus.csv", sep="\t")
df = pd.read_csv("table_mixed.csv", sep="\t")

df['Esperto'] = df['Esperto'].astype('category').cat.codes
df['Phase'] = df['Phase'].astype('category').cat.codes
df['tipo'] = df['tipo'].astype('category').cat.codes
df['Annotatore'] = df['Annotatore'].astype('category').cat.codes



# Assume df is your DataFrame in long format
# model = smf.mixedlm(
#     "value ~ Esperto * Phase * tipo * min ",
#     df,
#     groups=df["Annotatore"]
# )

# result = model.fit()
# print(result.summary())

# Assume df is your DataFrame in long format
model = smf.mixedlm(
    "delta ~ Esperto * Phase * tipo ",
    df,
    groups=df["Annotatore"]
)

# model = smf.mixedlm(
#     "value ~ Esperto * Phase * tipo",
#     df,
#     groups=df["Annotatore"],  # main grouping
#     re_formula="~min"         # random slope for min
# )

result = model.fit()
print(result.summary())


sns.color_palette("hls", 8)
# sns.lineplot(data=df, x='min', y='value', hue='Esperto', style='tipo')
# plt.title('Transcription over time by expertise and data type')
# plt.savefig("plot_mixed_type.png")

sns.lineplot(data=df, x='min', y='value', hue='Esperto', style='Phase')
plt.title('Transcription over time by expertise and experimental phase')
plt.savefig("plot_mixed_phase.png")

# sns.lineplot(data=df, x='min', y='value', hue='Phase', style='tipo')
# plt.title('Transcription over time by expertise and experimental phase')
# plt.savefig("plot_mixed_tipo_fase.png")