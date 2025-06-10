library(mgcv)
library(ggeffects)
library(ggplot2)

df <- read.csv("stats/table_params.csv", sep="\t")

df$expert <- as.factor(df$expert)
df$data <- as.factor(df$data)
df$phase <- as.factor(df$phase)
df$transcriber <- as.factor(df$transcriber)  # your random effect

model <- gam(intonation_patterns ~
			   s(minute, k=3) +                  # smooth term for time
               expert +                      # fixed effect
               data +                        # fixed effect
               phase +                       # fixed effect
               s(transcriber, bs = "re"),    # random intercept per transcriber
             data = df, method = "REML")

# View the model summary
summary(model)

png("tus_my_gam_plots.png", width = 800, height = 600) # Adjust width/height as needed

# Generate the plots (e.g., all on one page if your model has multiple smooths)
plot(model, pages = 1)

# Close the device (this saves the file)
dev.off()

# Open a PNG device
png("tus_gam_check_diagnostics.png", width = 1000, height = 800) # Adjust dimensions

# Generate the diagnostic plots
gam.check(model)

# Close the device
dev.off()



# Predict from the GAMM
pred <- predict(model, se.fit = TRUE)

# Store values
df$fit <- pred$fit
df$lower <- pred$fit - 1.96 * pred$se.fit
df$upper <- pred$fit + 1.96 * pred$se.fit

# Plot
ggplot(df, aes(x = fit, y = intonation_patterns, color=data, shape=phase)) +
  geom_errorbar(aes(ymin = lower, ymax = upper), width = 0, alpha = 0.4) +
  geom_point(alpha = 0.6) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
  labs(
    title = "Predicted vs Observed with 95% CI",
    x = "Predicted WER",
    y = "Observed WER"
  ) +
  theme_minimal(base_size = 14)

ggsave("plots/tus_predicted_vs_observed.png", width = 7, height = 6, dpi = 300)


eff_expert <- ggemmeans(model, terms = "expert")

p_expert <- ggplot(eff_expert, aes(x = x, y = predicted)) +
  geom_point(size = 4, color = "#0072B2") +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.2, color = "#0072B2") +
  geom_line(aes(group = 1), color = "#0072B2", linewidth = 1) +
  labs(
    title = "Effect of Expertise",
    x = "Expertise",
    y = "Predicted WER Gain"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    axis.title = element_text(size = 14),
    axis.text = element_text(size = 12)
  )

eff_data <- ggemmeans(model, terms = "data")

p_data <- ggplot(eff_data, aes(x = x, y = predicted)) +
  geom_point() +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.1) +
  labs(title = "Effect of Data Type", x = "Data", y = "Predicted Value") +
  theme_minimal()

  eff_phase <- ggemmeans(model, terms = "phase")

p_phase <- ggplot(eff_phase, aes(x = x, y = predicted)) +
  geom_point() +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), width = 0.1) +
  labs(title = "Effect of Phase", x = "Phase", y = "Predicted Value") +
  theme_minimal()

  library(patchwork)
(p_expert | p_data | p_phase)

# Save
ggsave("plots/tus_effects_categorical.png", width = 12, height = 4, dpi = 300)

