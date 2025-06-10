library(mgcv)
library(ggeffects)
library(ggplot2)
library(patchwork)

df <- read.csv("stats/table_mixed2.csv", sep="\t")

df$expert <- as.factor(df$expert)
df$data <- as.factor(df$data)
df$phase <- as.factor(df$phase)
df$transcriber <- as.factor(df$transcriber)  # your random effect

model <- gam(transcribed_delta ~
               s(minutes, k=3) +                  # smooth term for time
               expert +                      # fixed effect
               data +                        # fixed effect
               phase +                       # fixed effect
               s(transcriber, bs = "re"),    # random intercept per transcriber
             data = df, method = "REML", family = gaussian())

# View the model summary
summary(model)

png("my_gam_plots.png", width = 800, height = 600) # Adjust width/height as needed

# Generate the plots (e.g., all on one page if your model has multiple smooths)
plot(model, pages = 1)

# Close the device (this saves the file)
dev.off()

# Open a PNG device
png("gam_check_diagnostics.png", width = 1000, height = 800) # Adjust dimensions

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
ggplot(df, aes(x = fit, y = transcribed_delta, color = data, shape = phase)) +
  geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.05, alpha = 0.5, size = 0.7) +
  geom_point(size = 3, alpha = 0.8) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "gray40", size = 0.8) +
  labs(
    title = "Predicted vs. Observed Transcription Delta",
    subtitle = "With 95% Confidence Intervals",
    x = "Predicted transcribed delta",
    y = "Observed transcribed delta",
    color = "Data Source",
    shape = "Phase"
  ) +
  scale_color_brewer(palette = "Set1") +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5, color = "gray50"),
    legend.position = "bottom",
    panel.grid.minor = element_blank(),
    panel.border = element_rect(color = "gray80", fill = NA, size = 0.5),
    plot.margin = margin(15, 15, 15, 15)
  ) +
  guides(
    color = guide_legend(override.aes = list(size = 3)),
    shape = guide_legend(override.aes = list(size = 3))
  )
ggsave("plots/predicted_vs_observed.png", width = 7, height = 6, dpi = 300)


# Generate marginal effects - using ggpredict() instead of ggemmeans() for GAM
eff_expert <- ggpredict(model, terms = "expert")
eff_data <- ggpredict(model, terms = "data")
eff_phase <- ggpredict(model, terms = "phase")

# Custom theme for consistent styling
effect_theme <- function() {
  theme_minimal(base_size = 14) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5, size = 16),
      axis.title = element_text(size = 14),
      axis.text = element_text(size = 12),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_line(color = "gray90"),
      panel.grid.major.x = element_blank(),
      panel.border = element_rect(color = "gray80", fill = NA, size = 0.5),
      plot.margin = margin(10, 15, 10, 15),
      legend.position = "none"
    )
}

# Create expert plot
p_expert <- ggplot(eff_expert, aes(x = x, y = predicted)) +
  geom_point(size = 4, color = "#0072B2", fill = "white", shape = 21, stroke = 1.5) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), 
                width = 0.1, color = "#0072B2", linewidth = 1) +
  labs(title = "Effect of Expertise Level",
       x = "Expertise Level",
       y = "Predicted Δ Transcription") +
  effect_theme()

  # Create data plot
p_data <- ggplot(eff_data, aes(x = x, y = predicted)) +
  geom_point(size = 4, color = "#E69F00", fill = "white", shape = 22, stroke = 1.5) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), 
                width = 0.1, color = "#E69F00", linewidth = 1) +
  labs(title = "Effect of Data Type",
       x = "Data Type",
       y = "Predicted Δ Transcription") +
  effect_theme()

  # Create phase plot
p_phase <- ggplot(eff_phase, aes(x = x, y = predicted)) +
  geom_point(size = 4, color = "#009E73", fill = "white", shape = 24, stroke = 1.5) +
  geom_errorbar(aes(ymin = conf.low, ymax = conf.high), 
                width = 0.1, color = "#009E73", linewidth = 1) +
  labs(title = "Effect of Experimental Phase",
       x = "Phase",
       y = "Predicted Δ Transcription") +
  effect_theme()

  # Combine plots
combined_plots <- (p_expert | p_data | p_phase) +
  plot_annotation(title = "Marginal Effects of Predictors on Transcription Accuracy",
                 theme = theme(plot.title = element_text(face = "bold", size = 18, hjust = 0.5)))

# Display and save
print(combined_plots)
ggsave("plots/marginal_effects.png", combined_plots, 
       width = 14, height = 5, dpi = 300, bg = "white")
